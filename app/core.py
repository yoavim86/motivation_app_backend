import os

def get_firebase_project_id():
    return os.environ.get("FIREBASE_PROJECT_ID", "insideout-57008")

def get_firebase_storage_bucket():
    return os.environ.get("FIREBASE_STORAGE_BUCKET", "insideout-57008.firebasestorage.app")

def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "")

def get_rate_limit_chat_messages_per_day():
    return int(os.environ.get("RATE_LIMIT_CHAT_MESSAGES_PER_DAY", "20"))

def get_rate_limit_chat_tokens_per_request():
    return int(os.environ.get("RATE_LIMIT_CHAT_TOKENS_PER_REQUEST", "5000"))

def get_log_level():
    return os.environ.get("LOG_LEVEL", "INFO") 