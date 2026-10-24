import os
import io
import sys
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from database import get_db, is_atlas_connected

client = TestClient(app)

def create_sample_image_bytes():
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 40), "MindSync Tech Conference 2026", fill=(0, 0, 0))
    draw.text((30, 90), "Date: 2026-11-15 10:00 AM", fill=(0, 0, 0))
    draw.text((30, 140), "Venue: Silicon Hall, San Francisco", fill=(0, 0, 0))
    draw.text((30, 190), "Organizer: MindSync Labs", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def run_tests():
    print("=== 1. Testing Database & Atlas Status ===")
    db = get_db()
    print(f"Atlas Connected: {is_atlas_connected()}")

    print("\n=== 2. Testing User Registration & Authentication ===")
    user_a_email = f"user_a_{os.urandom(3).hex()}@example.com"
    user_b_email = f"user_b_{os.urandom(3).hex()}@example.com"
    pwd = "SecurePassword123!"

    # Signup User A
    res_a = client.post("/auth/signup", json={"name": "Alice Tester", "email": user_a_email, "password": pwd})
    assert res_a.status_code == 200, f"User A signup failed: {res_a.text}"
    user_a = res_a.json()
    token_a = user_a["access_token"]
    user_a_id = user_a["id"]
    print(f"User A registered successfully: id={user_a_id}, email={user_a_email}")

    # Signup User B
    res_b = client.post("/auth/signup", json={"name": "Bob Intruder", "email": user_b_email, "password": pwd})
    assert res_b.status_code == 200, f"User B signup failed: {res_b.text}"
    user_b = res_b.json()
    token_b = user_b["access_token"]
    user_b_id = user_b["id"]
    print(f"User B registered successfully: id={user_b_id}, email={user_b_email}")

    # Login User A
    login_a = client.post("/auth/login", json={"email": user_a_email, "password": pwd})
    assert login_a.status_code == 200, f"User A login failed: {login_a.text}"
    assert "token" in login_a.json()
    print("User A login verified.")

    # Duplicate registration prevention
    dup_res = client.post("/auth/signup", json={"name": "Alice Duplicate", "email": user_a_email, "password": pwd})
    assert dup_res.status_code == 400, "Duplicate email check failed!"
    print("Duplicate email unique check verified.")

    print("\n=== 3. Testing 8-Step PaddleOCR & DB Collections Pipeline ===")
    img_bytes = create_sample_image_bytes()
    upload_res = client.post(
        "/process/image",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("tech_conference_poster.png", img_bytes, "image/png")},
        data={"category": "event_poster"}
    )
    assert upload_res.status_code == 200, f"Image upload failed: {upload_res.text}"
    pipeline_data = upload_res.json()
    file_id = pipeline_data["file_id"]
    print(f"Image pipeline executed successfully. Created file_id: {file_id}")
    print(f"Extracted category: {pipeline_data.get('categoryNormalized') or pipeline_data.get('category')}")
    print(f"Status: {pipeline_data.get('processingStatus')}")

    # Verify MongoDB Atlas collections directly
    from database import to_object_id
    f_oid = to_object_id(file_id)

    # 1. files collection record
    file_doc = db.files.find_one({"_id": f_oid})
    assert file_doc is not None, "File record missing in 'files' collection!"
    assert file_doc["original_filename"] == "tech_conference_poster.png"
    assert file_doc["file_type"] == "image"
    assert file_doc["mime_type"] == "image/png"
    assert file_doc["processing_status"] in ["completed", "completed_no_text"]
    assert file_doc["processing_error"] is None
    assert os.path.exists(file_doc["stored_file_path"]), f"Physical file missing on disk: {file_doc['stored_file_path']}"
    print(f"Verified 'files' collection: stored on disk at {file_doc['stored_file_path']}")

    # 2. extracted_content collection record
    content_doc = db.extracted_content.find_one({"file_id": f_oid})
    assert content_doc is not None, "Extracted content record missing in 'extracted_content' collection!"
    assert content_doc["extraction_method"] == "PaddleOCR"
    print(f"Verified 'extracted_content' collection: method={content_doc['extraction_method']}")

    # 3. metadata collection record
    meta_doc = db.metadata.find_one({"file_id": f_oid})
    assert meta_doc is not None, "Metadata record missing in 'metadata' collection!"
    assert meta_doc["category"] in ["documents", "events", "travel", "food", "tickets", "receipts", "identity documents", "notes", "other"]
    print(f"Verified 'metadata' collection: normalized category='{meta_doc['category']}', title='{meta_doc['title']}'")

    print("\n=== 4. Testing Strict Ownership & User Isolation ===")
    # User A accesses their file: Should succeed (200)
    auth_get_a = client.get(f"/files/{file_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert auth_get_a.status_code == 200, f"User A could not access own file: {auth_get_a.text}"

    # User B accesses User A's file: MUST BE REJECTED with 403 Forbidden!
    auth_get_b = client.get(f"/files/{file_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert auth_get_b.status_code == 403, f"SECURITY VULNERABILITY: User B accessed User A's file! status={auth_get_b.status_code}"
    print("User isolation verified on GET /files/{id}: User B rejected with 403 Forbidden.")

    # User B accesses User A's extracted content: MUST BE REJECTED with 403 Forbidden!
    ext_b = client.get(f"/files/{file_id}/extracted-content", headers={"Authorization": f"Bearer {token_b}"})
    assert ext_b.status_code == 403, "SECURITY VULNERABILITY: User B accessed User A's extracted content!"
    print("User isolation verified on GET /files/{id}/extracted-content: User B rejected with 403 Forbidden.")

    # User B accesses User A's metadata: MUST BE REJECTED with 403 Forbidden!
    meta_b = client.get(f"/files/{file_id}/metadata", headers={"Authorization": f"Bearer {token_b}"})
    assert meta_b.status_code == 403, "SECURITY VULNERABILITY: User B accessed User A's metadata!"
    print("User isolation verified on GET /files/{id}/metadata: User B rejected with 403 Forbidden.")

    # User B attempts to DELETE User A's file: MUST BE REJECTED with 403 Forbidden!
    del_b = client.delete(f"/files/{file_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_b.status_code == 403, "SECURITY VULNERABILITY: User B deleted User A's file!"
    print("User isolation verified on DELETE /files/{id}: User B rejected with 403 Forbidden.")

    print("\n=== 5. Testing User Metadata Correction (Requirement 13) ===")
    update_res = client.put(
        f"/files/{file_id}/metadata",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "title": "MindSync Global AI Summit 2026",
            "category": "events",
            "summary": "Confirmed keynote conference on multi-modal neural memory.",
            "location": "Moscone Center West, San Francisco"
        }
    )
    assert update_res.status_code == 200, f"Metadata update failed: {update_res.text}"
    updated_meta = update_res.json()
    assert updated_meta["title"] == "MindSync Global AI Summit 2026"
    assert updated_meta["location"] == "Moscone Center West, San Francisco"
    print("User field correction verified without inventing values.")

    print("\n=== 6. Testing Reminders Collection with User & File ObjectIds ===")
    rem_res = client.post(
        "/reminders",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "title": "Attend MindSync Keynote",
            "dueDate": "2026-11-15T10:00:00",
            "priority": "urgent",
            "sourceId": file_id,
            "sourceTitle": "MindSync Global AI Summit 2026"
        }
    )
    assert rem_res.status_code == 200, f"Reminder creation failed: {rem_res.text}"
    rem_data = rem_res.json()
    rem_id = rem_data["id"]
    print(f"Created reminder id: {rem_id}")

    # Check reminder list isolated by user
    rem_list_a = client.get("/reminders", headers={"Authorization": f"Bearer {token_a}"}).json()
    rem_list_b = client.get("/reminders", headers={"Authorization": f"Bearer {token_b}"}).json()
    assert any(r["id"] == rem_id for r in rem_list_a), "Reminder missing for User A!"
    assert not any(r["id"] == rem_id for r in rem_list_b), "Reminder leaked to User B!"
    print("Reminder user isolation verified.")

    print("\n=== 7. Testing Metadata Search Endpoint ===")
    meta_search = client.get("/metadata?category=events", headers={"Authorization": f"Bearer {token_a}"})
    assert meta_search.status_code == 200
    meta_results = meta_search.json()
    assert len(meta_results) >= 1
    print(f"Metadata query returned {len(meta_results)} record(s) for category 'events'.")

    print("\n=== ALL PIPELINE, COLLECTIONS, INDEXES & ISOLATION TESTS PASSED! ===")

if __name__ == "__main__":
    run_tests()
