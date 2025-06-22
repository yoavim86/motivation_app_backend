from fastapi import FastAPI
from app.api import backup, chat, settings, account, content
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

# Include routes
app.include_router(backup.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(account.router)
app.include_router(content.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
