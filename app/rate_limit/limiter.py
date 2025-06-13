import datetime
from app.storage import get_storage_backend
from app.core import get_rate_limit_chat_messages_per_day, get_rate_limit_chat_tokens_per_request

class RateLimiter:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.storage = get_storage_backend()
        self.today = datetime.date.today().isoformat()
        self.chat_ai_path = 'chatAILimiter.json'

    def _get_usage(self):
        if self.storage.file_exists(self.user_id, self.chat_ai_path):
            data = self.storage.load_json(self.user_id, self.chat_ai_path)
            return data.get(self.today, {'messages': 0, 'tokens': 0})
        return {'messages': 0, 'tokens': 0}

    def increment(self, tokens: int):
        data = {}
        if self.storage.file_exists(self.user_id, self.chat_ai_path):
            data = self.storage.load_json(self.user_id, self.chat_ai_path)
        usage = data.get(self.today, {'messages': 0, 'tokens': 0})
        usage['messages'] += 1
        usage['tokens'] += tokens
        data[self.today] = usage
        self.storage.save_json(self.user_id, self.chat_ai_path, data)

    def check(self, tokens: int):
        usage = self._get_usage()
        if usage['messages'] >= get_rate_limit_chat_messages_per_day():
            return False, 'Daily message limit reached'
        if tokens > get_rate_limit_chat_tokens_per_request():
            return False, 'Token limit per request exceeded'
        return True, '' 