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
uvicorn main:app --reload
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

### `POST /fullBackup`
**Request:**
- JSON body containing the full backup data. The JSON should include an `exportedAt` field (ISO datetime string), e.g.:

```json
{
  "exportedAt": "2025-06-12T14:38:40.447098",
  "data": { "your": "backup data here" }
}
```

- The backend will use the date from `exportedAt` (if present and valid) to name the backup file as `full_backups/YYYY-MM-DD.json`. If missing or invalid, it will use today's date (UTC) and log a warning. If the date does not match today, a warning is logged but the request still succeeds.

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/fullBackup" \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "exportedAt": "2025-06-12T14:38:40.447098",
    "data": { "your": "backup data here" }
  }'
```

---

## Deploy and Test with deploy.py

You can use the `deploy.py` script to deploy, update environment variables, and test your Cloud Run service:

```bash
# Deploy Cloud Run service
python deploy.py --deploy

# Update environment variables on Cloud Run service
python deploy.py --update-env

# Test chatAIProxy endpoint (replace <ID_TOKEN> with a real Firebase ID token)
python deploy.py --test-chat <ID_TOKEN>

# Upload a zip file as a full_backup for a user (replace <ZIP_PATH> and <USER_ID>)
python deploy.py --upload-backup <ZIP_PATH> --user-id <USER_ID>
```

- The `--upload-backup` option uploads the specified zip file to the user's folder in your Firebase Storage bucket as `full_backup.zip`.

---

For questions, see the code or open an issue. 