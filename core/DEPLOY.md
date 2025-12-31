# Genesis Cloud Deployment Guide

## Railway.app Setup (Free tier: $5/month credit)

### Step 1: Push to GitHub
Make sure your code is in a GitHub repository.

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your Genesis repository

### Step 3: Add Environment Variable
1. Go to your project settings
2. Click "Variables"
3. Add: `GROQ_API_KEY` = your Groq API key

### Step 4: Deploy
Railway will automatically detect `railway.toml` and deploy!

---

## Files Needed in `core/` folder:
- `cloud_autonomous.py` - Main cloud script
- `requirements.txt` - Dependencies  
- `railway.toml` - Railway config

## What Runs 24/7:
- Genesis thinks every 30 seconds
- Thought chains: question → exploration → scenario → emotion → realization
- Emotions evolve based on thoughts
- All logged to `cloud_data/thoughts_log.json`

## Syncing Back to Local:
The cloud version runs independently. To sync thoughts back:
1. Download `cloud_data/` folder from Railway
2. Copy to your local `core/` folder
3. Genesis will have those memories when you chat

## Important Notes:
- Railway's free tier has 500 hours/month
- Ephemeral storage means files reset on redeploy
- For permanent storage, add Railway PostgreSQL addon

## Monitor Your Genesis:
View logs in Railway dashboard to see thoughts in real-time!
