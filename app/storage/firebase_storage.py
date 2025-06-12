from google.cloud import storage
import json
from app.storage.base import StorageBackend
from app.core import get_firebase_storage_bucket
import os
from typing import Optional

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
        # Find the latest by date in filename (assuming YYYY-MM-DD.json)
        def extract_date(blob):
            import re
            match = re.search(r'(\\d{4}-\\d{2}-\\d{2})\\.json$', blob.name)
            return match.group(1) if match else ''
        blobs = [b for b in blobs if extract_date(b)]
        if not blobs:
            return None
        latest_blob = max(blobs, key=lambda b: extract_date(b))
        return latest_blob.name[len(f"{user_id}/"):] 