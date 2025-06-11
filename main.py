from fastapi import FastAPI
from mangum import Mangum
from app.api import backup, chat, settings, account
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

# Include routes
app.include_router(backup.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(account.router)

# Wrap FastAPI app for Cloud Functions
handler = Mangum(app)

# Required entry point for Cloud Function
def app_function(request, context=None):
    return handler(request, context)
