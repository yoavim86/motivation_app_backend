from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    def save_json(self, user_id: str, path: str, data: dict): ...

    @abstractmethod
    def load_json(self, user_id: str, path: str) -> dict: ...

    @abstractmethod
    def file_exists(self, user_id: str, path: str) -> bool: ... 