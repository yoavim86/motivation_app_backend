from abc import ABC, abstractmethod
from app.config import Config
import openai

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list, **kwargs) -> dict:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY

    def chat(self, messages: list, **kwargs) -> dict:
        response = openai.ChatCompletion.create(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 1000),
        )
        return response

def get_llm_provider():
    # In the future, swap based on config
    return OpenAIProvider() 