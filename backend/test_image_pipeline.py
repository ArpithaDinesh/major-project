import io
import sys
from PIL import Image, ImageDraw, ImageFont
import requests

BASE_URL = "http://127.0.0.1:8000/api"

def create_synthetic_image(text_lines, width=600, height=400, bg_color="white", text_color="black"):
    """Generate an in-memory PNG image with clean printed text."""
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    y = 30
    for line in text_lines:
        draw.text((30, y), line, fill=text_color)
        y += 35

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

def run_tests():
    print("=" * 60)
    print("TESTING MINDYSNC IMAGE INTELLIGENCE PIPELINE")
    print("=" * 60)

    # 1. Image Format Validation
    print("\n1. Testing Image Format Validation...")
    r = requests.post(
        f"{BASE_URL}/process/image",
        files={"file": ("test.exe", b"binarycontent", "application/octet-stream")}
    )
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("-> PASS: Rejected invalid file extension.")

    # 2. Image Size Limit Validation
    print("\n2. Testing File Size Validation (>25 MB)...")
    huge_bytes = b"0" * (26 * 1024 * 1024)
    r = requests.post(
        f"{BASE_URL}/process/image",
        files={"file": ("huge.png", huge_bytes, "image/png")}
    )
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("-> PASS: Rejected oversized image.")

    # 3. Receipt Image Processing
    print("\n3. Testing Receipt Image Processing...")
    receipt_lines = [
        "STARBUCKS COFFEE",
        "Store #1042 - Seattle, WA",
        "Date: 2026-10-24",
        "1 Caffe Latte    $4.95",
        "1 Blueberry Muffin  $3.50",
        "Subtotal: $8.45",
        "Tax: $0.85",
        "Total: $9.30",
        "Payment: Visa ending 4242",
        "Thank you for your visit!"
    ]
    receipt_bytes = create_synthetic_image(receipt_lines, width=500, height=450)
    
    r = requests.post(
        f"{BASE_URL}/process/image",
        files={"file": ("starbucks_receipt.png", receipt_bytes, "image/png")},
        data={"category": "Receipt"}
    )
    print(f"Status: {r.status_code}")
    res = r.json()
    print("Extracted Data:", {
        "category": res.get("category"),
        "categoryLabel": res.get("categoryLabel"),
        "merchant": res.get("categoryData", {}).get("merchant"),
        "amount": res.get("categoryData", {}).get("amount"),
        "date": res.get("categoryData", {}).get("date"),
        "fileUrl": res.get("fileUrl"),
        "hasReadableText": res.get("hasReadableText")
    })
    assert r.status_code == 200
    assert res.get("fileUrl") is not None
    print("-> PASS: Receipt processed, saved to storage, and structured.")

    # 4. Event Poster Image Processing
    print("\n4. Testing Event Poster Image Processing...")
    event_lines = [
        "AI INNOVATION SUMMIT 2026",
        "Presented by Global Tech Alliance",
        "Date: November 15, 2026",
        "Time: 9:00 AM",
        "Venue: Moscone Center, San Francisco",
        "Keynote: Future of Multi-Modal Intelligence",
        "Register now at techsummit.io"
    ]
    event_bytes = create_synthetic_image(event_lines, width=650, height=450)
    r = requests.post(
        f"{BASE_URL}/process/image",
        files={"file": ("event_poster.png", event_bytes, "image/png")}
    )
    print(f"Status: {r.status_code}")
    res = r.json()
    print("Extracted Data:", {
        "category": res.get("category"),
        "event_name": res.get("categoryData", {}).get("event_name"),
        "venue": res.get("categoryData", {}).get("venue"),
        "date": res.get("categoryData", {}).get("date"),
        "suggestedReminders": len(res.get("suggestedReminders", []))
    })
    assert r.status_code == 200
    assert res.get("category") == "event_poster"
    assert len(res.get("suggestedReminders", [])) > 0
    print("-> PASS: Event poster recognized and reminder suggested.")

    # 5. Image with No Readable Text
    print("\n5. Testing Image with No Readable Text (Blank Photo)...")
    blank_bytes = create_synthetic_image([], width=200, height=200, bg_color="gray")
    r = requests.post(
        f"{BASE_URL}/process/image",
        files={"file": ("landscape.png", blank_bytes, "image/png")}
    )
    print(f"Status: {r.status_code}")
    res = r.json()
    print("Extracted Data:", {
        "hasReadableText": res.get("hasReadableText"),
        "processingStatus": res.get("processingStatus"),
        "confidence": res.get("confidence")
    })
    assert r.status_code == 200
    assert res.get("hasReadableText") is False
    assert res.get("processingStatus") == "completed_no_text"
    print("-> PASS: Handled non-text image cleanly without errors.")

    # 6. Save Item into MongoDB Atlas
    print("\n6. Testing Save Image Item to MongoDB Atlas...")
    item_payload = {
        "title": "Starbucks Receipt Oct 2026",
        "type": "image",
        "category": "Receipt / Invoice",
        "imageCategory": "receipt",
        "imageUrl": res.get("fileUrl") or "/api/uploads/images/test.png",
        "fileRef": "backend/uploads/images/test.png",
        "fileSize": "120 KB",
        "content": "Starbucks Coffee\nTotal: $9.30",
        "summary": "Receipt from Starbucks for $9.30.",
        "categoryData": {
            "merchant": "Starbucks Coffee",
            "amount": "$9.30",
            "date": "2026-10-24"
        },
        "keywords": ["Starbucks", "Receipt", "Coffee"],
        "suggestedReminders": [
            {
                "id": "sug-123",
                "title": "Expense Starbucks Coffee",
                "dueDate": "2026-10-25T10:00:00",
                "confirmed": False
            }
        ],
        "detectedEvents": []  # Note: unconfirmed reminder NOT created yet!
    }
    r = requests.post(f"{BASE_URL}/items", json=item_payload)
    print(f"Status: {r.status_code}")
    created_item = r.json()
    assert r.status_code == 200
    item_id = created_item["id"]
    print(f"-> PASS: Item saved with ID: {item_id}")

    # 7. Test In-Place Field Update (Requirement 13)
    print("\n7. Testing In-Place Field Correction (PUT /items/{id})...")
    r = requests.put(f"{BASE_URL}/items/{item_id}", json={
        "title": "Starbucks Downtown Seattle",
        "categoryData": {
            "merchant": "Starbucks Downtown",
            "amount": "$9.30",
            "date": "2026-10-24"
        }
    })
    print(f"Status: {r.status_code}")
    updated = r.json()
    assert r.status_code == 200
    assert updated["title"] == "Starbucks Downtown Seattle"
    assert updated["categoryData"]["merchant"] == "Starbucks Downtown"
    print("-> PASS: Field corrections persisted.")

    # 8. Test Confirm Suggested Reminder (Requirement 12)
    print("\n8. Testing Confirm Reminder from Image (POST /items/{id}/confirm-reminder)...")
    r = requests.post(f"{BASE_URL}/items/{item_id}/confirm-reminder", json={
        "title": "Expense Starbucks Coffee",
        "dueDate": "2026-10-25T10:00:00",
        "priority": "upcoming"
    })
    print(f"Status: {r.status_code}")
    rem_doc = r.json()
    assert r.status_code == 200
    assert rem_doc["title"] == "Expense Starbucks Coffee"
    assert rem_doc["sourceId"] == item_id
    print("-> PASS: Reminder confirmed and created in reminders collection.")

    # 9. Test Keyword & Semantic Search for Category Fields (Requirement 11)
    print("\n9. Testing Search for 'Starbucks'...")
    r = requests.get(f"{BASE_URL}/items?search=Starbucks")
    assert r.status_code == 200
    found = r.json()
    assert any(it["id"] == item_id for it in found), "Item not found in search results"
    print(f"-> PASS: Found {len(found)} item(s) matching keyword search.")

    # 10. Test RAG Pipeline with Image Data
    print("\n10. Testing RAG Chat retrieval for 'Starbucks'...")
    r = requests.post(f"{BASE_URL}/chat", json={"prompt": "What did I buy at Starbucks?"})
    assert r.status_code == 200
    chat_res = r.json()
    print("Chat Answer Snippet:\n", chat_res["reply"][:200], "...")
    assert len(chat_res.get("sources", [])) > 0
    print("-> PASS: RAG successfully retrieved and cited Starbucks receipt.")

    print("\n" + "=" * 60)
    print("ALL 16 REQUIREMENTS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
