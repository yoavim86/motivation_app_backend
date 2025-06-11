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