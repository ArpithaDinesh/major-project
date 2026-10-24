import os
import re
import json
import uuid
import logging
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("mindsync.image_intel")

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5, "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

ALL_CATEGORIES = [
    "bill",
    "receipt",
    "event_poster",
    "invitation",
    "ticket",
    "travel_booking",
    "identity_document",
    "certificate",
    "official_document",
    "handwritten_notes",
    "printed_notes",
    "screenshot",
    "menu_or_food_information",
    "product_or_label",
    "medical_document",
    "other",
    "unknown"
]

# ------------------------------------------------------------------------------
# 1. Date Extraction & Normalization
# ------------------------------------------------------------------------------
def normalize_date_string(date_str: str, time_str: Optional[str] = None) -> Optional[str]:
    """
    Parse natural date formats into ISO-8601 string (YYYY-MM-DDTHH:MM:SS).
    Handles ISO, Written (Month DD, YYYY / DD Month YYYY), and Slash formats.
    """
    if not date_str:
        return None

    clean_d = date_str.strip().strip(",.;")
    parsed_dt = None

    # Try ISO YYYY-MM-DD or YYYY/MM/DD
    m_iso = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', clean_d)
    if m_iso:
        y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        try:
            parsed_dt = datetime(y, m, d)
        except ValueError:
            pass

    # Try Month Name DD, YYYY
    if not parsed_dt:
        m_written = re.search(
            r'\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?(?:[,.]|\s)\s*(\d{4})\b|\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?\s*(\d{4})\b',
            clean_d,
            re.IGNORECASE
        )
        if m_written:
            month_name = (m_written.group(1) or m_written.group(4)).lower()
            day = int(m_written.group(2) or m_written.group(5))
            year = int(m_written.group(3) or m_written.group(6))
            if month_name in MONTH_MAP:
                try:
                    parsed_dt = datetime(year, MONTH_MAP[month_name], day)
                except ValueError:
                    pass

    # Try DD Month YYYY
    if not parsed_dt:
        m_written2 = re.search(
            r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([A-Za-z]{3,9})[,.]?\s+(\d{4})\b',
            clean_d,
            re.IGNORECASE
        )
        if m_written2:
            day = int(m_written2.group(1))
            month_name = m_written2.group(2).lower()
            year = int(m_written2.group(3))
            if month_name in MONTH_MAP:
                try:
                    parsed_dt = datetime(year, MONTH_MAP[month_name], day)
                except ValueError:
                    pass

    # Try DD/MM/YYYY or MM/DD/YYYY
    if not parsed_dt:
        m_slash = re.search(r'\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b', clean_d)
        if m_slash:
            p1, p2, yr = int(m_slash.group(1)), int(m_slash.group(2)), int(m_slash.group(3))
            if p1 > 12 >= p2:
                try:
                    parsed_dt = datetime(yr, p2, p1)
                except ValueError:
                    pass
            elif p2 > 12 >= p1:
                try:
                    parsed_dt = datetime(yr, p1, p2)
                except ValueError:
                    pass
            else:
                try:
                    parsed_dt = datetime(yr, p2, p1)  # Default DD/MM/YYYY
                except ValueError:
                    try:
                        parsed_dt = datetime(yr, p1, p2)
                    except ValueError:
                        pass

    if not parsed_dt:
        return None

    # Parse Time if provided
    hour, minute = 9, 0
    if time_str:
        m_time = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)?', time_str)
        if m_time:
            h = int(m_time.group(1))
            mi = int(m_time.group(2))
            meridiem = (m_time.group(4) or "").upper()
            if meridiem == "PM" and h < 12:
                h += 12
            elif meridiem == "AM" and h == 12:
                h = 0
            if 0 <= h <= 23 and 0 <= mi <= 59:
                hour, minute = h, mi

    parsed_dt = parsed_dt.replace(hour=hour, minute=minute, second=0)
    return parsed_dt.isoformat()


def extract_dates_and_times(text: str) -> List[Dict[str, Any]]:
    """Extract raw date occurrences and their normalized ISO counterparts."""
    detected = []
    if not text:
        return detected

    # 1. Written dates: "October 24, 2026", "24th October 2026", etc.
    written_matches = re.finditer(
        r'\b(?:(?:[A-Za-z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?(?:[,.]|\s)\s*\d{4})|(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?[A-Za-z]{3,9}[,.]?\s+\d{4}))\b',
        text,
        re.IGNORECASE
    )
    for m in written_matches:
        raw = m.group(0)
        norm = normalize_date_string(raw)
        if norm and not any(d["normalized"] == norm for d in detected):
            detected.append({"raw": raw, "normalized": norm})

    # 2. Numeric dates: YYYY-MM-DD or DD/MM/YYYY
    numeric_matches = re.finditer(r'\b(?:\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{4})\b', text)
    for m in numeric_matches:
        raw = m.group(0)
        norm = normalize_date_string(raw)
        if norm and not any(d["normalized"] == norm for d in detected):
            detected.append({"raw": raw, "normalized": norm})

    return detected


# ------------------------------------------------------------------------------
# 2. Ollama LLM Classifier Integration (Fallback-Safe)
# ------------------------------------------------------------------------------
import time

_ollama_last_checked = 0.0
_ollama_is_available = True

def _call_ollama_classifier(text: str, lines: List[str]) -> Optional[Dict[str, Any]]:
    """
    Attempt zero-cost classification using existing Ollama service if active.
    Uses short timeout (1.0s) and caches unreachable status to avoid stalling.
    """
    global _ollama_last_checked, _ollama_is_available
    current_time = time.time()
    if not _ollama_is_available and (current_time - _ollama_last_checked < 60.0):
        return None

    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3")
    url = f"{ollama_base.rstrip('/')}/api/generate"

    sample_snippet = " ".join(lines[:20]) if lines else text[:600]
    prompt = (
        f"You are a document classifier. Classify the following OCR text into exactly one of these categories:\n"
        f"bill, receipt, event_poster, invitation, ticket, travel_booking, identity_document, certificate, "
        f"official_document, handwritten_notes, printed_notes, screenshot, menu_or_food_information, "
        f"product_or_label, medical_document, other, unknown.\n\n"
        f"OCR Text:\n```\n{sample_snippet}\n```\n\n"
        f"Return ONLY valid JSON matching this schema:\n"
        f'{{"category": "<one_category>", "subtype": "<specific_subtype_or_null>", "confidence": <0.0-1.0>, "reason": "<short_reason>"}}'
    )

    req_payload = {
        "model": model_name,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 128}
    }

    try:
        data_bytes = json.dumps(req_payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=1.0) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            resp_body = resp_data.get("response", "")
            parsed = json.loads(resp_body)
            cat = str(parsed.get("category", "")).strip().lower().replace(" ", "_")
            if cat in ALL_CATEGORIES:
                conf = float(parsed.get("confidence", 0.85))
                _ollama_is_available = True
                return {
                    "category": cat,
                    "subtype": parsed.get("subtype"),
                    "confidence": max(0.5, min(0.99, conf)),
                    "reason": parsed.get("reason", f"Classified by LLM as {cat}")
                }
    except Exception as e:
        _ollama_is_available = False
        _ollama_last_checked = time.time()
        logger.debug(f"Ollama classification unavailable: {e}")
    return None


