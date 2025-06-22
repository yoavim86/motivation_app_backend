from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile, File, Form
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
from app.core import get_backup_limit
import logging
import datetime
import json
from datetime import datetime, timezone

router = APIRouter()

def update_backup_limiter(storage, user_id, backup_date, backup_limit):
    limiter_path = 'backupLimiter.json'
    data = {"date": backup_date, "counter": 1}
    if storage.file_exists(user_id, limiter_path):
        existing = storage.load_json(user_id, limiter_path)
        if existing.get("date") == backup_date:
            data["counter"] = existing.get("counter", 1) + 1
        # else: new day, counter stays 1
    storage.save_json(user_id, limiter_path, data)
    # Return True if allowed, False if limit exceeded
    return data["counter"] <= backup_limit, data

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
    request: Request,
    user=Depends(verify_firebase_token)
):
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        body = await request.json()
        exported_at = body.get("exportedAt")
        backup_date = None
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if exported_at:
            try:
                dt = datetime.fromisoformat(exported_at)
                backup_date = dt.strftime("%Y-%m-%d")
                if backup_date != today_str:
                    logging.warning(f"Backup date {backup_date} (from exportedAt) does not match today {today_str} (UTC) for user {user_id}")
            except Exception as e:
                logging.warning(f"Invalid exportedAt format: {exported_at} for user {user_id}: {e}")
                backup_date = today_str
        else:
            logging.warning(f"No exportedAt field in backup for user {user_id}")
            backup_date = today_str

        backup_limit = get_backup_limit()
        allowed, limiter_data = update_backup_limiter(storage, user_id, backup_date, backup_limit)
        logging.info(f"Backup limiter for user {user_id}: {limiter_data}")
        if not allowed:
            raise HTTPException(status_code=429, detail=f"Daily backup limit ({backup_limit}) reached for {backup_date}")

        path = f"full_backups/{backup_date}.json"
        storage.save_json(user_id, path, body)
        logging.info(f"User {user_id} uploaded full backup for {backup_date}")
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Full backup error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save full backup")

@router.get("/lastFullBackup")
async def get_last_full_backup(user=Depends(verify_firebase_token)):
    user_id = user['uid']
    storage = get_storage_backend()
    try:
        path = storage.get_latest_full_backup_path(user_id)
        if not path:
            raise HTTPException(status_code=404, detail="No backup found")
        logging.info(f"Getting last full backup for user {user_id} at {path}")
        data = storage.load_json(user_id, path)
        return data
    except Exception as e:
        logging.error(f"Get last full backup error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve last full backup") 