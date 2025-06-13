from google.cloud import storage
import json
from app.storage.base import StorageBackend
from app.core import get_firebase_storage_bucket
import os
from typing import Optional
import logging

class FirebaseStorageBackend(StorageBackend):
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(get_firebase_storage_bucket())

    def _blob_path(self, user_id: str, path: str) -> str:
        return f"{user_id}/{path}"

    def save_json(self, user_id: str, path: str, data: dict):
        blob = self.bucket.blob(self._blob_path(user_id, path))
        blob.upload_from_string(json.dumps(data), content_type='application/json')

    def load_json(self, user_id: str, path: str) -> dict:
        blob = self.bucket.blob(self._blob_path(user_id, path))
        if not blob.exists():
            raise FileNotFoundError(f"{path} not found for user {user_id}")
        data = blob.download_as_string()
        return json.loads(data)

    def file_exists(self, user_id: str, path: str) -> bool:
        blob = self.bucket.blob(self._blob_path(user_id, path))
        return blob.exists()

    def get_latest_full_backup_path(self, user_id: str) -> Optional[str]:
        # List all blobs in the user's full_backups folder
        prefix = f"{user_id}/full_backups/"
        blobs = list(self.bucket.list_blobs(prefix=prefix))
        if not blobs:
            return None
        # Extract date from each blob name and find the latest
        def get_date(blob):
            try:
                filename = blob.name.split('/')[-1] # get the filename
                return filename.replace('.json', '')
            except Exception:
                return ""
        blobs_with_dates = [(b, get_date(b)) for b in blobs if get_date(b)]
        if not blobs_with_dates:
            return None
        # Sort by date string (ISO format sorts correctly)
        latest_blob, _ = max(blobs_with_dates, key=lambda x: x[1])
        return latest_blob.name[len(f"{user_id}/"):] 