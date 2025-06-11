from google.cloud import storage
import json
from app.storage.base import StorageBackend
from app.config import Config
import os

class FirebaseStorageBackend(StorageBackend):
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(Config.FIREBASE_STORAGE_BUCKET)

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