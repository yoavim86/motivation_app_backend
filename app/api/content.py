from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.firebase import verify_firebase_token
from firebase_admin import storage
import json
import re

router = APIRouter()

@router.get("/content/daily")
async def get_daily_content(version: int = Query(0, description="The current version of the content on the client."), user=Depends(verify_firebase_token)):
    """
    Provides the daily content to the client.

    This endpoint checks the version of the daily content file stored in
    Firebase Storage. It compares the latest version available with the
    version provided by the client.

    - If the client's version is up-to-date, it returns a status message.
    - If the client's version is outdated, it returns the new content
      along with the latest version number.
    - If no content is found in the storage, it returns a corresponding message.
    """
    try:
        bucket = storage.bucket()
        # Note: list_blobs can be inefficient for a large number of files.
        # Consider a more direct way to get the latest version if performance becomes an issue.
        blobs = bucket.list_blobs(prefix="content/")

        latest_version = 0
        latest_blob = None

        # This regex finds the version number in filenames like 'daily_content_123.json'
        version_pattern = re.compile(r"daily_content_(\d+)\.json")

        for blob in blobs:
            match = version_pattern.search(blob.name)
            if match:
                current_version = int(match.group(1))
                if current_version > latest_version:
                    latest_version = current_version
                    latest_blob = blob
        
        if latest_version == 0:
            return {"status": "no_content_found"}

        if version >= latest_version:
            return {"status": "up_to_date"}
        else:
            if latest_blob:
                content_str = latest_blob.download_as_text()
                try:
                    content_json = json.loads(content_str)
                    return {
                        "status": "updated",
                        "version": latest_version,
                        "content": content_json
                    }
                except json.JSONDecodeError:
                    raise HTTPException(status_code=500, detail="Failed to parse content file.")
            else:
                # This case should not be reached if latest_version > 0
                return {"status": "no_content_found"}

    except Exception as e:
        # Log the exception for debugging purposes
        # logger.error(f"Error fetching daily content: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") 