from fastapi import APIRouter, Request, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
import logging

router = APIRouter()

@router.post("/saveAccount")
async def save_account(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    account_json = body.get("account_json")
    if not account_json:
        raise HTTPException(status_code=400, detail="Missing account_json")
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        storage.save_json(user_id, "account.json", account_json)
        logging.info(f"User {user_id} saved account")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Account save error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save account")

@router.post("/deleteAccount")
async def delete_user(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    user_id = body.get("userId")
    reason = body.get("reason")
    additional_reason = body.get("additionalReason")
    timestamp = body.get("timestamp")

    if not user_id or not reason or not timestamp:
        raise HTTPException(status_code=400, detail="Missing required fields: userId, reason, or timestamp")

    # Optionally, check that the user_id matches the authenticated user
    if user_id != user['uid']:
        raise HTTPException(status_code=403, detail="User ID does not match authenticated user")

    storage = get_storage_backend()
    try:
        # Store the deletion reason in a dedicated file
        deletion_data = {
            "reason": reason,
            "additionalReason": additional_reason,
            "timestamp": timestamp
        }
        storage.save_json(user_id, "deletion_reason.json", deletion_data)
        logging.info(f"User {user_id} requested account deletion: {deletion_data}")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Delete user error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to log account deletion reason") 