from app.core import get_firebase_storage_bucket
from app.storage.firebase_storage import FirebaseStorageBackend

def get_storage_backend():
    # Only firebase backend is implemented, but this is now config-agnostic
    return FirebaseStorageBackend() 