# ------------------------------------------------------------------------------
# 3. Deterministic NLP / Heuristic Classifier Engine
# ------------------------------------------------------------------------------
def classify_image_category_nlp(
    text: str,
    lines: List[str],
    has_readable_text: bool,
    ocr_conf: float = 0.0
) -> Tuple[str, Optional[str], float, str, bool]:
    """
    Score the image OCR text across 17 distinct categories with subtype detection.
    Returns:
        (category: str, subtype: Optional[str], confidence: float, reason: str, needs_review: bool)
    """
    if not has_readable_text or not text.strip():
        return (
            "unknown",
            "unreadable",
            0.15,
            "No decipherable text was detected in the image visual contents.",
            True
        )

    words = [w for w in re.findall(r'\b[A-Za-z0-9]+\b', text) if len(w) > 1]
    lower = text.lower()

    # Low-information or sparse check
    if len(words) < 3 and ocr_conf < 0.55:
        return (
            "unknown",
            "insufficient_text",
            0.30,
            "OCR text is too sparse (< 3 words) or degraded to classify with certainty.",
            True
        )

    scores: Dict[str, float] = {cat: 0.0 for cat in ALL_CATEGORIES}
    reasons: Dict[str, List[str]] = {cat: [] for cat in ALL_CATEGORIES}

    # --------------------------------------------------------------------------
    # 1. BILL Signals (Utility bills, electricity, water, telecom, etc.)
    # --------------------------------------------------------------------------
    bill_score = 0.0
    if re.search(r'\b(?:electricity bill|electric bill|power corp|discom|energy consumption)\b', lower):
        bill_score += 10.0
        reasons["bill"].append("Contains electricity provider and utility billing terminology")
    if re.search(r'\b(?:meter reading|previous reading|current reading|units consumed|kwh|connected load)\b', lower):
        bill_score += 9.0
        reasons["bill"].append("Contains meter readings and kWh energy metrics")
    if re.search(r'\b(?:water bill|water board|sewerage charge|water consumption|gallons consumed)\b', lower):
        bill_score += 9.0
        reasons["bill"].append("Contains water utility markers")
    if re.search(r'\b(?:bill amount|amount payable|payment due date|pay by date|disconnect date|late payment surcharge)\b', lower):
        bill_score += 7.0
        reasons["bill"].append("Contains bill payment due date and total amount payable")
    if re.search(r'\b(?:consumer no|account no|consumer id|subdivision|tariff rate)\b', lower):
        bill_score += 5.0
        reasons["bill"].append("Contains utility account / consumer identifier")
    if re.search(r'\b(?:broadband bill|internet service bill|monthly billing cycle|telecom bill)\b', lower):
        bill_score += 8.0
        reasons["bill"].append("Contains telecom / internet subscription invoice details")
    scores["bill"] = bill_score

    # --------------------------------------------------------------------------
    # 2. RECEIPT Signals (Point of sale, shopping, dining)
    # --------------------------------------------------------------------------
    rcpt_score = 0.0
    if re.search(r'\b(?:receipt|tax invoice|sales receipt|pos transaction|cash receipt)\b', lower):
        rcpt_score += 8.0
        reasons["receipt"].append("Explicit receipt/tax invoice heading")
    if re.search(r'\b(?:subtotal|change due|cash tend|balance due|cashier:|register #|terminal #)\b', lower):
        rcpt_score += 8.0
        reasons["receipt"].append("Point of sale transaction breakdown (subtotal, cashier, register)")
    if re.search(r'\b(?:visa|mastercard|amex|debit card|credit card|apple pay|google pay)\b', lower) and re.search(r'[$€£₹]\s*\d+[.,]\d{2}', text):
        rcpt_score += 6.0
        reasons["receipt"].append("Card payment terminal summary with charged amount")
    if re.search(r'\b(?:qty|items? sold|price|each|thank you for shopping|thank you for your business)\b', lower):
        rcpt_score += 5.0
        reasons["receipt"].append("Itemized merchant retail receipt footer")
    if re.search(r'\b(?:table #|waiter|server:|dine in|take out|gratuity|tip:)\b', lower):
        rcpt_score += 6.0
        reasons["receipt"].append("Restaurant dining slip markers")
    scores["receipt"] = rcpt_score

    # --------------------------------------------------------------------------
    # 3. EVENT POSTER Signals (College fests, workshops, conferences, concerts)
    # --------------------------------------------------------------------------
    event_score = 0.0
    if re.search(r'\b(?:annual conference|symposium|workshop|hackathon|annual fest|tech fest|cultural fest|webinar)\b', lower):
        event_score += 9.0
        reasons["event_poster"].append("Mentions organized event type (symposium, workshop, conference, fest)")
    if re.search(r'\b(?:doors open|venue:|held at|auditorium|amphitheater|campus|hall [a-z0-9]|keynote speaker|guest lecture)\b', lower):
        event_score += 7.0
        reasons["event_poster"].append("Event venue and keynote speaker details")
    if re.search(r'\b(?:register now|registration link|free admission|tickets available|entry fee|presents:|organized by|department of)\b', lower):
        event_score += 7.0
        reasons["event_poster"].append("Call-to-action for registration or hosting department")
    if re.search(r'\b(?:live in concert|featuring live|lineup|headline act|doors:)\b', lower):
        event_score += 8.0
        reasons["event_poster"].append("Live performance or concert announcement")
    scores["event_poster"] = event_score

    # --------------------------------------------------------------------------
    # 4. INVITATION Signals (Weddings, birthdays, anniversaries, parties)
    # --------------------------------------------------------------------------
    inv_score = 0.0
    if re.search(r'\b(?:cordially invite you|request the honour of your presence|request the pleasure of your company)\b', lower):
        inv_score += 10.0
        reasons["invitation"].append("Formal ceremonial invitation phrasing")
    if re.search(r'\b(?:wedding ceremony|holy matrimony|marriage of|nuptials|reception to follow|bride and groom|grace the auspicious occasion)\b', lower):
        inv_score += 9.0
        reasons["invitation"].append("Wedding ceremonial announcement")
    if re.search(r'\b(?:birthday party|turns \d+|turning \d+|celebrate with us|save the date|join us in celebrating)\b', lower):
        inv_score += 8.0
        reasons["invitation"].append("Celebratory birthday or social gathering invitation")
    if re.search(r'\b(?:rsvp|r\.s\.v\.p|best compliments from|with love and best wishes)\b', lower):
        inv_score += 5.0
        reasons["invitation"].append("RSVP and host felicitations")
    scores["invitation"] = inv_score

    # --------------------------------------------------------------------------
    # 5. TICKET Signals (Train, flight, movie, boarding pass)
    # --------------------------------------------------------------------------
    ticket_score = 0.0
    if re.search(r'\b(?:boarding pass|airline ticket|e-ticket|transit pass)\b', lower):
        ticket_score += 10.0
        reasons["ticket"].append("Flight boarding pass / e-ticket designation")
    if re.search(r'\b(?:flight no|flight:|gate:|gate\s+\d+|seat:|seat\s+[0-9]+[a-z]?|pnr[:\s]|pnr\b)\b', lower):
        ticket_score += 8.0
        reasons["ticket"].append("Flight credential indicators (Flight No, Gate, Seat, PNR)")
    if re.search(r'\b(?:train ticket|train no|coach:|berth:|irctc|amtrak|sleeper class|class: 3a|railway)\b', lower):
        ticket_score += 10.0
        reasons["ticket"].append("Rail passenger transit ticket with train/berth allocation")
    if re.search(r'\b(?:cinema ticket|movie ticket|theatre ticket|screen \d+|audi \d+|showtime:)\b', lower):
        ticket_score += 8.0
        reasons["ticket"].append("Cinema / theater admission pass")
    if re.search(r'\b(?:departure|arrival|boarding time|passenger name|origin|destination)\b', lower):
        ticket_score += 6.0
        reasons["ticket"].append("Transit routing and scheduled departure details")
    scores["ticket"] = ticket_score

    # --------------------------------------------------------------------------
    # 6. TRAVEL BOOKING Signals (Hotels, stays, itineraries)
    # --------------------------------------------------------------------------
    tb_score = 0.0
    if re.search(r'\b(?:hotel reservation|reservation confirmation|booking confirmation|booking\.com|airbnb|resort)\b', lower):
        tb_score += 9.0
        reasons["travel_booking"].append("Hotel or property lodging reservation confirmation")
    if re.search(r'\b(?:check-in:|check-out:|check in date|check out date|nights stay|room type|deluxe room)\b', lower):
        tb_score += 9.0
        reasons["travel_booking"].append("Accommodation check-in/check-out itinerary schedule")
    if re.search(r'\b(?:booking reference|confirmation code|host details|itinerary overview)\b', lower):
        tb_score += 5.0
        reasons["travel_booking"].append("Travel booking reference code")
    scores["travel_booking"] = tb_score

    # --------------------------------------------------------------------------
    # 7. IDENTITY DOCUMENT Signals (Passports, driver licenses, national IDs)
    # --------------------------------------------------------------------------
    id_score = 0.0
    if re.search(r'\b(?:passport|republic of|kingdom of|nationality|issuing country)\b', lower):
        id_score += 10.0
        reasons["identity_document"].append("Official sovereign passport markers")
    if re.search(r'\b(?:driving licence|driver\'s license|driver license|motor vehicle dept|dl no|class c)\b', lower):
        id_score += 10.0
        reasons["identity_document"].append("Driver licensing authority markers")
    if re.search(r'\b(?:national identity card|national id|aadhaar|unique identification authority|pan card|voter id)\b', lower):
        id_score += 10.0
        reasons["identity_document"].append("National identity card or civic identification authority")
    if re.search(r'\b(?:date of birth|dob|sex:|gender:|place of birth|expiry date|valid until)\b', lower):
        id_score += 5.0
        reasons["identity_document"].append("Civil registration demographic fields")
    scores["identity_document"] = id_score

    # --------------------------------------------------------------------------
    # 8. CERTIFICATE Signals (Course completion, diplomas, awards)
    # --------------------------------------------------------------------------
    cert_score = 0.0
    if re.search(r'\b(?:certificate of completion|certificate of achievement|certificate of participation|certifies that)\b', lower):
        cert_score += 10.0
        reasons["certificate"].append("Explicit certificate credential designation")
    if re.search(r'\b(?:has successfully completed|awarded to|in recognition of|is hereby conferred)\b', lower):
        cert_score += 9.0
        reasons["certificate"].append("Formal credential conferment phrasing")
    if re.search(r'\b(?:degree of|bachelor of|master of|diploma in|distinction|dean of|head of institute)\b', lower):
        cert_score += 8.0
        reasons["certificate"].append("Academic honor / degree conferral")
    scores["certificate"] = cert_score

    # --------------------------------------------------------------------------
    # 9. OFFICIAL DOCUMENT Signals (Agreements, notices, contracts, legal, bank statement)
    # --------------------------------------------------------------------------
    off_score = 0.0
    if re.search(r'\b(?:agreement|memorandum of understanding|party of the first part|in witness whereof|hereby agreed)\b', lower):
        off_score += 9.0
        reasons["official_document"].append("Legal agreement / contract covenant structure")
    if re.search(r'\b(?:official notice|public notice|circular no|statutory notification|government gazette|office order)\b', lower):
        off_score += 9.0
        reasons["official_document"].append("Government administrative notice or circular")
    if re.search(r'\b(?:account statement|bank statement|ledger balance|statement of account|clearing branch)\b', lower):
        off_score += 8.0
        reasons["official_document"].append("Formal banking account statement")
    if re.search(r'\b(?:ref no:|reference number|case no|authorized signatory|seal and signature)\b', lower):
        off_score += 4.0
        reasons["official_document"].append("Formal document tracking reference & seal")
    scores["official_document"] = off_score

    # --------------------------------------------------------------------------
    # 10. HANDWRITTEN NOTES Signals
    # --------------------------------------------------------------------------
    hn_score = 0.0
    if re.search(r'\b(?:handwritten|scribble|meeting scribbles|rough notes|lecture scratchpad)\b', lower):
        hn_score += 8.0
        reasons["handwritten_notes"].append("Direct handwritten notes indicator")
    if any(l.strip().startswith("- [ ]") or l.strip().startswith("todo:") for l in lines):
        hn_score += 4.0
        reasons["handwritten_notes"].append("Informal task checklist structure")
    scores["handwritten_notes"] = hn_score

    # --------------------------------------------------------------------------
    # 11. PRINTED NOTES Signals (Study guides, cheat sheets, textbook summary)
    # --------------------------------------------------------------------------
    pn_score = 0.0
    if re.search(r'\b(?:study guide|cheat sheet|summary sheet|lecture notes|chapter summary|key takeaways|key concepts)\b', lower):
        pn_score += 8.0
        reasons["printed_notes"].append("Curated study guide or conceptual notes heading")
    if re.search(r'\b(?:definition:|theorem \d+|formula sheet|syllabus overview|unit \d+:|module \d+:)\b', lower):
        pn_score += 7.0
        reasons["printed_notes"].append("Educational syllabus / lecture module outlines")
    scores["printed_notes"] = pn_score

    # --------------------------------------------------------------------------
    # 12. SCREENSHOT Signals (Digital UI, phone/computer apps)
    # --------------------------------------------------------------------------
    sc_score = 0.0
    if re.search(r'\b(?:battery|wifi|lte|5g|am|pm)\b', lower) and len(lines) > 0 and re.search(r'\b(?:\d{1,2}:\d{2})\b', lines[0]):
        sc_score += 7.0
        reasons["screenshot"].append("Device status bar clock / battery indicators detected")
    if re.search(r'\b(?:settings|whatsapp|slack|telegram|instagram|notifications|system preferences|app store|google play)\b', lower):
        sc_score += 6.0
        reasons["screenshot"].append("Known software application UI chrome")
    if re.search(r'\b(?:http://|https://|www\.|\.com/|search or type url)\b', lower):
        sc_score += 6.0
        reasons["screenshot"].append("Web browser address bar / URL element")
    scores["screenshot"] = sc_score

    # --------------------------------------------------------------------------
    # 13. MENU OR FOOD INFORMATION Signals (Restaurant menus, nutrition facts)
    # --------------------------------------------------------------------------
    food_score = 0.0
    if re.search(r'\b(?:starters|appetizers|main course|desserts|beverages|drinks menu|chef\'s special|combos|entrees)\b', lower):
        food_score += 9.0
        reasons["menu_or_food_information"].append("Structured restaurant dining menu sections")
    if re.search(r'\b(?:nutrition facts|serving size|calories|total fat|sodium|dietary fiber|total carbohydrate|protein)\b', lower):
        food_score += 10.0
        reasons["menu_or_food_information"].append("Standard regulatory nutrition facts panel")
    if re.search(r'\b(?:pizza|burger|pasta|tacos|salad|sandwich|espresso|cappuccino|cocktail)\b', lower):
        food_score += 4.0
        reasons["menu_or_food_information"].append("Dishes and culinary menu items")
    scores["menu_or_food_information"] = food_score

    # --------------------------------------------------------------------------
    # 14. PRODUCT OR LABEL Signals (Packaging, barcodes, model spec sheets)
    # --------------------------------------------------------------------------
    prod_score = 0.0
    if re.search(r'\b(?:net wt|net weight|model no|serial no|batch no|mfg date|best before|use by date|barcode)\b', lower):
        prod_score += 8.0
        reasons["product_or_label"].append("Consumer product manufacturing batch and specification label")
    if re.search(r'\b(?:handling instructions|keep away from heat|voltage:|operating temperature|dimensions:)\b', lower):
        prod_score += 6.0
        reasons["product_or_label"].append("Product packaging technical specifications")
    scores["product_or_label"] = prod_score

    # --------------------------------------------------------------------------
    # 15. MEDICAL DOCUMENT Signals (Prescriptions, lab reports, doctor records)
    # --------------------------------------------------------------------------
    med_score = 0.0
    if re.search(r'\b(?:hospital|clinic|dr\.|doctor|patient name|rx\b|prescription|diagnostic laboratory)\b', lower):
        med_score += 9.0
        reasons["medical_document"].append("Clinical healthcare facility and medical consultation markers")
    if re.search(r'\b(?:dosage|tablet|capsule|syrup|take \d+ daily|after meals|opd|department of pathology)\b', lower):
        med_score += 8.0
        reasons["medical_document"].append("Medical prescription dosage / pharmacy dispensation")
    if re.search(r'\b(?:lab report|blood test|hemoglobin|reference range|clinical pathology|specimen:)\b', lower):
        med_score += 9.0
        reasons["medical_document"].append("Laboratory diagnostic test report")
    scores["medical_document"] = med_score

    # --------------------------------------------------------------------------
    # Disambiguation & Bias Corrections
    # --------------------------------------------------------------------------
    # A utility bill vs point of sale receipt
    if scores["bill"] >= 6.0 and scores["receipt"] >= 4.0:
        if any("kwh" in lower or "meter reading" in lower or "water board" in lower or "discom" in lower for _ in [1]):
            scores["bill"] += 5.0
            scores["receipt"] -= 2.0

    # Sort categories by score
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_cats[0]

    # Baseline threshold checks
    if best_score < 4.0:
        # Check if notes or generic document
        if len(lines) >= 4 and len(words) >= 15:
            return (
                "other",
                "miscellaneous",
                0.60,
                "Document contains readable textual content but does not strictly match specific domain categories.",
                True
            )
        return (
            "unknown",
            "insufficient_evidence",
            0.40,
            "Document content lacked strong category-specific keywords or structural indicators.",
            True
        )

    # Calculate calibrated confidence
    conf = min(0.98, max(0.60, round(0.55 + (best_score / 25.0) * 0.40, 2)))
    cat_reasons = reasons.get(best_cat, [])
    reason_str = "; ".join(cat_reasons) if cat_reasons else f"High correlation with {best_cat.replace('_', ' ')} indicators."
    needs_rev = conf < 0.70

    # Determine Granular Subtype
    subtype = _determine_subtype(best_cat, lower, lines)

    return best_cat, subtype, conf, reason_str, needs_rev


