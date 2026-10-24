import logging
import re
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("mindsync.ocr")

_ocr_engine = None

def get_ocr_engine():
    """
    Lazy-load the PaddleOCR engine on first request so server startup is instant.
    Uses PP-OCR Mobile models optimized for CPU inference on Windows without requiring GPU.
    """
    global _ocr_engine
    if _ocr_engine is None:
        try:
            # Bypass Windows CPU OneDNN instruction bug in PaddlePaddle 3.x by enforcing run_mode='paddle'
            try:
                import paddlex.inference.models.runners.paddle_static.runner as runner_mod
                orig_create = runner_mod.PaddleStaticRunner._create
                def patched_create(self):
                    self._config['run_mode'] = 'paddle'
                    return orig_create(self)
                runner_mod.PaddleStaticRunner._create = patched_create
            except Exception:
                pass

            from paddleocr import PaddleOCR
            _ocr_engine = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='en'
            )
            logger.info("PaddleOCR CPU engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise e
    return _ocr_engine


def clean_ocr_line(line: str) -> str:
    """
    Clean individual OCR line while preserving intentional punctuation, numbers, and currency.
    Removes non-printable control chars and excessive whitespace.
    """
    if not line:
        return ""
    # Replace non-breaking spaces and tabs with standard space
    line = re.sub(r'[\u00a0\u2000-\u200b\t]+', ' ', line)
    # Strip non-printable ASCII control characters
    line = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', line)
    return line.strip()


def structure_ocr_lines(raw_lines: List[str], confidences: List[float]) -> Dict[str, Any]:
    """
    Filter noise, preserve line breaks and paragraph structure,
    and detect if the image has genuine readable text.
    """
    cleaned_lines = []
    valid_confidences = []

    for raw, conf in zip(raw_lines, confidences):
        cleaned = clean_ocr_line(raw)
        if not cleaned:
            continue

        # Filter out stray low-confidence non-alphanumeric noise (e.g. random `~`, `^`, `|` with score < 0.4)
        has_alpha_or_digit = bool(re.search(r'[a-zA-Z0-9$€£₹¥%#@]', cleaned))
        if not has_alpha_or_digit and conf < 0.40:
            continue

        cleaned_lines.append(cleaned)
        valid_confidences.append(conf)

    # Check for readable content: at least 1 word or substantial alphanumeric sequence
    joined_text = "\n".join(cleaned_lines)
    words = [w for w in re.findall(r'[a-zA-Z0-9]{2,}', joined_text)]
    has_readable_text = len(words) > 0 and len(joined_text.strip()) >= 2

    avg_conf = float(sum(valid_confidences) / len(valid_confidences)) if valid_confidences else 0.0
    conf_percentage = round(avg_conf * 100, 1)

    return {
        "has_readable_text": has_readable_text,
        "cleaned_text": joined_text if has_readable_text else "",
        "raw_text": "\n".join(raw_lines),
        "lines": cleaned_lines if has_readable_text else [],
        "confidence": conf_percentage if has_readable_text else 0.0,
        "line_count": len(cleaned_lines) if has_readable_text else 0,
        "word_count": len(words) if has_readable_text else 0,
        "char_count": len(joined_text) if has_readable_text else 0,
        "status": "completed" if has_readable_text else "completed_no_text"
    }


def extract_ocr_details_from_image_bytes(image_bytes: bytes) -> dict:
    """
    Extracts legible text, per-line segments, confidence, and statistics from image bytes.
    Preserves line breaks, cleans OCR noise, and handles images with no readable text.
    """
    default_res = {
        "has_readable_text": False,
        "full_text": "",
        "cleaned_text": "",
        "raw_text": "",
        "confidence": 0.0,
        "lines": [],
        "line_count": 0,
        "word_count": 0,
        "char_count": 0,
        "status": "completed_no_text"
    }
    if not image_bytes:
        return default_res

    try:
        import cv2
        import numpy as np

        # Decode raw bytes into an OpenCV BGR numpy array without touching disk
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_raw = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

        img = None
        if img_raw is not None:
            if len(img_raw.shape) == 3 and img_raw.shape[2] == 4:
                # Composite transparent alpha channel onto solid white background
                alpha = img_raw[:, :, 3].astype(np.float32) / 255.0
                bgr = img_raw[:, :, :3].astype(np.float32)
                white = np.ones_like(bgr) * 255.0
                img = (bgr * alpha[:, :, np.newaxis] + white * (1.0 - alpha[:, :, np.newaxis])).astype(np.uint8)
            elif len(img_raw.shape) == 2:
                img = cv2.cvtColor(img_raw, cv2.COLOR_GRAY2BGR)
            else:
                img = img_raw[:, :, :3]

        if img is None:
            # Fallback to PIL with automatic EXIF orientation transposition
            try:
                from PIL import Image, ImageOps
                import io
                pil_img = Image.open(io.BytesIO(image_bytes))
                pil_img = ImageOps.exif_transpose(pil_img)
                pil_img = pil_img.convert("RGB")
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as pe:
                logger.warning(f"PIL fallback decoding failed: {pe}")

        if img is None:
            logger.warning("Could not decode image bytes into valid image array.")
            return default_res

        # Downscale ultra-high-resolution images to max 1600px for lightning-fast CPU inference (<1.5s)
        h, w = img.shape[:2]
        max_dim = 1600
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        ocr = get_ocr_engine()
        
        extracted_lines = []
        confidences = []

        # Predict using paddleocr engine
        try:
            results = list(ocr.predict(img))
            if results:
                for item in results:
                    if isinstance(item, dict):
                        texts = item.get("rec_texts", [])
                        scores = item.get("rec_scores", [])
                        for t, s in zip(texts, scores):
                            if t and str(t).strip():
                                extracted_lines.append(str(t).strip())
                                confidences.append(float(s))
        except Exception as pred_err:
            logger.warning(f"ocr.predict failed, trying ocr.ocr fallback: {pred_err}")
            try:
                res_ocr = ocr.ocr(img, cls=False)
                if res_ocr and isinstance(res_ocr, list):
                    for page in res_ocr:
                        if page:
                            for line in page:
                                if len(line) >= 2 and isinstance(line[1], (list, tuple)):
                                    txt, score = line[1][0], line[1][1]
                                    if txt and str(txt).strip():
                                        extracted_lines.append(str(txt).strip())
                                        confidences.append(float(score))
            except Exception as ocr_err:
                logger.error(f"Both OCR prediction methods failed: {ocr_err}")

        structured = structure_ocr_lines(extracted_lines, confidences)

        return {
            "has_readable_text": structured["has_readable_text"],
            "full_text": structured["cleaned_text"],
            "cleaned_text": structured["cleaned_text"],
            "raw_text": structured["raw_text"],
            "confidence": structured["confidence"],
            "lines": structured["lines"],
            "line_count": structured["line_count"],
            "word_count": structured["word_count"],
            "char_count": structured["char_count"],
            "status": structured["status"]
        }

    except Exception as e:
        logger.error(f"Error during PaddleOCR image extraction: {e}")
        return default_res


def extract_text_from_image_bytes(image_bytes: bytes) -> Tuple[str, float]:
    """
    Backwards-compatible wrapper returning (full_text, average_confidence_0_to_1).
    """
    details = extract_ocr_details_from_image_bytes(image_bytes)
    return details["full_text"], (details["confidence"] / 100.0)
