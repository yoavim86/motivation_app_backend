# Motivation Backend (Firebase + FastAPI)

## Features
- Firebase Auth integration (Google, email, phone)
- Modular storage (Firebase Cloud Storage)
- Per-user data isolation
- Pluggable LLM provider for chat proxy (default: OpenAI)
- Rate limiting, logging, and audit
- Ready for Cloud Functions or monolithic deployment

## Setup
1. Clone this repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Firebase service account key as `firebase_service_account.json` in the root directory.
4. Configure environment variables (see `.env.example`).

## Running Locally
```bash
uvicorn app.main:app --reload
```

## Deployment
- See `deploy/cloud_function_guide.md` and `deploy/monolith_guide.md` for deployment instructions.

## API Endpoints

### `POST /backupDateSummary`
**Request JSON:**
```json
{
  "date": "2024-06-10",
  "data_json": { "summary": "Your summary data here" }
}
```

### `POST /chatAIProxy`
**Request JSON:**
```json
{
  "messages": [
    { "role": "user", "content": "Hello, who are you?" },
    { "role": "assistant", "content": "I am an AI assistant." }
  ]
}
```

### `POST /saveSettings`
**Request JSON:**
```json
{
  "settings_file": { "theme": "dark", "notifications": true }
}
```

### `POST /saveAccount`
**Request JSON:**
```json
{
  "account_json": { "email": "user@example.com", "name": "User Name" }
}
```

---

For questions, see the code or open an issue. 