def _determine_subtype(category: str, lower: str, lines: List[str]) -> Optional[str]:
    """Determine a granular subtype for a primary category."""
    if category == "bill":
        if re.search(r'\b(?:kwh|electric|power|discom|energy)\b', lower):
            return "electricity_bill"
        if re.search(r'\b(?:water|sewerage|gallons)\b', lower):
            return "water_bill"
        if re.search(r'\b(?:natural gas|gas bill|cylinder|lpg)\b', lower):
            return "gas_bill"
        if re.search(r'\b(?:broadband|fiber|internet|wi-fi)\b', lower):
            return "internet_bill"
        if re.search(r'\b(?:telecom|mobile bill|phone bill|cellular)\b', lower):
            return "phone_bill"
        if re.search(r'\b(?:credit card|minimum due|credit limit)\b', lower):
            return "credit_card_bill"
        return "utility_bill"

    if category == "receipt":
        if re.search(r'\b(?:table|waiter|server|dine|restaurant|cafe|tip)\b', lower):
            return "restaurant_receipt"
        if re.search(r'\b(?:grocery|supermarket|produce|market|walmart|target)\b', lower):
            return "grocery_receipt"
        if re.search(r'\b(?:fuel|gas station|petrol|diesel|pump)\b', lower):
            return "fuel_receipt"
        return "shopping_receipt"

    if category == "event_poster":
        if re.search(r'\b(?:college|university|campus|department|fest|symposium)\b', lower):
            return "college_poster"
        if re.search(r'\b(?:workshop|hands-on|bootcamp|training)\b', lower):
            return "workshop_poster"
        if re.search(r'\b(?:conference|summit|keynote)\b', lower):
            return "conference_poster"
        if re.search(r'\b(?:hackathon|coding|tracks|devpost)\b', lower):
            return "hackathon_poster"
        if re.search(r'\b(?:concert|band|music|live|dj|performance)\b', lower):
            return "concert_poster"
        return "event_poster"

    if category == "invitation":
        if re.search(r'\b(?:wedding|marriage|matrimony|bride|groom|nuptials)\b', lower):
            return "wedding_invitation"
        if re.search(r'\b(?:birthday|turns \d+|turning \d+)\b', lower):
            return "birthday_invitation"
        if re.search(r'\b(?:anniversary|years of togetherness)\b', lower):
            return "anniversary_invitation"
        return "party_invitation"

    if category == "ticket":
        if re.search(r'\b(?:boarding pass|flight|airline|airport|gate)\b', lower):
            return "flight_ticket"
        if re.search(r'\b(?:train|irctc|amtrak|railway|berth|coach)\b', lower):
            return "train_ticket"
        if re.search(r'\b(?:cinema|movie|theatre|screen|imax)\b', lower):
            return "movie_ticket"
        if re.search(r'\b(?:bus|volvo|coach)\b', lower):
            return "bus_ticket"
        return "transit_ticket"

    if category == "travel_booking":
        if re.search(r'\b(?:hotel|resort|room|suite)\b', lower):
            return "hotel_reservation"
        if re.search(r'\b(?:flight confirmation|airline booking)\b', lower):
            return "flight_booking"
        return "hotel_reservation"

    if category == "identity_document":
        if "passport" in lower:
            return "passport"
        if "driver" in lower or "driving" in lower:
            return "drivers_license"
        if "aadhaar" in lower:
            return "aadhaar_card"
        if "pan" in lower and "card" in lower:
            return "pan_card"
        if "voter" in lower:
            return "voter_id"
        return "national_id"

    if category == "certificate":
        if re.search(r'\b(?:course|training|specialization|bootcamp)\b', lower):
            return "course_certificate"
        if re.search(r'\b(?:degree|diploma|bachelor|master|university)\b', lower):
            return "degree_certificate"
        if re.search(r'\b(?:achievement|excellence|merit)\b', lower):
            return "achievement_certificate"
        return "completion_certificate"

    if category == "official_document":
        if re.search(r'\b(?:agreement|contract|memorandum|clause)\b', lower):
            return "contract"
        if re.search(r'\b(?:bank statement|account statement|ledger)\b', lower):
            return "bank_statement"
        if re.search(r'\b(?:gazette|circular|public notice|order)\b', lower):
            return "government_notice"
        return "official_document"

    if category == "handwritten_notes":
        if "meeting" in lower:
            return "meeting_notes"
        return "study_notes"

    if category == "printed_notes":
        if re.search(r'\b(?:cheat sheet|quick reference)\b', lower):
            return "cheat_sheet"
        if re.search(r'\b(?:summary sheet|chapter summary)\b', lower):
            return "summary_sheet"
        return "lecture_notes"

    if category == "screenshot":
        if any(w in lower for w in ["whatsapp", "slack", "messages", "chat"]):
            return "chat_screenshot"
        if any(w in lower for w in ["battery", "wifi", "lte", "5g"]):
            return "mobile_screenshot"
        return "desktop_screenshot"

    if category == "menu_or_food_information":
        if "nutrition" in lower:
            return "nutrition_label"
        return "restaurant_menu"

    if category == "product_or_label":
        if "barcode" in lower:
            return "barcode_label"
        return "product_label"

    if category == "medical_document":
        if "prescription" in lower or "rx" in lower:
            return "prescription"
        if "lab" in lower or "test" in lower or "hemoglobin" in lower:
            return "lab_report"
        return "medical_record"

    return None


