from fastapi import APIRouter, Request, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
import logging

router = APIRouter()

@router.post("/saveSettings")
async def save_settings(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    settings_file = body.get("settings_file")
    if not settings_file:
        raise HTTPException(status_code=400, detail="Missing settings_file")
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        storage.save_json(user_id, "settings.json", settings_file)
        logging.info(f"User {user_id} saved settings")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Settings save error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings") 