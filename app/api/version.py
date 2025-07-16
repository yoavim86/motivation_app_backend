from fastapi import APIRouter, Depends, HTTPException
from app.auth.firebase import verify_firebase_token
from google.cloud import storage
from app.core import get_firebase_storage_bucket
import json
import logging
import time
from typing import Optional, Dict, Any

router = APIRouter()

# In-memory cache for version data
_version_cache: Optional[Dict[str, Any]] = None
_last_cache_time: float = 0
_cache_duration: int = 4 * 60 * 60  # 4 hours in seconds

def _is_cache_valid() -> bool:
    """Check if the cache is still valid (less than 4 hours old)"""
    return _version_cache is not None and (time.time() - _last_cache_time) < _cache_duration

def _update_cache(version_data: Dict[str, Any]) -> None:
    """Update the cache with new version data"""
    global _version_cache, _last_cache_time
    _version_cache = version_data
    _last_cache_time = time.time()
    logging.info("Version cache updated")

def _get_version_from_storage() -> Dict[str, Any]:
    """Fetch version data from Firebase Storage"""
    client = storage.Client()
    bucket = client.bucket(get_firebase_storage_bucket())
    
    # Path to the version.json file in Firebase Storage
    blob_path = "admin/version_control/version.json"
    blob = bucket.blob(blob_path)
    
    if not blob.exists():
        logging.error(f"Version file not found at path: {blob_path}")
        raise HTTPException(status_code=404, detail="Version file not found")
    
    # Download and parse the JSON content
    content = blob.download_as_string()
    version_data = json.loads(content)
    logging.info("Version data fetched from Firebase Storage")
    return version_data

@router.get("/version")
async def get_version(user=Depends(verify_firebase_token)):
    """
    Get the latest app version information from Firebase Storage.
    Uses in-memory cache with 4-hour sync cycle.
    Requires user authentication.
    """
    try:
        # Check if cache is valid
        if _is_cache_valid():
            logging.info(f"Version data served from cache for user {user['uid']}")
            return _version_cache
        
        # Cache is invalid or empty, fetch from storage
        logging.info("Cache invalid or empty, fetching from Firebase Storage")
        version_data = _get_version_from_storage()
        _update_cache(version_data)
        
        logging.info(f"Version data retrieved successfully for user {user['uid']}")
        return version_data
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in version file: {e}")
        raise HTTPException(status_code=500, detail="Invalid version file format")
    except Exception as e:
        logging.error(f"Error retrieving version data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve version data") 