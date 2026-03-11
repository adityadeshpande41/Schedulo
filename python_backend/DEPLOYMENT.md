# Deployment Guide - Render.com

## Overview

This guide covers deploying Schedulo to Render's free tier, which includes:
- Free PostgreSQL database (90 days, then $7/month)
- Free web service (spins down after 15 min inactivity)
- Automatic HTTPS
- Auto-deploy from GitHub

## Prerequisites

1. GitHub account
2. Render account (free): https://render.com
3. Push your code to GitHub

## Step 1: Prepare Your Repository

Ensure these files are in your `python_backend/` directory:
- ✅ `requirements.txt`
- ✅ `main.py`
- ✅ `render.yaml` (blueprint)
- ✅ `alembic.ini` (migrations)

## Step 2: Create PostgreSQL Database

### Option A: Using Render Blueprint (Recommended)

1. Go to Render Dashboard
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository
5. Render will detect `render.yaml` and create:
   - PostgreSQL database
   - Web service
   - Environment variables

### Option B: Manual Setup

1. **Create Database:**
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Name: `schedulo-db`
   - Database: `schedulo`
   - Plan: Free
   - Region: Oregon (or closest to you)
   - Click "Create Database"

2. **Get Connection String:**
   - Once created, copy the "Internal Database URL"
   - Format: `postgresql://user:password@host:port/database`

## Step 3: Create Web Service

1. **New Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

2. **Configure Service:**
   ```
   Name: schedulo-api
   Region: Oregon
   Branch: main
   Root Directory: python_backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

3. **Environment Variables:**
   Add these in the "Environment" tab:
   ```
   API_V1_STR=/api
   PROJECT_NAME=Schedulo
   DATABASE_URL=<paste your database URL>
   AGENT_TIMEOUT=30
   LOOKBACK_DAYS=90
   DEBUG=false
   CORS_ORIGINS=https://your-frontend-url.onrender.com,http://localhost:5000
   ```

4. **Click "Create Web Service"**

## Step 4: Initialize Database

Once deployed, run migrations:

### Option A: Using Render Shell

1. Go to your web service dashboard
2. Click "Shell" tab
3. Run:
   ```bash
   python cli.py init
   python cli.py seed
   ```

### Option B: Using Build Hook

Add to `render.yaml`:
```yaml
services:
  - type: web
    name: schedulo-api
    buildCommand: |
      pip install -r requirements.txt
      python cli.py init
      python cli.py seed
```

## Step 5: Deploy Frontend

### Option 1: Render Static Site

1. **New Static Site:**
   - Click "New" → "Static Site"
   - Connect repository
   - Configure:
     ```
     Name: schedulo-frontend
     Root Directory: (leave empty or "client")
     Build Command: npm install && npm run build
     Publish Directory: dist/public
     ```

2. **Environment Variables:**
   ```
   VITE_API_URL=https://schedulo-api.onrender.com/api
   VITE_DEFAULT_USER_ID=u1
   ```

### Option 2: Vercel/Netlify

Deploy frontend separately to Vercel or Netlify:

**Vercel:**
```bash
npm install -g vercel
cd client
vercel --prod
```

**Netlify:**
```bash
npm install -g netlify-cli
cd client
npm run build
netlify deploy --prod --dir=dist/public
```

## Step 6: Update CORS

After frontend is deployed, update backend CORS:

1. Go to backend service → Environment
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-frontend.onrender.com,https://your-frontend.vercel.app
   ```
3. Save and redeploy

## Database Management

### Run Migrations

```bash
# In Render Shell or locally
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Seed Data

```bash
python cli.py seed
```

### Reset Database

```bash
python cli.py reset
```

### Backup Database

Render provides automatic daily backups on paid plans. For free tier:

```bash
# Export from Render Shell
pg_dump $DATABASE_URL > backup.sql

# Or use Render's backup feature (manual)
```

## Monitoring

### View Logs

1. Go to service dashboard
2. Click "Logs" tab
3. Monitor real-time logs

### Health Check

Your API will be available at:
```
https://schedulo-api.onrender.com/
https://schedulo-api.onrender.com/api/health
https://schedulo-api.onrender.com/docs
```

## Free Tier Limitations

⚠️ **Important:**

1. **Web Service:**
   - Spins down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - 750 hours/month free (enough for 1 service)

2. **Database:**
   - Free for 90 days
   - Then $7/month
   - 1GB storage
   - Automatic backups on paid plans only

3. **Workarounds:**
   - Use a cron job to ping your API every 14 minutes
   - Upgrade to paid plan ($7/month) for always-on

## Troubleshooting

### Database Connection Errors

```python
# Check DATABASE_URL format
postgresql://user:password@host:port/database

# Ensure psycopg2-binary is installed
pip install psycopg2-binary
```

### Build Failures

```bash
# Check Python version
python --version  # Should be 3.8+

# Check requirements.txt
pip install -r requirements.txt
```

### CORS Errors

```python
# Verify CORS_ORIGINS includes your frontend URL
CORS_ORIGINS=https://your-frontend.onrender.com

# Check settings in core/config.py
```

### Database Not Initialized

```bash
# Run in Render Shell
python cli.py init
python cli.py seed
```

## Scaling

When you're ready to scale:

1. **Upgrade Web Service:**
   - Starter: $7/month (always-on)
   - Standard: $25/month (more resources)

2. **Upgrade Database:**
   - Starter: $7/month (1GB)
   - Standard: $20/month (10GB)

3. **Add Redis:**
   - For caching and sessions
   - $10/month

## CI/CD

Render auto-deploys on git push:

1. Push to `main` branch
2. Render detects changes
3. Runs build command
4. Deploys automatically

### Manual Deploy

```bash
# Trigger manual deploy from dashboard
# Or use Render API
curl -X POST https://api.render.com/deploy/srv-xxx?key=xxx
```

## Environment-Specific Configs

### Development
```bash
DATABASE_URL=postgresql://localhost/schedulo_dev
DEBUG=true
CORS_ORIGINS=http://localhost:5000
```

### Production (Render)
```bash
DATABASE_URL=<render-provided>
DEBUG=false
CORS_ORIGINS=https://your-frontend.onrender.com
```

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Schedulo Issues: GitHub Issues

## Cost Estimate

**Free Tier:**
- Web Service: Free (with spin-down)
- Database: Free for 90 days
- Total: $0/month (first 90 days)

**After 90 Days:**
- Web Service: Free or $7/month (always-on)
- Database: $7/month
- Total: $7-14/month

**Production Ready:**
- Web Service: $25/month
- Database: $20/month
- Redis: $10/month
- Total: $55/month
