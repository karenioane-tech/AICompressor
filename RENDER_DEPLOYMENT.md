# Deployment Guide: Render

## Prerequisites
- GitHub repository with your code pushed (✓ You've done this!)
- Render account (https://render.com)

## Setup Steps

### 1. Connect GitHub to Render
1. Log in to [Render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"** and authorize GitHub
4. Choose your `AI Compressor` repository

### 2. Configure the Web Service
Fill in the following settings:

- **Name:** `ai-compressor` (or your preferred name)
- **Environment:** Python 3
- **Region:** Choose closest to you
- **Branch:** main
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

### 3. Set Environment Variables
Click **"Advanced"** and add these environment variables:

```
FLASK_ENV=production
UPLOAD_FOLDER=/tmp/uploads
COMPRESSED_FOLDER=/tmp/compressed
FILE_RETENTION_SECONDS=1800
MAX_UPLOAD_SIZE=52428800
```

**Important Notes:**
- Use `/tmp/` for upload/compressed folders (Render's file system is ephemeral)
- Set `FILE_RETENTION_SECONDS` to 1800 (30 min) since files won't persist between deploys
- Keep `MAX_UPLOAD_SIZE=52428800` (50 MB) for free tier, or adjust as needed

### 4. Deploy
1. Click **"Create Web Service"**
2. Render will automatically build and deploy your app
3. Monitor the deployment in the logs
4. Once deployed, visit your app at `https://your-service-name.onrender.com`

## Important: File Storage on Render

⚠️ **Render's file system is ephemeral** — files are deleted when the service restarts.

Your app currently saves files to disk. For production, consider:
- **Option A (Temporary):** Use `/tmp/` folders (files persist only during a session)
- **Option B (Recommended):** Use cloud storage (AWS S3, Google Cloud Storage, etc.)

If you want to use cloud storage, you'll need to:
1. Update your compression modules to upload to S3/cloud
2. Add cloud storage credentials as environment variables
3. Install required packages (e.g., `boto3` for AWS S3)

## Troubleshooting

**Deployment fails:**
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`

**Files not found:**
- Verify you're using the correct folder paths from environment variables
- Remember files are temporary on Render's file system

**App crashes:**
- Check live logs in Render dashboard
- Verify environment variables are set correctly

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

The `.env` file will load your local configuration automatically.
