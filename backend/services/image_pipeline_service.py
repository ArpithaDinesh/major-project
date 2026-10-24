import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from bson.objectid import ObjectId

from database import get_db, to_object_id, normalize_category, serialize_doc
from services.storage_service import validate_image_file, save_image_file
from services.ocr_service import extract_ocr_details_from_image_bytes
from services.image_intelligence import analyze_image_intelligence

logger = logging.getLogger("mindsync.image_pipeline")

def execute_image_pipeline(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str],
    user_id: Optional[Any],
    category_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the 8-step image processing and intelligence pipeline:
    1. Receive an uploaded image.
    2. Save the original image using existing storage implementation.
    3. Create a `files` record with processing status ('processing').
    4. Extract text using PaddleOCR.
    5. Save the OCR output in `extracted_content`.
    6. Save image category, summary, keywords, and extracted entities in `metadata`.
    7. Update the processing status to completed or failed.
    8. Return a response containing the file ID and processing result.
    """
    db = get_db()
    
    # Resolve user ObjectId from authenticated session
    user_oid = to_object_id(user_id)
    if not user_oid and user_id:
        user_doc = db.users.find_one({"id": str(user_id)})
        if user_doc and user_doc.get("_id"):
            user_oid = user_doc["_id"]

    if not user_oid:
        raise ValueError("Authenticated user_id is strictly required to process and upload files.")

    # Step 1: Validate image format and file size (< 25 MB)
    is_valid, err_msg, meta = validate_image_file(filename, content_type, file_bytes)
    if not is_valid:
        raise ValueError(err_msg)

    # Step 2: Save original image using existing file-storage approach
    storage = save_image_file(file_bytes, filename)
    file_size_int = meta.get("sizeBytes") or len(file_bytes)
    resolved_mime = content_type or f"image/{meta.get('format', 'png').lower()}"

    # Step 3: Create a `files` record with processing status 'processing'
    file_oid = ObjectId()
    files_record = {
        "_id": file_oid,
        "user_id": user_oid,
        "original_filename": filename,
        "stored_file_path": storage["filePath"],
        "file_type": "image",
        "mime_type": resolved_mime,
        "file_size": file_size_int,
        "upload_date": datetime.utcnow(),
        "processing_status": "processing",
        "processing_error": None
    }
    db.files.insert_one(files_record)

    try:
        # Step 4: Extract text using PaddleOCR
        ocr_info = extract_ocr_details_from_image_bytes(file_bytes)

        # Step 5: Save the OCR output in `extracted_content`
        cleaned_text = ocr_info.get("cleaned_text") or ""
        raw_text = ocr_info.get("raw_text") or ""
        extracted_doc = {
            "_id": ObjectId(),
            "file_id": file_oid,
            "user_id": user_oid,
            "extracted_text": cleaned_text or raw_text,
            "extraction_method": "PaddleOCR",
            "language": os.getenv("PADDLE_OCR_LANG", "en"),
            "created_at": datetime.utcnow()
        }
        db.extracted_content.insert_one(extracted_doc)

        # Step 6: Save category, summary, keywords, and extracted entities in `metadata`
        intel = analyze_image_intelligence(file_bytes, filename, ocr_info, category_hint)
        
        # Normalize category to one of the 9 required categories
        category_norm = normalize_category(intel.get("category"))
        
        # Parse event date without inventing missing values
        event_date_dt = None
        norm_dates = intel.get("normalizedDates") or []
        if norm_dates:
            try:
                event_date_dt = datetime.fromisoformat(norm_dates[0]["normalized"])
            except Exception:
                event_date_dt = None
        elif intel.get("categoryData", {}).get("normalized_date"):
            try:
                event_date_dt = datetime.fromisoformat(intel["categoryData"]["normalized_date"])
            except Exception:
                event_date_dt = None

        location_val = (
            intel.get("categoryData", {}).get("venue")
            or intel.get("categoryData", {}).get("destination")
            or None
        )

        title_val = (
            intel.get("categoryData", {}).get("event_name")
            or intel.get("categoryData", {}).get("merchant")
            or intel.get("title")
            or os.path.splitext(filename)[0]
        )

        metadata_doc = {
            "_id": ObjectId(),
            "file_id": file_oid,
            "user_id": user_oid,
            "category": category_norm,
            "subtype": intel.get("subtype"),
            "confidence": intel.get("confidence"),
            "reason": intel.get("reason"),
            "needs_review": intel.get("needs_review", False),
            "title": title_val,
            "summary": intel.get("summary") or "",
            "entities": intel.get("category_fields") or intel.get("categoryData") or {},
            "category_fields": intel.get("category_fields") or intel.get("categoryData") or {},
            "extracted_entities": intel.get("extracted_entities") or [],
            "keywords": intel.get("keywords") or [],
            "event_date": event_date_dt,
            "location": location_val,
            "created_at": datetime.utcnow()
        }
        db.metadata.insert_one(metadata_doc)

        # Step 7: Update processing status to completed (or completed_no_text)
        final_status = "completed" if ocr_info.get("has_readable_text") else "completed_no_text"
        db.files.update_one(
            {"_id": file_oid},
            {"$set": {"processing_status": final_status, "processing_error": None}}
        )
        files_record["processing_status"] = final_status

        # Step 8: Return a response containing the file ID and processing result
        return {
            "success": True,
            "file_id": str(file_oid),
            "fileId": str(file_oid),
            "files": serialize_doc(files_record),
            "extracted_content": serialize_doc(extracted_doc),
            "metadata": serialize_doc(metadata_doc),
            # Validated JSON response fields (Requirement 3)
            "category": intel["category"],
            "subtype": intel.get("subtype"),
            "confidence": intel.get("confidence", 0.0),
            "reason": intel.get("reason", ""),
            "title": title_val,
            "summary": intel["summary"],
            "extracted_text": cleaned_text,
            "keywords": intel["keywords"],
            "extracted_entities": intel.get("extracted_entities", []),
            "category_fields": intel.get("category_fields", {}),
            "needs_review": intel.get("needs_review", False),
            # Backwards-compatible fields for frontend CaptureModal
            "filename": storage["fileName"],
            "originalFilename": filename,
            "fileUrl": storage["fileUrl"],
            "filePath": storage["filePath"],
            "fileSize": storage["fileSize"],
            "dimensions": {"width": meta["width"], "height": meta["height"]},
            "mimeType": resolved_mime,
            "hasReadableText": intel["hasReadableText"],
            "extractedText": cleaned_text,
            "cleanedText": cleaned_text,
            "rawText": raw_text,
            "lines": ocr_info.get("lines", []),
            "lineCount": intel["lineCount"],
            "wordCount": intel["wordCount"],
            "charCount": len(cleaned_text),
            "categoryNormalized": category_norm,
            "categoryLabel": intel["categoryLabel"],
            "categoryConfidence": intel["categoryConfidence"],
            "categoryData": intel["categoryData"],
            "semanticKeywords": intel["keywords"],
            "tags": [intel["categoryLabel"]] + (["OCR"] if intel["hasReadableText"] else ["VisualMedia"]),
            "normalizedDates": intel["normalizedDates"],
            "suggestedReminders": intel["suggestedReminders"],
            "isSensitive": intel["isSensitive"],
            "processingStatus": final_status
        }

    except Exception as exc:
        logger.error(f"Image processing failure: {exc}", exc_info=True)
        db.files.update_one(
            {"_id": file_oid},
            {"$set": {"processing_status": "failed", "processing_error": str(exc)}}
        )
        raise exc
