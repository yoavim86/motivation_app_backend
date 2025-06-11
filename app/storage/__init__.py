from app.config import Config
from app.storage.firebase_storage import FirebaseStorageBackend

def get_storage_backend():
    if Config.STORAGE_BACKEND == 'firebase':
        return FirebaseStorageBackend()
    raise NotImplementedError('Only firebase backend is implemented') 