# Deployment Guide for Render.com

## Prerequisites
- GitHub account with your code pushed
- Render account (free at render.com)
- PostgreSQL database (included in Render)

## Step-by-Step Deployment Guide

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2. Create Account on Render
- Go to https://render.com
- Sign up with GitHub (recommended for easy integration)

### 3. Deploy Using render.yaml
The `render.yaml` file in your repository automatically configures:
- Web service (Django app with Gunicorn)
- PostgreSQL database
- Environment variables
- Build and start commands

### 4. Connect GitHub Repository to Render
1. Go to Render Dashboard
2. Click **New +** > **Web Service**
3. Select **Deploy an existing repository**
4. Search and select your `app_backend` repository
5. Render will automatically detect `render.yaml`

### 5. Configure Environment Variables
Render will set these automatically from `render.yaml`:
- `SECRET_KEY` - Randomly generated
- `DATABASE_URL` - Connection string
- `DJANGO_SETTINGS_MODULE` - config.settings.production
- `ALLOWED_HOSTS` - *.onrender.com

You can add additional environment variables in Render Dashboard:
- `CORS_ALLOWED_ORIGINS` - Your frontend URLs

### 6. Manual Deployment (Alternative)
If automatic deployment doesn't work:

1. Create new **Web Service** on Render
2. Use GitHub repository
3. Settings:
   - **Name**: fypproject-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
   - **Start Command**: `gunicorn config.wsgi`
   - **Plan**: Free (or paid for better performance)

4. Create PostgreSQL Database:
   - Click **New +** > **PostgreSQL**
   - Name: fypproject_db
   - Region: Choose closest to users
   - Plan: Free
   - Connect to your web service

### 7. First Deployment
After connecting your repository:
1. Wait for initial build (5-15 minutes)
2. Check deployment logs for errors
3. Your app will be available at: `https://your-service-name.onrender.com`

## Important Notes

### Free Tier Limitations:
- **Spins down** after 15 minutes of inactivity
- Takes time to wake up (cold start)
- Limited resources (512MB RAM, shared CPU)

### Fix Cold Start Issue:
Add a cron job or monitoring service to ping your API every 14 minutes:
1. Use external services like UptimeRobot (free)
2. Set URL: `https://your-service-name.onrender.com/`
3. Ping interval: 14 minutes

### Static Files:
- Configured with WhiteNoise for serving static files
- No need to manually upload

### Database:
- Free PostgreSQL included
- Automatic backups available
- Keep data even if service stops

## Common Issues & Solutions

### Issue: Build fails
- Check logs in Render Dashboard
- Ensure all dependencies in requirements.txt
- Verify migrations run correctly

### Issue: "502 Bad Gateway"
- Check application logs
- Verify DATABASE_URL is set
- Ensure gunicorn is running

### Issue: CORS errors on frontend
- Update `CORS_ALLOWED_ORIGINS` in environment variables
- Add your frontend URL

### Issue: Static files not loading
- Run: `python manage.py collectstatic` locally
- Verify `STATIC_ROOT` configuration

## Monitoring & Logs
- View logs in Render Dashboard under "Logs"
- Check for errors and warnings
- Monitor resource usage under "Metrics"

## Upgrading to Paid Plan
- Click service > Settings > Plan
- Options: Starter ($7/month), Standard ($12/month), etc.
- Kept alive 24/7 on paid plans

## Support
- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- PostgreSQL Guide: https://render.com/docs/databases

---
Good luck with your deployment! 🚀
