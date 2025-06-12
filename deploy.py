import os
import subprocess
from dotenv import load_dotenv
import shlex
from google.cloud import storage

# Load .env file
load_dotenv()

# Get environment variables
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REGION = 'europe-west1'
PROJECT = 'insideout-57008'
SERVICE = 'api-server'

# Compose env vars string for gcloud
env_vars = f"FIREBASE_PROJECT_ID={FIREBASE_PROJECT_ID},FIREBASE_STORAGE_BUCKET={FIREBASE_STORAGE_BUCKET},OPENAI_API_KEY={OPENAI_API_KEY}"

# 1. Deploy Cloud Run

def deploy_cloud_run():
    cmd = f"gcloud run deploy {SERVICE} " \
          f"--region={REGION} " \
          f"--project={PROJECT} " \
          f"--allow-unauthenticated " \
          f"--set-env-vars {env_vars} " \
          f"--source=."
    print("\n[Deploying Cloud Run service...]")
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)

# 2. Update Cloud Run Service Env Vars

def update_cloud_run_env():
    cmd = f"gcloud run services update {SERVICE} " \
          f"--region={REGION} " \
          f"--project={PROJECT} " \
          f"--set-env-vars {env_vars}"
    print("\n[Updating Cloud Run service environment variables...]")
    print(cmd)
    subprocess.run(shlex.split(cmd), check=True)

# 3. Test chatAIProxy endpoint using curl

def test_chat_ai_proxy(id_token):
    url = f"https://{SERVICE}-546378642469.{REGION}.run.app/chatAIProxy"
    headers = [
        f"-H", f"Authorization: Bearer {id_token}",
        f"-H", "Content-Type: application/json"
    ]
    data = '{"messages": [{"role": "user", "content": "Hello, who are you?"}]}'
    cmd = [
        "curl", "-X", "POST", url,
        *headers,
        "-d", data
    ]
    print("\n[Testing chatAIProxy endpoint...]")
    print(' '.join(cmd))
    subprocess.run(cmd)

# 4. Upload a zip file as full_backup for a user

def upload_full_backup(zip_path, user_id):
    if not os.path.isfile(zip_path):
        print(f"[Error] File not found: {zip_path}")
        return
    bucket_name = FIREBASE_STORAGE_BUCKET
    dest_blob_name = f"{user_id}/full_backup.zip"
    print(f"[Uploading {zip_path} to gs://{bucket_name}/{dest_blob_name} ...]")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)
    blob.upload_from_filename(zip_path, content_type='application/zip')
    print("[Upload complete]")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy and test Cloud Run service.")
    parser.add_argument('--deploy', action='store_true', help='Deploy Cloud Run service')
    parser.add_argument('--update-env', action='store_true', help='Update Cloud Run service env vars')
    parser.add_argument('--test-chat', metavar='ID_TOKEN', help='Test chatAIProxy endpoint with given Firebase ID token')
    parser.add_argument('--upload-backup', metavar='ZIP_PATH', help='Upload a zip file as full_backup for a user')
    parser.add_argument('--user-id', metavar='USER_ID', help='User ID for full_backup upload (required with --upload-backup)')
    args = parser.parse_args()

    if args.deploy:
        deploy_cloud_run()
    if args.update_env:
        update_cloud_run_env()
    if args.test_chat:
        test_chat_ai_proxy(args.test_chat)
    if args.upload_backup:
        if not args.user_id:
            print("[Error] --user-id is required with --upload-backup")
        else:
            upload_full_backup(args.upload_backup, args.user_id) 