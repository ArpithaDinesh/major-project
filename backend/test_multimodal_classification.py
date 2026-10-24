"""
Test Suite: General-Purpose Image Classification and Information Extraction
Adheres to the 10 document types required in specification:
  1. Electricity Bill
  2. Shopping Receipt
  3. College Event Poster
  4. Wedding Invitation
  5. Birthday Invitation
  6. Train or Flight Ticket
  7. Certificate
  8. Handwritten Notes
  9. Screenshot
 10. Unreadable / Low-Information Image
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.image_intelligence import (
    classify_image_category,
    classify_image_category_nlp,
    extract_category_fields,
    generate_reminder_suggestions,
    generate_image_summary_and_keywords,
    analyze_image_intelligence
)


# ==============================================================================
# 1. Electricity Bill Test
# ==============================================================================
def test_electricity_bill():
    text = (
        "PACIFIC POWER CORPORATION\n"
        "ELECTRICITY BILL / TAX INVOICE\n"
        "Consumer No: ACC-8921094\n"
        "Tariff: Residential LT-1\n"
        "Previous Reading: 1420 kWh\n"
        "Current Reading: 1680 kWh\n"
        "Units Consumed: 260 kWh\n"
        "Bill Date: 2026-10-15\n"
        "Payment Due Date: Nov 15, 2026\n"
        "Amount Payable: $142.50\n"
        "Late Payment Surcharge: $10.00"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.94
    }

    result = analyze_image_intelligence(b"fake_bytes", "pacific_power_bill.png", ocr_details)

    assert result["category"] == "bill", f"Expected 'bill', got '{result['category']}'"
    assert result["subtype"] == "electricity_bill", f"Expected 'electricity_bill', got '{result['subtype']}'"
    assert result["confidence"] >= 0.70
    assert result["needs_review"] is False
    assert "electricity" in result["reason"].lower() or "kwh" in result["reason"].lower() or "utility" in result["reason"].lower()
    
    fields = result["category_fields"]
    assert fields["amount"] == "$142.50" or "142.50" in str(fields["amount"])
    assert fields["due_date"] is not None and "15" in fields["due_date"]
    assert fields["vendor"] is not None
    assert fields["payment_status"] == "due"

    # Reminders: must suggest reminder for due date, confirmed=False
    reminders = result["suggestedReminders"]
    assert len(reminders) > 0
    assert any("bill" in r["title"].lower() or "pacific" in r["title"].lower() for r in reminders)
    assert all(r["confirmed"] is False for r in reminders)
    print("[PASS] Test 1: Electricity Bill Passed")


# ==============================================================================
# 2. Shopping Receipt Test
# ==============================================================================
def test_shopping_receipt():
    text = (
        "TARGET STORE #1042\n"
        "123 MARKET STREET, SAN FRANCISCO CA\n"
        "09/24/2026 14:32:00\n"
        "ORDER # 482910\n"
        "1 ORGANIC MILK      $4.50\n"
        "2 WHOLE WHEAT BREAD $6.00\n"
        "1 HONEYCRISP APPLES $5.20\n"
        "SUBTOTAL            $15.70\n"
        "TAX                 $1.35\n"
        "TOTAL               $17.05\n"
        "VISA ENDING 4920    $17.05\n"
        "CHANGE DUE          $0.00\n"
        "THANK YOU FOR SHOPPING AT TARGET"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.95
    }

    result = analyze_image_intelligence(b"fake_bytes", "target_receipt.jpg", ocr_details)

    assert result["category"] == "receipt", f"Expected 'receipt', got '{result['category']}'"
    assert result["confidence"] >= 0.75
    assert result["needs_review"] is False
    
    fields = result["category_fields"]
    assert fields["amount"] == "$17.05" or "17.05" in str(fields["amount"])
    assert fields["payment_status"] == "paid"
    assert fields["vendor"] is not None and "TARGET" in fields["vendor"]
    print("[PASS] Test 2: Shopping Receipt Passed")


# ==============================================================================
# 3. College Event Poster Test
# ==============================================================================
def test_college_event_poster():
    text = (
        "STANFORD UNIVERSITY\n"
        "DEPARTMENT OF COMPUTER SCIENCE PRESENTS\n"
        "ANNUAL AI & ROBOTICS SYMPOSIUM 2026\n"
        "Keynote Speaker: Dr. Andrew Ng\n"
        "Date: November 12, 2026\n"
        "Time: 09:00 AM\n"
        "Venue: Kresge Auditorium, Stanford Campus\n"
        "Registration Deadline: November 05, 2026\n"
        "Free Admission - Register Now at symposium.stanford.edu"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.92
    }

    result = analyze_image_intelligence(b"fake_bytes", "symposium_poster.png", ocr_details)

    assert result["category"] == "event_poster", f"Expected 'event_poster', got '{result['category']}'"
    assert result["subtype"] == "college_poster" or "poster" in result["subtype"]
    assert result["confidence"] >= 0.70
    assert result["needs_review"] is False

    fields = result["category_fields"]
    assert "ANNUAL AI" in (fields.get("event_name") or "") or "STANFORD" in (fields.get("event_name") or "")
    assert "Kresge Auditorium" in (fields.get("venue") or "") or "Stanford" in (fields.get("venue") or "")
    assert fields.get("start_time") == "09:00 AM" or "9:00" in str(fields.get("start_time"))
    
    # Check non-automatic reminder suggestion
    reminders = result["suggestedReminders"]
    assert len(reminders) > 0
    assert all(r["confirmed"] is False for r in reminders)
    print("✓ Test 3: College Event Poster Passed")


# ==============================================================================
# 4. Wedding Invitation Test
# ==============================================================================
def test_wedding_invitation():
    text = (
        "Together with their families\n"
        "Sarah Jenkins and Michael Harrison\n"
        "request the honour of your presence\n"
        "at their wedding ceremony and reception\n"
        "Saturday, December 19, 2026 at 4:00 PM\n"
        "Grace Cathedral, 1100 California St\n"
        "San Francisco, California\n"
        "RSVP by November 20 to jenkins-harrison.com"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.91
    }

    result = analyze_image_intelligence(b"fake_bytes", "wedding_invite.png", ocr_details)

    assert result["category"] == "invitation", f"Expected 'invitation', got '{result['category']}'"
    assert result["subtype"] == "wedding_invitation"
    assert result["confidence"] >= 0.70
    assert result["needs_review"] is False

    fields = result["category_fields"]
    assert fields.get("occasion") == "Wedding"
    assert "Sarah" in str(fields.get("host_names")) or "families" in str(fields.get("host_names"))
    assert "19" in str(fields.get("date")) or "December" in str(fields.get("date"))

    reminders = result["suggestedReminders"]
    assert len(reminders) > 0
    assert all(r["confirmed"] is False for r in reminders)
    print("✓ Test 4: Wedding Invitation Passed")


# ==============================================================================
# 5. Birthday Invitation Test
# ==============================================================================
def test_birthday_invitation():
    text = (
        "Join us in celebrating!\n"
        "Leo turns 5!\n"
        "Come for cake, games, and fun!\n"
        "Saturday, November 28, 2026 from 2:00 PM to 5:00 PM\n"
        "Sunnyvale Community Park, Picnic Area #3\n"
        "RSVP to Emma at 555-0192 by Nov 20\n"
        "Save the date!"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.90
    }

    result = analyze_image_intelligence(b"fake_bytes", "birthday_invite.jpg", ocr_details)

    assert result["category"] == "invitation", f"Expected 'invitation', got '{result['category']}'"
    assert result["subtype"] == "birthday_invitation"
    assert result["confidence"] >= 0.70
    assert result["needs_review"] is False

    fields = result["category_fields"]
    assert fields.get("occasion") == "Birthday"
    assert "28" in str(fields.get("date")) or "November" in str(fields.get("date"))
    print("✓ Test 5: Birthday Invitation Passed")


# ==============================================================================
# 6. Train or Flight Ticket Test
# ==============================================================================
def test_transit_ticket():
    text = (
        "UNITED AIRLINES\n"
        "BOARDING PASS\n"
        "Passenger Name: DOE/JOHN MR\n"
        "Flight No: UA 882\n"
        "Date: 24 OCT 2026\n"
        "Departure: SFO 10:45 AM\n"
        "Arrival: ORD 04:55 PM\n"
        "Gate: 82\n"
        "Seat: 14B\n"
        "PNR: X89QKL\n"
        "Boarding Time: 10:05 AM"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.96
    }

    result = analyze_image_intelligence(b"fake_bytes", "boarding_pass.png", ocr_details)

    assert result["category"] == "ticket", f"Expected 'ticket', got '{result['category']}'"
    assert result["subtype"] == "flight_ticket"
    assert result["confidence"] >= 0.80
    assert result["needs_review"] is False

    fields = result["category_fields"]
    assert fields.get("booking_reference") == "X89QKL" or fields.get("ticket_number") == "X89QKL"
    assert fields.get("seat") == "14B"
    assert fields.get("carrier") is not None and "UNITED" in fields["carrier"]

    reminders = result["suggestedReminders"]
    assert len(reminders) > 0
    assert all(r["confirmed"] is False for r in reminders)
    print("✓ Test 6: Flight Ticket Passed")


# ==============================================================================
# 7. Certificate Test
# ==============================================================================
def test_certificate():
    text = (
        "CERTIFICATE OF COMPLETION\n"
        "This is to certify that\n"
        "ALEXANDER WANG\n"
        "has successfully completed the advanced course\n"
        "Deep Learning with PyTorch and Transformers\n"
        "Issued on October 10, 2026\n"
        "Deep Learning Institute & Stanford Online\n"
        "Director: Dr. Fei-Fei Li"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.95
    }

    result = analyze_image_intelligence(b"fake_bytes", "completion_cert.pdf", ocr_details)

    assert result["category"] == "certificate", f"Expected 'certificate', got '{result['category']}'"
    assert "certificate" in result["subtype"] or "course" in result["subtype"]
    assert result["confidence"] >= 0.75
    assert result["needs_review"] is False

    fields = result["category_fields"]
    assert "ALEXANDER" in (fields.get("recipient") or "") or "ALEXANDER" in (fields.get("recipient_name") or "")
    print("✓ Test 7: Certificate Passed")


# ==============================================================================
# 8. Handwritten / Printed Study Notes Test
# ==============================================================================
def test_notes():
    text = (
        "Physics 201: Thermodynamics Lecture Notes\n"
        "Key Concepts & Equations\n"
        "- First Law: dU = dQ - dW (Conservation of energy)\n"
        "- Second Law: Entropy of isolated system always increases (dS >= 0)\n"
        "- Carnot Engine Efficiency: eta = 1 - (Tc / Th)\n"
        "Action Items:\n"
        "- [ ] Solve problems 4.1 to 4.8 from chapter 4\n"
        "- [ ] Review adiabatic expansion derivations"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.88
    }

    result = analyze_image_intelligence(b"fake_bytes", "lecture_notes.jpg", ocr_details)

    assert result["category"] in ["handwritten_notes", "printed_notes"], f"Got '{result['category']}'"
    assert result["confidence"] >= 0.65

    fields = result["category_fields"]
    assert "Physics" in fields.get("title", "") or "Thermodynamics" in fields.get("title", "")
    assert len(fields.get("main_topics", [])) > 0
    print("✓ Test 8: Study Notes Passed")


# ==============================================================================
# 9. Screenshot Test
# ==============================================================================
def test_screenshot():
    text = (
        "9:41 AM  5G  85%\n"
        "WhatsApp\n"
        "Engineering Team (12 members)\n"
        "Dave: Just pushed the latest commit for vector search indexing.\n"
        "Sarah: Awesome! The latency dropped to 42ms on the test cluster.\n"
        "Dave: Let's deploy to staging after review.\n"
        "Type a message..."
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.92
    }

    result = analyze_image_intelligence(b"fake_bytes", "chat_screenshot.png", ocr_details)

    assert result["category"] == "screenshot", f"Expected 'screenshot', got '{result['category']}'"
    assert result["subtype"] in ["chat_screenshot", "mobile_screenshot"]
    assert result["confidence"] >= 0.70

    fields = result["category_fields"]
    assert "WhatsApp" in fields.get("application_or_content_type", "")
    print("✓ Test 9: Screenshot Passed")


# ==============================================================================
# 10. Unreadable / Low Information Image Test
# ==============================================================================
def test_unreadable_low_information():
    text = "x . ~"
    lines = ["x . ~"]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.18
    }

    result = analyze_image_intelligence(b"fake_bytes", "blurred_photo.jpg", ocr_details)

    assert result["category"] == "unknown", f"Expected 'unknown', got '{result['category']}'"
    assert result["needs_review"] is True, "Expected needs_review to be True"
    assert result["confidence"] < 0.50
    assert "sparse" in result["reason"].lower() or "degraded" in result["reason"].lower() or "unreadable" in result["reason"].lower()
    print("✓ Test 10: Unreadable Low Information Image Passed")


# ==============================================================================
# Bonus 11: Identity Document Privacy Masking Test
# ==============================================================================
def test_identity_document_privacy():
    text = (
        "REPUBLIC OF INDIA\n"
        "PASSPORT\n"
        "Type: P  Country Code: IND  Passport No: Z4819204\n"
        "Surname: SHARMA\n"
        "Given Name: ROHIT\n"
        "Nationality: INDIAN\n"
        "Date of Birth: 15/08/1990\n"
        "Date of Expiry: 14/08/2030"
    )
    lines = [l.strip() for l in text.split("\n")]
    ocr_details = {
        "has_readable_text": True,
        "cleaned_text": text,
        "raw_text": text,
        "lines": lines,
        "confidence": 0.95
    }

    result = analyze_image_intelligence(b"fake_bytes", "passport_scan.png", ocr_details)

    assert result["category"] == "identity_document"
    assert result["isSensitive"] is True
    fields = result["category_fields"]
    # Check ID number masking: unmasked portion must not appear, only masked
    assert fields.get("id_number_masked") is not None
    assert "*" in fields["id_number_masked"]
    assert "Z4819204" not in fields["id_number_masked"]
    print("✓ Bonus Test 11: Identity Document Masking Passed")


if __name__ == "__main__":
    print("\n================ RUNNING MULTIMODAL CLASSIFIER TESTS ================\n")
    test_electricity_bill()
    test_shopping_receipt()
    test_college_event_poster()
    test_wedding_invitation()
    test_birthday_invitation()
    test_transit_ticket()
    test_certificate()
    test_notes()
    test_screenshot()
    test_unreadable_low_information()
    test_identity_document_privacy()
    print("\n================ ALL 11 TESTS PASSED SUCCESSFULLY! ================\n")
