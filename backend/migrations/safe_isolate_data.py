import sys
import os
from bson.objectid import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_db, to_object_id

def safe_isolate_existing_data():
    db = get_db()
    print("=== Safely Inspecting & Handling Existing Data ===")

    # 1. Establish ownership for known user records:
    # User 'nedya@gmail.com' has id 'usr-1792145805' and _id ObjectId('6ad246e5d7ba17ed43589e06')
    nedya = db.users.find_one({"email": "nedya@gmail.com"})
    if nedya:
        nedya_oid = nedya["_id"]
        # Update items created by Nedya with verified user_id ObjectId
        r = db.items.update_many(
            {"ownerId": "usr-1792145805"},
            {"$set": {"user_id": nedya_oid, "ownerId": str(nedya_oid)}}
        )
        print(f"Mapped {r.modified_count} items to owner 'nedya@gmail.com' (user_id: {nedya_oid})")

        # Map associated reminders (e.g., 'sug-6fd74646') to Nedya
        r2 = db.reminders.update_many(
            {"id": "sug-6fd74646"},
            {"$set": {"user_id": nedya_oid}}
        )
        print(f"Mapped {r2.modified_count} reminder to owner 'nedya@gmail.com'")

    # 2. Isolate unowned demo items (item-1 to item-5) and unowned reminders (ev-1, ev-2, ev-3)
    # They have no user_id or ownerId. Do NOT assign them to any user, and do NOT delete them.
    # Mark them with is_isolated: True and ownerId: 'SYSTEM_DEMO_ISOLATED' so normal user queries never see them.
    demo_item_ids = ["item-1", "item-2", "item-3", "item-4", "item-5"]
    r3 = db.items.update_many(
        {"id": {"$in": demo_item_ids}},
        {"$set": {"is_isolated": True, "ownerId": "SYSTEM_DEMO_ISOLATED", "user_id": None}}
    )
    print(f"Isolated {r3.modified_count} legacy demo items from normal user access.")

    # Any remaining unowned items:
    r4 = db.items.update_many(
        {"user_id": {"$exists": False}, "ownerId": {"$exists": False}},
        {"$set": {"is_isolated": True, "ownerId": "SYSTEM_DEMO_ISOLATED", "user_id": None}}
    )
    if r4.modified_count > 0:
        print(f"Isolated {r4.modified_count} additional unowned items.")

    # Isolate unowned demo reminders (ev-1, ev-2, ev-3):
    r5 = db.reminders.update_many(
        {"user_id": {"$exists": False}},
        {"$set": {"is_isolated": True, "user_id": None}}
    )
    print(f"Isolated {r5.modified_count} legacy demo reminders from normal user access.")

    print("=== Data Isolation Migration Complete ===")

if __name__ == "__main__":
    safe_isolate_existing_data()
