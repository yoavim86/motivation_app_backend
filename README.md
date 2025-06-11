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
- `POST /backupDateSummary`
- `POST /chatAIProxy`
- `POST /saveSettings`
- `POST /saveAccount`

---

For questions, see the code or open an issue. 