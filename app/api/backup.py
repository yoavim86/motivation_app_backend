from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile, File, Form
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
import logging
import datetime

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

@router.post("/fullBackup")
async def full_backup(
    user=Depends(verify_firebase_token),
    file: UploadFile = File(...),
    date: str = Form(...)
):
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        # Read the uploaded file
        file_bytes = await file.read()
        # Save as a binary blob in the full_backups folder
        path = f"full_backups/{date}.zip"
        storage.bucket.blob(f"{user_id}/{path}").upload_from_string(file_bytes, content_type='application/zip')
        logging.info(f"User {user_id} uploaded full backup for {date}")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Full backup error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save full backup") 