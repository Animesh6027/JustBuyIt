# Django Ecommerce Site - Production Deployment Guide

## 🚨 **BEFORE DEPLOYMENT - CRITICAL STEPS:**

### 1. Environment Variables Setup
Create a `.env` file in your project root with the following variables:
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Generate a New Secret Key
Run this command to generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Install Production Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migration
```bash
python manage.py migrate
```

### 5. Collect Static Files
```bash
python manage.py collectstatic
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

## 🚀 **Deployment Options:**

### Option 1: Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables in Heroku dashboard
5. Deploy: `git push heroku main`

### Option 2: DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically

### Option 3: VPS (Ubuntu/DigitalOcean Droplet)
1. Set up Nginx + Gunicorn
2. Configure SSL with Let's Encrypt
3. Set up PostgreSQL database
4. Configure environment variables

## 🔒 **Security Checklist:**
- [ ] DEBUG=False in production
- [ ] Secret key is secure and not in code
- [ ] Database credentials are in environment variables
- [ ] ALLOWED_HOSTS is properly configured
- [ ] HTTPS is enabled
- [ ] Static files are served securely
- [ ] Media files are properly configured

## 📁 **File Structure for Production:**
```
ecommerce_site/
├── .env (create this with your production values)
├── requirements.txt
├── manage.py
├── staticfiles/ (created by collectstatic)
├── media/ (your uploaded files)
└── ecommerce_site/
    └── settings.py (updated for production)
```

## ⚠️ **Important Notes:**
- Never commit your `.env` file to version control
- Always use HTTPS in production
- Regularly backup your database
- Monitor your application logs
- Keep dependencies updated 