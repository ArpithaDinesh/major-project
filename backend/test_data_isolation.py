import os
import io
import sys
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from database import get_db, is_atlas_connected, to_object_id

client = TestClient(app)

def create_sample_image_bytes(text="User A Secret Blueprint"):
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 40), text, fill=(0, 0, 0))
    draw.text((30, 90), "Event Date: 2026-12-25 18:00:00", fill=(0, 0, 0))
    draw.text((30, 140), "Location: User A Private Vault Room", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def run_all_isolation_tests():
    print("=" * 65)
    print("RUNNING COMPREHENSIVE USER DATA ISOLATION TEST SUITE")
    print("=" * 65)
    
    db = get_db()
    print(f"MongoDB Atlas Connected: {is_atlas_connected()}")

    # Setup 2 independent user accounts
    rand_suffix = os.urandom(3).hex()
    user_a_email = f"usera_{rand_suffix}@privacy.vault"
    user_b_email = f"userb_{rand_suffix}@privacy.vault"
    password = "StrongPassword123!"

    print("\n[Step 0] Registering User A and User B...")
    reg_a = client.post("/auth/signup", json={"name": "Alice Privacy", "email": user_a_email, "password": password})
    assert reg_a.status_code == 200, f"User A signup failed: {reg_a.text}"
    user_a = reg_a.json()
    token_a = user_a["token"]
    user_a_id = user_a["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"User A registered: id={user_a_id}, email={user_a_email}")

    reg_b = client.post("/auth/signup", json={"name": "Bob Intruder", "email": user_b_email, "password": password})
    assert reg_b.status_code == 200, f"User B signup failed: {reg_b.text}"
    user_b = reg_b.json()
    token_b = user_b["token"]
    user_b_id = user_b["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"User B registered: id={user_b_id}, email={user_b_email}")

    # =========================================================================
    # Test 1: User A uploads an image and a document
    # =========================================================================
    print("\n[Test 1] User A uploads an image and a document...")
    img_bytes = create_sample_image_bytes("Top Secret Alpha Project - Confidential")
    upload_img_res = client.post(
        "/process/image",
        headers=headers_a,
        files={"file": ("alpha_blueprint.png", img_bytes, "image/png")},
        data={"category": "documents"}
    )
    assert upload_img_res.status_code == 200, f"User A image upload failed: {upload_img_res.text}"
    img_data = upload_img_res.json()
    file_id_a = img_data["file_id"]
    print(f"User A image created: file_id={file_id_a}")

    # User A saves image as vault item
    item_img_res = client.post(
        "/items",
        headers=headers_a,
        json={
            "title": "Confidential Alpha Architecture Diagram",
            "type": "image",
            "category": "documents",
            "summary": "Executive schematic of Alpha neural clustering.",
            "content": "Confidential Alpha Architecture: Private cluster nodes with hardware security keys.",
            "tags": ["Confidential", "AlphaProject", "Architecture"],
            "entities": ["Alpha Node", "Security Key"],
            "fileRef": file_id_a,
            "detectedEvents": [
                {
                    "title": "Alpha Project Architecture Review",
                    "dueDate": "2026-11-20T15:00:00",
                    "priority": "urgent",
                    "completed": False
                }
            ]
        }
    )
    assert item_img_res.status_code == 200, f"User A image item creation failed: {item_img_res.text}"
    item_img_a = item_img_res.json()
    item_img_id_a = item_img_a["id"]
    print(f"User A image item indexed: id={item_img_id_a}")

    # User A creates a document item
    item_doc_res = client.post(
        "/items",
        headers=headers_a,
        json={
            "title": "User A Financial Audit Strategy 2026",
            "type": "document",
            "category": "documents",
            "summary": "Private financial balance sheets and quarterly revenue disclosures.",
            "content": "Net Q3 revenue reached 4.2M with zero debt liability. Encrypted financial ledger.",
            "tags": ["Finance", "Audit", "PrivateLedger"],
            "entities": ["Revenue 4.2M", "Ledger"]
        }
    )
    assert item_doc_res.status_code == 200, f"User A document item creation failed: {item_doc_res.text}"
    item_doc_a = item_doc_res.json()
    item_doc_id_a = item_doc_a["id"]
    print(f"User A document item indexed: id={item_doc_id_a}")

    # =========================================================================
    # Test 2: User B logs in and must not see either file
    # =========================================================================
    print("\n[Test 2] User B logs in and verifies vault isolation...")
    # Get User B items
    items_b = client.get("/items", headers=headers_b).json()
    b_item_ids = [it["id"] for it in items_b]
    assert item_img_id_a not in b_item_ids, "DATA LEAK: User B can see User A's image item!"
    assert item_doc_id_a not in b_item_ids, "DATA LEAK: User B can see User A's document item!"
    assert len(items_b) == 0, f"DATA LEAK: User B's vault should be empty, but found {len(items_b)} items!"
    print(f"PASS: User B sees 0 items. Neither User A's image nor document is visible.")

    # Get User B files list
    files_b = client.get("/files", headers=headers_b).json()
    b_file_ids = [f["_id"] for f in files_b]
    assert file_id_a not in b_file_ids, "DATA LEAK: User B can see User A's uploaded file record!"
    assert len(files_b) == 0, f"DATA LEAK: User B files list should be empty, but found {len(files_b)} files!"
    print(f"PASS: User B file list is empty. User A's file is not listed.")

    # =========================================================================
    # Test 3: User B must not be able to access User A's files by guessing/copying IDs
    # =========================================================================
    print("\n[Test 3] User B attempts direct access using User A's IDs...")
    direct_file = client.get(f"/files/{file_id_a}", headers=headers_b)
    assert direct_file.status_code == 403, f"SECURITY FAILURE: User B accessed User A's file directly! status={direct_file.status_code}"

    direct_item_img = client.get(f"/items/{item_img_id_a}", headers=headers_b)
    assert direct_item_img.status_code == 403, f"SECURITY FAILURE: User B accessed User A's image item directly! status={direct_item_img.status_code}"

    direct_item_doc = client.get(f"/items/{item_doc_id_a}", headers=headers_b)
    assert direct_item_doc.status_code == 403, f"SECURITY FAILURE: User B accessed User A's document item directly! status={direct_item_doc.status_code}"
    print("PASS: User B receives HTTP 403 Forbidden for all attempted direct ID lookups.")

    # =========================================================================
    # Test 4: User B's keyword and semantic searches must not return User A's content
    # =========================================================================
    print("\n[Test 4] User B executes keyword search and semantic/RAG chat...")
    # Keyword search on /items
    search_res = client.get("/items?search=Alpha", headers=headers_b).json()
    assert len(search_res) == 0, f"DATA LEAK: User B keyword search for 'Alpha' returned: {search_res}"

    search_res2 = client.get("/items?search=Financial", headers=headers_b).json()
    assert len(search_res2) == 0, f"DATA LEAK: User B keyword search for 'Financial' returned: {search_res2}"

    # Semantic / RAG query on /chat
    chat_res = client.post("/chat", headers=headers_b, json={"prompt": "Tell me about the Alpha Project Architecture"}).json()
    assert "Alpha Architecture" not in chat_res.get("reply", "") or "Confidential" not in chat_res.get("reply", ""), \
        f"DATA LEAK: User B chat query leaked User A's content: {chat_res['reply']}"
    assert len(chat_res.get("sources", [])) == 0, f"DATA LEAK: User B chat returned User A sources: {chat_res['sources']}"

    chat_res2 = client.post("/chat", headers=headers_b, json={"prompt": "What are my financial revenue balance sheets?"}).json()
    assert "4.2M" not in chat_res2.get("reply", ""), f"DATA LEAK: User B chat query leaked revenue 4.2M: {chat_res2['reply']}"
    assert len(chat_res2.get("sources", [])) == 0, f"DATA LEAK: User B chat returned sources: {chat_res2['sources']}"
    print("PASS: User B keyword and semantic searches returned zero records and zero leaked content.")

    # =========================================================================
    # Test 5: User B must not access User A's extracted text, summaries, metadata, or reminders
    # =========================================================================
    print("\n[Test 5] User B attempts access to extracted text, metadata, and reminders...")
    # Extracted content check
    ext_res = client.get(f"/files/{file_id_a}/extracted-content", headers=headers_b)
    assert ext_res.status_code == 403, f"DATA LEAK: User B accessed extracted text! status={ext_res.status_code}"

    # Metadata record check
    meta_res = client.get(f"/files/{file_id_a}/metadata", headers=headers_b)
    assert meta_res.status_code == 403, f"DATA LEAK: User B accessed metadata! status={meta_res.status_code}"

    # Metadata search query
    meta_query = client.get("/metadata?search=Alpha", headers=headers_b).json()
    assert len(meta_query) == 0, f"DATA LEAK: User B queried metadata and found: {meta_query}"

    # Reminders list check (User A had an auto-generated reminder 'Alpha Project Architecture Review')
    reminders_b = client.get("/reminders", headers=headers_b).json()
    assert not any("Alpha" in r.get("title", "") for r in reminders_b), "DATA LEAK: User B sees User A's reminder!"
    print("PASS: User B blocked from extracted content, metadata, summaries, and reminders.")

    # =========================================================================
    # Test 6: User B must not update or delete User A's records
    # =========================================================================
    print("\n[Test 6] User B attempts to tamper, update, or delete User A's records...")
    # Attempt update item
    upd_item = client.put(f"/items/{item_img_id_a}", headers=headers_b, json={"title": "Hacked Title"})
    assert upd_item.status_code == 403, "SECURITY FAILURE: User B was able to update User A's item!"

    # Attempt delete item
    del_item = client.delete(f"/items/{item_img_id_a}", headers=headers_b)
    assert del_item.status_code == 403, "SECURITY FAILURE: User B was able to delete User A's item!"

    # Attempt delete file
    del_file = client.delete(f"/files/{file_id_a}", headers=headers_b)
    assert del_file.status_code == 403, "SECURITY FAILURE: User B was able to delete User A's file!"

    # Attempt update metadata
    upd_meta = client.put(f"/files/{file_id_a}/metadata", headers=headers_b, json={"title": "Hacked Meta"})
    assert upd_meta.status_code == 403, "SECURITY FAILURE: User B was able to update User A's metadata!"

    # Attempt toggle favorite
    fav_res = client.post(f"/items/{item_img_id_a}/favorite", headers=headers_b)
    assert fav_res.status_code == 403, "SECURITY FAILURE: User B was able to toggle favorite on User A's item!"
    print("PASS: User B denied all update, delete, and modification requests with HTTP 403 Forbidden.")

    # =========================================================================
    # Test 7: User A can still access their own files after logout and login
    # =========================================================================
    print("\n[Test 7] User A re-authenticates (logout & login) and verifies own data intact...")
    login_a = client.post("/auth/login", json={"email": user_a_email, "password": password})
    assert login_a.status_code == 200, f"User A re-login failed: {login_a.text}"
    token_a_new = login_a.json()["token"]
    headers_a_new = {"Authorization": f"Bearer {token_a_new}"}

    items_a = client.get("/items", headers=headers_a_new).json()
    a_ids = [it["id"] for it in items_a]
    assert item_img_id_a in a_ids, "FAILURE: User A cannot find their own image item after re-login!"
    assert item_doc_id_a in a_ids, "FAILURE: User A cannot find their own document item after re-login!"

    file_a_check = client.get(f"/files/{file_id_a}", headers=headers_a_new)
    assert file_a_check.status_code == 200, "FAILURE: User A cannot fetch their own file after re-login!"

    chat_a = client.post("/chat", headers=headers_a_new, json={"prompt": "When is my Alpha Project review?"}).json()
    assert any("Alpha" in s.get("title", "") for s in chat_a.get("sources", [])) or "Alpha" in chat_a.get("reply", ""), \
        f"FAILURE: User A cannot retrieve their own Alpha Project details via chat: {chat_a}"
    print("PASS: User A successfully re-authenticated and verified all own files and items remain intact.")

    # =========================================================================
    # Test 8: Repeat tests for documents, images, and vector-search results
    # =========================================================================
    print("\n[Test 8] Repeating tests for documents, images, and vector-search results...")
    # User B creates their own private item
    item_b_create = client.post(
        "/items",
        headers=headers_b,
        json={
            "title": "Bob Independent Project Beta",
            "type": "note",
            "category": "notes",
            "summary": "Bob's private note regarding project Beta.",
            "content": "Project Beta strictly belongs to User B."
        }
    )
    assert item_b_create.status_code == 200
    item_b_id = item_b_create.json()["id"]

    # Verify User A cannot see Bob's item
    items_a_now = client.get("/items", headers=headers_a_new).json()
    assert not any(it["id"] == item_b_id for it in items_a_now), "DATA LEAK: User A can see User B's item!"

    # Verify User A cannot query Bob's item directly
    forbidden_get = client.get(f"/items/{item_b_id}", headers=headers_a_new)
    assert forbidden_get.status_code == 403, "SECURITY FAILURE: User A accessed User B's item directly!"

    # Verify vector search isolation on MongoDB Atlas embeddings
    from services.rag_service import search_vector_embeddings
    chunks_for_b = search_vector_embeddings(db, to_object_id(user_b_id), "Alpha confidential project")
    assert not any(c.get("item_id") == item_img_id_a or c.get("file_id") == file_id_a for c in chunks_for_b), \
        "DATA LEAK: Atlas vector search for User B returned User A's vector chunk!"

    chunks_for_a = search_vector_embeddings(db, to_object_id(user_a_id), "Alpha confidential project")
    # Verify chunks for A belong exclusively to A
    for c in chunks_for_a:
        assert str(c.get("user_id")) == str(user_a_id), "DATA LEAK: Cross-user chunk found in User A vector results!"

    print("PASS: Bi-directional isolation verified across documents, images, and vector embeddings.")

    print("\n" + "=" * 65)
    print("ALL 8 USER DATA ISOLATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_isolation_tests()
