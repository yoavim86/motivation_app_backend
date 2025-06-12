import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status, Request, Depends
from app.core import get_firebase_project_id, get_firebase_storage_bucket
import os

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(os.getcwd(), 'firebase_service_account.json'))
    firebase_admin.initialize_app(cred, {
        'projectId': get_firebase_project_id(),
        'storageBucket': get_firebase_storage_bucket()
    })

def verify_firebase_token(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing or invalid Authorization header')
    id_token = auth_header.split(' ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            'uid': decoded_token['uid'],
            'claims': decoded_token.get('claims', {}),
            'token': decoded_token
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Firebase ID token') 