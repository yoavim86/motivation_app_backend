# Deploying to Google Cloud Functions

1. **Prepare your code**
   - Ensure all dependencies are in `requirements.txt`.
   - Your entrypoint should be `app.main:app` (FastAPI ASGI app).

2. **Set up Google Cloud project**
   - Enable Cloud Functions, Cloud Build, and Cloud Storage APIs.
   - Upload your `firebase_service_account.json` to a secure location.

3. **Deploy**
   ```bash
   gcloud functions deploy motivation-backend \
     --runtime python310 \
     --trigger-http \
     --entry-point app \
     --allow-unauthenticated \
     --set-env-vars FIREBASE_PROJECT_ID=your-id,FIREBASE_STORAGE_BUCKET=your-bucket,OPENAI_API_KEY=sk-... \
     --source .
   ```
   - Adjust env vars as needed.

4. **Test**
   - Use Postman or curl to hit your endpoints.

5. **Notes**
   - For production, restrict unauthenticated access and use IAM.
   - You may need to adapt the entrypoint for Cloud Run or other serverless platforms. 