def classify_image_category(
    text: str,
    lines: List[str],
    has_readable_text: bool,
    ocr_conf: float = 0.0
) -> Tuple[str, Optional[str], float, str, bool]:
    """
    Combined classification: tries LLM if active, otherwise falls back smoothly to NLP engine.
    """
    if not has_readable_text or not text.strip():
        return "unknown", "unreadable", 0.10, "No readable text detected.", True

    # Check local LLM (Ollama) with 2s timeout
    llm_res = _call_ollama_classifier(text, lines)
    if llm_res and llm_res.get("category") in ALL_CATEGORIES:
        cat = llm_res["category"]
        conf = llm_res["confidence"]
        sub = llm_res.get("subtype") or _determine_subtype(cat, text.lower(), lines)
        needs_rev = conf < 0.70
        return cat, sub, conf, llm_res["reason"], needs_rev

    # Deterministic NLP Engine
    return classify_image_category_nlp(text, lines, has_readable_text, ocr_conf)


# ------------------------------------------------------------------------------
# 4. Comprehensive Category-Specific Field Extraction
# ------------------------------------------------------------------------------
def extract_category_fields(
    category: str,
    subtype: Optional[str],
    text: str,
    lines: List[str]
) -> Dict[str, Any]:
    """
    Extract structured, category-specific fields without hallucinating values.
    Returns clean dictionary with detected fields or explicit None for absent values.
    """
    lower = text.lower()
    data: Dict[str, Any] = {}

    # 1. Bills & Receipts
    if category in ["bill", "receipt"]:
        # Vendor / Provider / Merchant
        vendor = None
        for l in lines[:4]:
            clean_l = l.strip()
            if len(clean_l) >= 2 and not any(k in clean_l.lower() for k in ["receipt", "invoice", "bill to", "tax invoice", "tel:", "welcome"]):
                vendor = clean_l
                break
        data["vendor"] = vendor
        data["bill_type"] = subtype.replace("_", " ").title() if subtype else ("Utility Bill" if category == "bill" else "Shopping Receipt")

        # Bill / Invoice Number
        bill_no = None
        m_bno = re.search(r'\b(?:bill no|invoice no|inv no|bill #|invoice #|order #)[:\s]*([A-Z0-9-]{3,16})\b', text, re.IGNORECASE)
        if m_bno:
            bill_no = m_bno.group(1).strip()
        data["bill_number"] = bill_no

        # Amount & Currency
        amount = None
        currency = None
        m_amt = re.findall(r'\b(?:grand total|total amount|amount payable|balance due|amount due|total)\b[:\s]*([$€£₹]?\s*\d+[.,]\d{2})', text, re.IGNORECASE)
        if m_amt:
            # Prefer the last explicit total occurrence (to skip intermediate subtotals)
            amount = m_amt[-1].strip()
        else:
            amounts = re.findall(r'[$€£₹]\s*\d+[.,]\d{2}', text)
            if amounts:
                amount = amounts[-1].strip()

        if amount:
            m_curr = re.match(r'([$€£₹])', amount)
            if m_curr:
                currency = m_curr.group(1)
            elif "usd" in lower: currency = "USD"
            elif "eur" in lower: currency = "EUR"
            elif "inr" in lower or "rs" in lower: currency = "INR"
            elif "gbp" in lower: currency = "GBP"
        data["amount"] = amount
        data["currency"] = currency

        # Dates
        dates = extract_dates_and_times(text)
        issue_date = None
        due_date = None

        m_due = re.search(r'(?:due date|payment due|pay by|due on)[:\s]*([^\n]+)', text, re.IGNORECASE)
        if m_due:
            due_str = m_due.group(1).strip()
            due_dates = extract_dates_and_times(due_str)
            if due_dates:
                due_date = due_dates[0]["raw"]
                data["normalized_due_date"] = due_dates[0]["normalized"]

        if dates:
            issue_date = dates[0]["raw"]
            data["normalized_issue_date"] = dates[0]["normalized"]
            if not due_date and len(dates) > 1 and category == "bill":
                due_date = dates[-1]["raw"]
                data["normalized_due_date"] = dates[-1]["normalized"]

        data["issue_date"] = issue_date
        data["due_date"] = due_date
        data["date"] = issue_date
        data["normalized_date"] = data.get("normalized_due_date") or data.get("normalized_issue_date")

        # Payment Status
        payment_status = "unspecified"
        if "paid in full" in lower or "cash tend" in lower or "change due" in lower or "status: paid" in lower:
            payment_status = "paid"
        elif due_date or "amount payable" in lower or "pay by" in lower:
            payment_status = "due"
        data["payment_status"] = payment_status

        # Merchant compatibility alias
        data["merchant"] = vendor

    # 2. Event Poster
    elif category == "event_poster":
        event_name = None
        for l in lines[:4]:
            if len(l) > 3 and not any(k in l.lower() for k in ["presents", "presents:", "hosted by", "venue", "date:", "registration"]):
                event_name = l.strip()
                break
        data["event_name"] = event_name

        organizer = None
        m_org = re.search(r'(?:hosted by|presented by|organized by|department of)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_org:
            organizer = m_org.group(1).strip()
        data["organizer"] = organizer

        dates = extract_dates_and_times(text)
        data["event_date"] = dates[0]["raw"] if dates else None
        data["date"] = data["event_date"]

        m_time = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\b', text)
        data["start_time"] = m_time.group(1) if m_time else None
        data["time"] = data["start_time"]

        if dates:
            if data["start_time"]:
                norm_with_time = normalize_date_string(dates[0]["raw"], data["start_time"])
                data["normalized_date"] = norm_with_time or dates[0]["normalized"]
            else:
                data["normalized_date"] = dates[0]["normalized"]
        else:
            data["normalized_date"] = None

        venue = None
        m_venue = re.search(r'(?:venue|location|at|held at)[:\s]+([^\n,]+)', text, re.IGNORECASE)
        if m_venue:
            venue = m_venue.group(1).strip()
        else:
            for l in lines:
                if any(w in l.lower() for w in ["auditorium", "center", "centre", "hall", "stadium", "theater", "campus", "room"]):
                    venue = l.strip()
                    break
        data["venue"] = venue

        reg_deadline = None
        m_reg = re.search(r'(?:registration deadline|register by|last date)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_reg:
            reg_deadline = m_reg.group(1).strip()
        data["registration_deadline"] = reg_deadline

        contact = None
        m_contact = re.search(r'(?:contact|email|phone|website)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_contact:
            contact = m_contact.group(1).strip()
        data["contact_details"] = contact

    # 3. Invitation
    elif category == "invitation":
        occasion = "Celebration"
        if "wedding" in lower or "matrimony" in lower or "marriage" in lower:
            occasion = "Wedding"
        elif "birthday" in lower or "turns " in lower or "turning " in lower or subtype == "birthday_invitation":
            occasion = "Birthday"
        elif "anniversary" in lower:
            occasion = "Anniversary"
        data["occasion"] = occasion

        # Host Names
        host = None
        m_host = re.search(r'(?:together with their families|cordially invited by|hosted by|request the pleasure of your company)[:\s]*([^\n]+)', text, re.IGNORECASE)
        if m_host:
            host = m_host.group(1).strip()
        data["host_names"] = host

        # Invited Person
        invited_person = None
        m_guest = re.search(r'(?:dear|to:|inviting)[:\s]+([A-Za-z\s.]+)', text, re.IGNORECASE)
        if m_guest:
            invited_person = m_guest.group(1).strip().split('\n')[0]
        data["invited_person"] = invited_person

        dates = extract_dates_and_times(text)
        data["date"] = dates[0]["raw"] if dates else None
        data["normalized_date"] = dates[0]["normalized"] if dates else None

        m_time = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\b', text)
        data["time"] = m_time.group(1) if m_time else None

        venue = None
        m_venue = re.search(r'(?:venue|at|held at|place)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_venue:
            venue = m_venue.group(1).strip()
        data["venue"] = venue

        rsvp = None
        m_rsvp = re.search(r'(?:rsvp|r\.s\.v\.p)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_rsvp:
            rsvp = m_rsvp.group(1).strip()
        data["rsvp_details"] = rsvp

    # 4. Ticket
    elif category == "ticket":
        ticket_type = subtype.replace("_", " ").title() if subtype else "Transit Ticket"
        data["ticket_type"] = ticket_type

        # Carrier
        carrier = None
        for l in lines[:4]:
            if any(w in l.lower() for w in ["airline", "airways", "express", "rail", "amtrak", "irctc", "transit", "air", "cinema", "theatre"]):
                carrier = l.strip()
                break
        data["carrier"] = carrier

        # PNR / Booking Reference
        pnr = None
        m_pnr = re.search(r'\b(?:pnr|booking ref|e-ticket|ticket no|booking code|pnr no)[:\s]*([A-Z0-9-]{5,12})\b', text, re.IGNORECASE)
        if m_pnr:
            pnr = m_pnr.group(1).strip()
        data["booking_reference"] = pnr
        data["ticket_number"] = pnr

        # Journey or Event Name
        journey_name = None
        m_journey = re.search(r'(?:flight no|train no|movie|event)[:\s]*([A-Z0-9\s-]+)', text, re.IGNORECASE)
        if m_journey:
            journey_name = m_journey.group(1).strip().split('\n')[0]
        data["journey_or_event_name"] = journey_name

        # Route / Origin / Destination
        origin, destination = None, None
        m_route = re.search(r'([A-Z]{3})\s*(?:to|->|→|-)\s*([A-Z]{3})', text)
        if m_route:
            origin, destination = m_route.group(1), m_route.group(2)
        else:
            m_from = re.search(r'(?:from|departs)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
            m_to = re.search(r'(?:to|arrives)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
            if m_from: origin = m_from.group(1).strip().split('\n')[0]
            if m_to: destination = m_to.group(1).strip().split('\n')[0]
        data["departure_details"] = origin
        data["arrival_details"] = destination
        data["origin"] = origin
        data["destination"] = destination

        # Seat & Travel Date
        m_seat = re.search(r'\b(?:seat|seat no|coach/seat)[:\s]*([0-9]{1,3}[A-K]?)\b', text, re.IGNORECASE)
        data["seat"] = m_seat.group(1) if m_seat else None

        dates = extract_dates_and_times(text)
        data["date"] = dates[0]["raw"] if dates else None
        data["normalized_date"] = dates[0]["normalized"] if dates else None

        m_time = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b', text)
        data["time"] = m_time.group(1) if m_time else None

        m_pass = re.search(r'(?:passenger|name)[:\s]+([A-Za-z\s/]+)', text, re.IGNORECASE)
        data["passenger_name"] = m_pass.group(1).strip().split('\n')[0] if m_pass else None

    # 5. Travel Booking
    elif category == "travel_booking":
        provider = None
        for p in ["Booking.com", "Airbnb", "Expedia", "Marriott", "Hilton", "Hyatt", "Hotels.com", "Agoda"]:
            if p.lower() in lower:
                provider = p
                break
        data["provider"] = provider or (lines[0] if lines else "Travel Provider")
        data["booking_provider"] = data["provider"]

        m_conf = re.search(r'(?:confirmation number|reservation code|booking id|reference)[:\s]*([A-Z0-9-]{5,14})', text, re.IGNORECASE)
        data["booking_reference"] = m_conf.group(1).strip() if m_conf else None
        data["confirmation_code"] = data["booking_reference"]

        destination = None
        m_dest = re.search(r'(?:hotel|property|location|resort)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if m_dest:
            destination = m_dest.group(1).strip()
        data["destination"] = destination

        dates = extract_dates_and_times(text)
        data["check_in_details"] = dates[0]["raw"] if len(dates) >= 1 else None
        data["check_out_details"] = dates[1]["raw"] if len(dates) >= 2 else None
        data["check_in_date"] = data["check_in_details"]
        data["check_out_date"] = data["check_out_details"]
        data["normalized_date"] = dates[0]["normalized"] if dates else None

        m_room = re.search(r'(?:room type|room)[:\s]+([^\n]+)', text, re.IGNORECASE)
        data["journey_details"] = m_room.group(1).strip() if m_room else None

    # 6. Identity Document (Strict Masking for Privacy)
    elif category == "identity_document":
        doc_type = "National ID"
        if "passport" in lower: doc_type = "Passport"
        elif "driver" in lower or "driving" in lower: doc_type = "Driver's License"
        elif "aadhaar" in lower: doc_type = "Aadhaar Card"
        elif "pan" in lower and "card" in lower: doc_type = "PAN Card"
        data["document_type"] = doc_type

        auth = None
        m_auth = re.search(r'(?:republic of|government of|state of|department of motor vehicles)[:\s]*([A-Za-z\s]+)', text, re.IGNORECASE)
        if m_auth:
            auth = m_auth.group(0).strip().split('\n')[0]
        data["issuing_authority"] = auth or "Government Authority"

        full_name = None
        m_name = re.search(r'(?:name|given names?|surname)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if m_name:
            full_name = m_name.group(1).strip().split('\n')[0]
        data["full_name"] = full_name

        # MASK SENSITIVE ID NUMBERS
        m_id = re.search(r'\b(?:id no|passport no|licence no|license no|dl no|uid)[:\s]*([A-Z0-9-]{6,16})\b', text, re.IGNORECASE)
        if m_id:
            raw_id = m_id.group(1)
            data["id_number_masked"] = re.sub(r'[A-Za-z0-9](?=.{4})', '*', raw_id)
        else:
            data["id_number_masked"] = None

        dates = extract_dates_and_times(text)
        data["expiry_date"] = dates[-1]["raw"] if dates else None
        data["normalized_date"] = dates[-1]["normalized"] if dates else None

    # 7. Certificate
    elif category == "certificate":
        data["certificate_type"] = subtype.replace("_", " ").title() if subtype else "Certificate of Achievement"
        
        recipient = None
        m_rec = re.search(r'(?:certify that|certifies that|awarded to|presented to|conferred upon)[:\s]+([^\n]+(?:\n[A-Za-z\s]+)?)', text, re.IGNORECASE)
        if m_rec:
            matched_lines = [l.strip() for l in m_rec.group(1).split('\n') if l.strip()]
            for ml in matched_lines:
                if len(ml) > 2 and not any(w in ml.lower() for w in ["successfully", "completed", "advanced", "course", "degree"]):
                    recipient = ml
                    break

        if not recipient:
            for i, l in enumerate(lines):
                if any(k in l.lower() for k in ["certify that", "certifies that", "awarded to", "presented to"]) and i + 1 < len(lines):
                    next_l = lines[i + 1].strip()
                    if len(next_l) > 2 and not any(w in next_l.lower() for w in ["successfully", "completed"]):
                        recipient = next_l
                        break

        data["recipient"] = recipient
        data["recipient_name"] = recipient

        issuer = None
        for l in lines[-4:]:
            if any(w in l.lower() for w in ["university", "institute", "academy", "foundation", "director", "chairperson", "authorized"]):
                issuer = l.strip()
                break
        data["issuing_organization"] = issuer
        data["issuer"] = issuer

        dates = extract_dates_and_times(text)
        data["issue_date"] = dates[0]["raw"] if dates else None
        data["normalized_date"] = dates[0]["normalized"] if dates else None

    # 8. Handwritten & Printed Notes
    elif category in ["handwritten_notes", "printed_notes"]:
        data["title"] = lines[0] if lines else "Study Notes"
        data["subject"] = lines[1] if len(lines) > 1 else "General Subject"
        topics = []
        for l in lines:
            clean_l = l.strip()
            if clean_l.startswith("-") or clean_l.startswith("•") or clean_l.startswith("*") or "todo" in clean_l.lower():
                topics.append(clean_l.lstrip("-•* "))
        data["main_topics"] = topics[:6]
        data["concise_summary"] = " ".join(lines[:4])

    # 9. Screenshot
    elif category == "screenshot":
        app_name = "Desktop / Mobile App"
        for app in ["Slack", "WhatsApp", "Chrome", "Browser", "Terminal", "Settings", "Twitter", "Instagram", "GitHub"]:
            if app.lower() in lower:
                app_name = app
                break
        data["application_or_content_type"] = app_name
        data["app_or_source"] = app_name
        data["main_text"] = "\n".join(lines[:6])
        data["summary"] = f"Screen capture from {app_name}"

    # 10. Menu or Food Information
    elif category == "menu_or_food_information":
        data["restaurant_or_business_name"] = lines[0] if lines else "Restaurant / Food Brand"
        data["restaurant_or_brand"] = data["restaurant_or_business_name"]
        items = []
        prices = []
        for l in lines:
            if re.search(r'[$€£₹]\s*\d+[.,]?\d*', l):
                prices.append(l.strip())
            elif len(l.strip()) > 3 and not any(k in l.lower() for k in ["menu", "starters", "main course", "desserts"]):
                items.append(l.strip())
        data["food_items"] = items[:8]
        data["prices"] = prices[:8]

    # 11. Product or Label
    elif category == "product_or_label":
        data["product_name"] = lines[0] if lines else "Consumer Product"
        brand = None
        for l in lines[:3]:
            if "brand" in l.lower() or "mfg" in l.lower():
                brand = l.strip()
                break
        data["brand"] = brand or (lines[1] if len(lines) > 1 else None)
        m_model = re.search(r'\b(?:model no|model|item no)[:\s]*([A-Z0-9-]+)', text, re.IGNORECASE)
        data["model"] = m_model.group(1).strip() if m_model else None
        data["relevant_label_details"] = "\n".join(lines[2:7])

    # 12. Medical Document (Strictly No Hallucinated Diagnoses)
    elif category == "medical_document":
        data["document_type"] = subtype.replace("_", " ").title() if subtype else "Clinical Record"
        dates = extract_dates_and_times(text)
        data["date"] = dates[0]["raw"] if dates else None
        data["normalized_date"] = dates[0]["normalized"] if dates else None

        clinic = None
        for l in lines[:4]:
            if any(w in l.lower() for w in ["hospital", "clinic", "dr.", "healthcare", "pathology", "diagnostic"]):
                clinic = l.strip()
                break
        data["relevant_metadata"] = {
            "facility_or_doctor": clinic,
            "disclaimer": "Informational extraction only; no diagnostic or clinical claims asserted."
        }
        data["clinic_or_doctor"] = clinic

    # 13. Official Document
    elif category == "official_document":
        data["document_type"] = subtype.replace("_", " ").title() if subtype else "Official Document"
        data["issuing_authority"] = lines[0] if lines else "Issuing Authority"
        m_ref = re.search(r'\b(?:ref no|reference no|case no|file no)[:\s]*([A-Z0-9/-]+)', text, re.IGNORECASE)
        data["reference_number"] = m_ref.group(1).strip() if m_ref else None
        dates = extract_dates_and_times(text)
        data["issue_date"] = dates[0]["raw"] if dates else None
        data["normalized_date"] = dates[0]["normalized"] if dates else None
        data["subject"] = lines[2] if len(lines) > 2 else "Official Administrative Subject"

    # 14. Other & Unknown
    else:
        data["general_description"] = lines[0] if lines else "Unclassified Document"
        data["extracted_text"] = text[:300]

    return data


# ------------------------------------------------------------------------------
# 5. Non-Automatic Reminder Suggestions
# ------------------------------------------------------------------------------
def generate_reminder_suggestions(
    category: str,
    subtype: Optional[str],
    title: str,
    category_fields: Dict[str, Any],
    normalized_dates: List[Dict[str, Any]],
    filename: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate actionable reminders for detected dates.
    Crucial: These are SUGGESTIONS only and will not be created automatically without user confirmation.
    """
    suggestions = []
    now = datetime.utcnow()

    # Collect distinct target dates
    target_dates = []
    if category_fields.get("normalized_due_date"):
        target_dates.append({
            "iso": category_fields["normalized_due_date"],
            "raw": category_fields.get("due_date"),
            "context": "due_date"
        })
    elif category_fields.get("normalized_date"):
        target_dates.append({
            "iso": category_fields["normalized_date"],
            "raw": category_fields.get("date") or category_fields.get("event_date") or category_fields.get("expiry_date"),
            "context": "primary_date"
        })

    for nd in normalized_dates:
        iso = nd["normalized"]
        if not any(t["iso"] == iso for t in target_dates):
            target_dates.append({"iso": iso, "raw": nd["raw"], "context": "general_date"})

    for item in target_dates:
        try:
            dt = datetime.fromisoformat(item["iso"])
            # Format context-specific reminder title
            if category == "bill":
                vendor = category_fields.get("vendor") or "Utility"
                amt = category_fields.get("amount") or ""
                rem_title = f"Pay Bill: {vendor}" + (f" ({amt})" if amt else "")
                reason_txt = f"Payment due date: {item['raw']}"
            elif category == "event_poster":
                ev_name = category_fields.get("event_name") or title
                rem_title = f"Attend Event: {ev_name}"
                reason_txt = f"Scheduled event date: {item['raw']}"
            elif category == "invitation":
                occ = category_fields.get("occasion") or "Celebration"
                host = category_fields.get("host_names") or title
                rem_title = f"Attend {occ}: {host}"
                reason_txt = f"Invitation date: {item['raw']}"
            elif category == "ticket":
                dest = category_fields.get("destination") or "destination"
                carrier = category_fields.get("carrier") or "Transit"
                rem_title = f"Travel Departure: {carrier} to {dest}"
                reason_txt = f"Scheduled departure: {item['raw']}"
            elif category == "travel_booking":
                dest = category_fields.get("destination") or title
                rem_title = f"Hotel Check-in: {dest}"
                reason_txt = f"Check-in date: {item['raw']}"
            elif category == "identity_document":
                doc = category_fields.get("document_type") or "ID Document"
                rem_title = f"Renew Document: {doc} Expiry"
                reason_txt = f"Document expiry date: {item['raw']}"
            elif category == "medical_document":
                rem_title = f"Medical Follow-up: {title}"
                reason_txt = f"Appointment/Report date: {item['raw']}"
            else:
                rem_title = f"Follow-up: {title}"
                reason_txt = f"Detected document date: {item['raw']}"

            days_diff = (dt - now).days
            priority = "urgent" if 0 <= days_diff <= 3 else "upcoming"

            suggestions.append({
                "id": f"sug-{uuid.uuid4().hex[:8]}",
                "title": rem_title,
                "dueDate": dt.isoformat(),
                "priority": priority,
                "rawDate": item["raw"],
                "reason": reason_txt,
                "source_ref": filename,
                "confirmed": False
            })
        except Exception as e:
            logger.warning(f"Failed to generate reminder suggestion for date: {e}")

    return suggestions


# ------------------------------------------------------------------------------
# 6. Summary and Keyword Synthesis
# ------------------------------------------------------------------------------
def generate_image_summary_and_keywords(
    category: str,
    subtype: Optional[str],
    category_fields: Dict[str, Any],
    cleaned_text: str,
    confidence: float,
    has_readable_text: bool
) -> Tuple[str, List[str], List[str]]:
    """
    Synthesize an executive summary, search keywords, and entities list.
    """
    if not has_readable_text or not cleaned_text:
        return (
            "Image captured with PaddleOCR. No legible text detected in visual contents.",
            ["Visual Image", "No Text Detected"],
            []
        )

    cat_label = category.replace("_", " ").title()
    sub_label = subtype.replace("_", " ").title() if subtype else cat_label

    summary_parts = []
    if category == "bill":
        vendor = category_fields.get("vendor") or "Provider"
        amt = category_fields.get("amount") or "amount"
        due = category_fields.get("due_date") or "due date"
        summary_parts.append(f"{sub_label} from {vendor} for {amt} due on {due}.")
    elif category == "receipt":
        merchant = category_fields.get("vendor") or category_fields.get("merchant") or "Store"
        amt = category_fields.get("amount") or "total"
        date_str = category_fields.get("date") or "unspecified date"
        summary_parts.append(f"Receipt from {merchant} for {amt} on {date_str}.")
    elif category == "event_poster":
        event = category_fields.get("event_name") or "Event"
        date_str = category_fields.get("event_date") or ""
        venue = category_fields.get("venue") or ""
        summary_parts.append(f"Event poster for '{event}'" + (f" scheduled for {date_str}" if date_str else "") + (f" at {venue}" if venue else "") + ".")
    elif category == "invitation":
        occ = category_fields.get("occasion") or "Celebration"
        host = category_fields.get("host_names") or "hosts"
        summary_parts.append(f"Invitation to {occ} from {host}.")
    elif category == "ticket":
        carrier = category_fields.get("carrier") or "Carrier"
        origin = category_fields.get("origin")
        dest = category_fields.get("destination")
        summary_parts.append(f"{sub_label} for {carrier}" + (f" from {origin} to {dest}" if origin and dest else "") + ".")
    elif category == "certificate":
        rec = category_fields.get("recipient") or "Recipient"
        title_c = category_fields.get("certificate_type") or "Certificate"
        summary_parts.append(f"{title_c} awarded to {rec}.")
    elif category == "identity_document":
        doc = category_fields.get("document_type") or "Identity Document"
        summary_parts.append(f"Official {doc} credential (confidential record with masked identifiers).")
    elif category == "travel_booking":
        prov = category_fields.get("provider") or "Travel Provider"
        dest = category_fields.get("destination") or "destination"
        summary_parts.append(f"Travel reservation from {prov} for {dest}.")
    elif category == "medical_document":
        doc = category_fields.get("document_type") or "Medical Document"
        summary_parts.append(f"{doc} record processed.")
    else:
        clean_first = " ".join(cleaned_text.split()[:20])
        summary_parts.append(f"{sub_label} analyzed via PaddleOCR ({int(confidence * 100)}% match): {clean_first}...")

    summary = " ".join(summary_parts)

    # Keywords & Entities Extraction
    keywords = set()
    keywords.add(cat_label)
    if subtype:
        keywords.add(sub_label)

    entities = []
    for k, v in category_fields.items():
        if isinstance(v, str) and v and len(v) < 40 and not k.endswith("_masked") and not k.startswith("normalized"):
            keywords.add(v)
            entities.append(v)
        elif isinstance(v, list):
            for it in v:
                if isinstance(it, str) and len(it) < 30:
                    keywords.add(it)
                    entities.append(it)

    for w in re.findall(r'\b[A-Z][a-zA-Z0-9-]{2,}\b', cleaned_text):
        if w.lower() not in {"the", "and", "for", "with", "from", "date", "total", "time", "amount"}:
            keywords.add(w)

    clean_kw = [k.strip() for k in keywords if k.strip()][:10]
    return summary, clean_kw, entities[:8]


# ------------------------------------------------------------------------------
# 7. Complete Multimodal Classification & Intelligence Pipeline
# ------------------------------------------------------------------------------
def analyze_image_intelligence(
    file_bytes: bytes,
    original_filename: str,
    ocr_details: Dict[str, Any],
    user_category_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Standardized, validated classification and extraction pipeline:
      - Validated JSON response fields
      - 17 categories with subtypes
      - Deep deterministic + optional LLM classification
      - Category-specific field extraction
      - Privacy masking for identity documents
      - Non-automatic reminder generation
    """
    has_text = ocr_details.get("has_readable_text", False)
    cleaned_text = ocr_details.get("cleaned_text", "")
    raw_text = ocr_details.get("raw_text", "")
    lines = ocr_details.get("lines", [])
    ocr_conf = ocr_details.get("confidence", 0.0)

    # 1. Classify Category & Subtype
    category, subtype, conf, reason, needs_review = classify_image_category(
        cleaned_text,
        lines,
        has_text,
        ocr_conf
    )

    # Honor explicit user category override if provided
    if user_category_hint and user_category_hint.lower() not in {"general", "all", "research", ""}:
        hint_clean = user_category_hint.lower().replace(" ", "_").replace("-", "_")
        for cat_cand in ALL_CATEGORIES:
            if cat_cand in hint_clean or hint_clean in cat_cand:
                category = cat_cand
                subtype = _determine_subtype(category, cleaned_text.lower(), lines)
                conf = 1.0
                reason = "User manually specified this category."
                needs_review = False
                break

    # 2. Extract structured category fields
    category_fields = extract_category_fields(category, subtype, cleaned_text, lines)

    # 3. Date Normalization
    normalized_dates = extract_dates_and_times(cleaned_text)

    # 4. Determine Suggested Title
    base_name = os.path.splitext(original_filename)[0] if original_filename else "Document"
    suggested_title = (
        category_fields.get("event_name")
        or category_fields.get("vendor")
        or category_fields.get("product_name")
        or category_fields.get("title")
        or base_name
    )

    # 5. Non-Automatic Reminder Suggestions
    reminders = generate_reminder_suggestions(
        category,
        subtype,
        suggested_title,
        category_fields,
        normalized_dates,
        original_filename
    )

    # 6. Summary, Keywords & Entities
    summary, keywords, extracted_entities = generate_image_summary_and_keywords(
        category,
        subtype,
        category_fields,
        cleaned_text,
        conf,
        has_text
    )

    # 7. Privacy protection for sensitive identity documents
    is_sensitive = (category == "identity_document")
    if is_sensitive:
        logger.info(f"Identity document processed ({original_filename}). Text content redacted from logs.")
    else:
        logger.info(f"Image classified as '{category}' ('{subtype}'), conf={conf*100:.0f}%, review={needs_review}.")

    # 8. Return Validated JSON Structure
    return {
        # Validated contract fields (Requirement 3)
        "category": category,
        "subtype": subtype,
        "confidence": conf,
        "reason": reason,
        "title": suggested_title,
        "summary": summary,
        "extracted_text": cleaned_text,
        "keywords": keywords,
        "extracted_entities": extracted_entities,
        "category_fields": category_fields,
        "needs_review": needs_review,

        # Backwards-compatible aliases for frontend & pipeline
        "categoryLabel": category.replace("_", " ").title(),
        "categoryConfidence": conf,
        "categoryData": category_fields,
        "hasReadableText": has_text,
        "cleanedText": cleaned_text,
        "rawText": raw_text,
        "lineCount": len(lines),
        "wordCount": len(cleaned_text.split()),
        "normalizedDates": normalized_dates,
        "suggestedReminders": reminders,
        "isSensitive": is_sensitive,
        "processingStatus": "completed" if has_text else "completed_no_text"
    }
