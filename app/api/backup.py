from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
import logging

router = APIRouter()

@router.post("/backupDateSummary")
async def backup_date_summary(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    date = body.get("date")
    data_json = body.get("data_json")
    if not date or not data_json:
        raise HTTPException(status_code=400, detail="Missing date or data_json")
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        storage.save_json(user_id, f"data/{date}.json", data_json)
        logging.info(f"User {user_id} backed up summary for {date}")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Backup error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save summary") 