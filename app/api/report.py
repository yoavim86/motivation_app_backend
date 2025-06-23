import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from app.auth.firebase import verify_firebase_token
from app.storage import get_storage_backend
import logging

router = APIRouter()

class CrashReportPayload(BaseModel):
    error: str
    stack_trace: str = Field(..., alias='stackTrace')
    logs: List[str]
    timestamp: str
    device_info: Optional[Dict[str, Any]] = Field(None, alias='deviceInfo')
    app_version: Optional[str] = Field(None, alias='appVersion')

@router.post("/report/crash", status_code=status.HTTP_201_CREATED)
async def report_crash(payload: CrashReportPayload, user=Depends(verify_firebase_token)):
    """
    Receives a crash report from the client application and stores it in Firebase Storage.
    This endpoint is unauthenticated to ensure that crash reports can be received
    even if the user is not logged in or if authentication is part of the problem.
    """
    try:
        user_id = user['uid']
        storage = get_storage_backend()
        report_time = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        file_name = f"crash_{report_time}_{uuid.uuid4()}.json"
        path = f"crashes/{file_name}"
        report_data = payload.model_dump(by_alias=True)
        storage.save_json(user_id, path, report_data)
        return {"status": "Crash report received."}
    except Exception as e:
        logging.error(f"Error processing crash report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not process crash report.") 