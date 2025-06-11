from fastapi import FastAPI
from app.api import backup, chat, settings, account
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(backup.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(account.router) 