# Deploying as Monolithic Server/Pod

## 1. Local/VM Deployment

1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (see `.env.example`).
4. Run the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 2. Docker Deployment

1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY . .
   RUN pip install --no-cache-dir -r requirements.txt
   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
2. Build and run:
   ```bash
   docker build -t motivation-backend .
   docker run -d -p 8000:8000 --env-file .env motivation-backend
   ```

## 3. Kubernetes/Pod
- Use the Docker image above in your deployment YAML.
- Mount your `.env` and `firebase_service_account.json` as secrets/volumes.

---

For multi-project, duplicate the repo or use different env files per deployment. 