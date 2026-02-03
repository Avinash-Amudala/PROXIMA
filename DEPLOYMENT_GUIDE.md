# 🚀 PROXIMA Deployment Guide

Complete guide for hosting PROXIMA locally and in the cloud.

---

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Git

---

## 🏠 Local Deployment

### Option 1: Quick Start (Recommended for Testing)

```bash
# 1. Start Backend (Terminal 1)
cd src
py -m uvicorn proxima.api.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# Access:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Production Build

```bash
# Build frontend for production
cd frontend
npm run build

# Serve with backend
cd ../src
py -m uvicorn proxima.api.main:app --host 0.0.0.0 --port 8000

# Frontend will be served from dist/ folder
```

---

## ☁️ Cloud Deployment

### 🎯 Recommended: Vercel (Frontend) + Railway (Backend)

**Why?**
- ✅ Free tiers available
- ✅ Automatic deployments from Git
- ✅ Easy setup (< 10 minutes)
- ✅ Great performance

#### Deploy Frontend to Vercel

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
cd frontend
vercel deploy --prod

# Follow prompts:
# - Link to Git repository (optional)
# - Set build command: npm run build
# - Set output directory: dist
# - Done! You'll get a URL like: https://proxima.vercel.app
```

#### Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
cd src
railway init

# 4. Deploy
railway up

# 5. Add environment variables (in Railway dashboard):
# - PYTHON_VERSION=3.11
# - PORT=8000

# Done! You'll get a URL like: https://proxima-backend.railway.app
```

#### Connect Frontend to Backend

```javascript
// frontend/src/api/client.js
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://proxima-backend.railway.app'  // Your Railway URL
  : 'http://localhost:8000';
```

---

### Alternative: Render (Full Stack)

**Free tier includes both frontend and backend!**

#### Deploy Backend

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Configure:
   - **Name**: proxima-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src && uvicorn proxima.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Click "Create Web Service"

#### Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect your Git repository
3. Configure:
   - **Name**: proxima-frontend
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Plan**: Free
4. Add environment variable:
   - `VITE_API_URL=https://proxima-backend.onrender.com`
5. Click "Create Static Site"

---

### Alternative: Heroku (All-in-One)

```bash
# 1. Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create proxima-app

# 4. Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# 5. Create Procfile
echo "web: cd src && uvicorn proxima.api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 6. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 7. Open app
heroku open
```

---

### Alternative: AWS (Full Control)

#### EC2 Instance Setup

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm nginx

# 4. Clone repository
git clone https://github.com/yourusername/PROXIMA.git
cd PROXIMA

# 5. Install Python dependencies
pip3 install -r requirements.txt

# 6. Install Node dependencies
cd frontend
npm install
npm run build

# 7. Configure Nginx
sudo nano /etc/nginx/sites-available/proxima
```

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/ubuntu/PROXIMA/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 8. Enable site
sudo ln -s /etc/nginx/sites-available/proxima /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 9. Start backend with PM2
npm install -g pm2
cd /home/ubuntu/PROXIMA/src
pm2 start "uvicorn proxima.api.main:app --host 0.0.0.0 --port 8000" --name proxima-backend
pm2 save
pm2 startup

# Done! Access at http://your-ec2-ip
```

---

## 🔒 Security Considerations

### Environment Variables

Never commit sensitive data! Use environment variables:

```bash
# .env (add to .gitignore)
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

### CORS Configuration

```python
# src/proxima/api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://proxima.vercel.app",  # Your frontend URL
        "http://localhost:5173"         # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring & Logging

### Add Logging

```python
# src/proxima/api/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.get("/analyze")
async def analyze():
    logger.info("Analysis endpoint called")
    # ... your code
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

---

## 🎯 Recommended Setup for Different Use Cases

| Use Case | Frontend | Backend | Cost | Setup Time |
|----------|----------|---------|------|------------|
| **Demo/Testing** | Local | Local | Free | 5 min |
| **Research Paper** | Vercel | Railway | Free | 10 min |
| **Production (Small)** | Vercel | Render | Free-$7/mo | 15 min |
| **Production (Large)** | Vercel | AWS EC2 | $10-50/mo | 1-2 hours |
| **Enterprise** | AWS CloudFront | AWS ECS | $100+/mo | 1-2 days |

---

## 🆘 Troubleshooting

### Frontend can't connect to backend

```javascript
// Check CORS settings in backend
// Update API_BASE_URL in frontend/src/api/client.js
```

### Backend crashes on startup

```bash
# Check Python version
py --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt
```

### Port already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## ✅ Deployment Checklist

- [ ] Backend runs locally
- [ ] Frontend runs locally
- [ ] Frontend can call backend API
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health check endpoint works
- [ ] Logging configured
- [ ] Domain name configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Monitoring setup (optional)

---

## 📞 Support

For deployment issues:
1. Check logs: `railway logs` or `heroku logs --tail`
2. Verify environment variables
3. Test health check endpoint
4. Check CORS configuration

**You're ready to deploy PROXIMA! 🚀**

