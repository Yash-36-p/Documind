# 🚀 DocuMind Production & Zero-Cost Deployment Guide

DocuMind is engineered to run in production or at **100% Zero Cost ($0 / month)** without requiring a credit card:

| Deployment Path | Cost | Best For | Setup Complexity |
| :--- | :--- | :--- | :--- |
| **Option 1: Render 100% Free Blueprint** | **$0.00** | Full Cloud Deployment (Web API + React SPA) | 1-Click via `render.yaml` |
| **Option 2: Vercel (Frontend) + Render (API)** | **$0.00** | Blazing-fast edge frontend + Free Docker API | 2 Clicks |
| **Option 3: Neon.tech Free PostgreSQL** | **$0.00** | Free Lifetime Cloud Postgres (No Card Needed) | 30 Seconds |
| **Option 4: Docker Compose** | Host Cost | Self-hosted VPS (DigitalOcean / AWS / Hetzner) | Terminal command |

---

## 💰 How DocuMind Runs at 100% ZERO COST ($0)

Standard enterprise setups use separate Redis brokers, PostgreSQL clusters, and dedicated Celery worker containers, which cloud platforms charge for ($7-$45/month).

**DocuMind includes built-in Zero-Cost optimizations**:
1. **In-Process Task Execution**: Setting `CELERY_TASK_ALWAYS_EAGER=true` eliminates the need for a separate Celery worker container and Redis broker. OCR, PyMuPDF, document classification, and field extraction run directly inside the free Django web service!
2. **Free Database Options**:
   - **Built-in SQLite**: Works out of the box with $0 cost and zero external accounts.
   - **Neon.tech Free Serverless PostgreSQL**: Provides 0.5 GB storage, serverless autoscaling, and free SSL with **zero credit card required forever**.
3. **Optimized Gunicorn Memory**: Configured with 1 worker and 4 threads (`--workers 1 --threads 4`), keeping total memory footprint under 250MB to comfortably fit within 512MB free tier RAM limits without crashing.

---

## ☁️ Option 1: 1-Click 100% Free Deployment on Render ($0)

DocuMind's `render.yaml` is pre-configured with `plan: free` for both services:

1. Push latest code to your GitHub:
   ```bash
   git push origin main
   ```
2. Go to **[dashboard.render.com](https://dashboard.render.com/)** and log in with GitHub.
3. Click **New +** → **Blueprint**.
4. Select your repository: **`Yash-36-p/Documind`**.
5. Render reads `render.yaml` and will display **$0 / month Free Tier**:
   - `documind-api` (Docker Web Service, `plan: free`)
   - `documind-frontend` (Static Web Service, `plan: free`)
6. Click **Apply**.
7. Render deploys both services for free!

*(Optional: To use a free PostgreSQL database with Render, sign up at [Neon.tech](https://neon.tech), create a free project, copy the connection string, and add `DATABASE_URL` in the `documind-api` Environment variables tab in Render).*

---

## ⚡ Option 2: Vercel (Frontend) + Render (Backend) ($0)

Deploying the React frontend on **Vercel** gives you global edge caching and 0-second deploy times:

1. **Deploy Frontend on Vercel**:
   - Go to [vercel.com](https://vercel.com/) and click **Add New Project**.
   - Import `Yash-36-p/Documind`.
   - Set **Root Directory** to `frontend`.
   - Framework Preset: **Vite**.
   - Add Environment Variable:
     - `VITE_API_URL` = `https://<your-documind-api>.onrender.com`
   - Click **Deploy**.

---

## 📦 Option 3: Docker Compose (Self-Hosted VPS)

Docker Compose containerizes all 5 services with persistent volumes, automatic restarts, and isolated networking:
- **`frontend`**: Nginx web gateway serving React Vite production bundle and reverse-proxying API requests
- **`backend`**: Gunicorn WSGI server running Django REST Framework with Tesseract OCR
- **`celery_worker`**: Celery worker instance processing OCR background tasks
- **`redis`**: Redis 7 message broker
- **`db`**: PostgreSQL 16 database

### Step 1: Clone Repository on your Server
```bash
git clone https://github.com/yourusername/DocuMind.git
cd DocuMind
```

### Step 2: Configure Production Environment
Copy the example environment file:
```bash
cp .env.production.example .env
```
Edit `.env` and set your secure credentials:
```bash
nano .env
```
Key variables to update:
```env
SECRET_KEY=generate-a-strong-random-50-character-string
DB_PASSWORD=your_secure_postgres_password
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Step 3: Build & Launch Containers
```bash
docker compose up -d --build
```

### Step 4: Verify Deployment
Check the status of all containers:
```bash
docker compose ps
```
Check logs:
```bash
docker compose logs -f backend
docker compose logs -f celery_worker
```

Visit your server IP or domain in your browser:
- **Web App**: `http://your-server-ip`
- **Swagger API Docs**: `http://your-server-ip/api/docs/`

---

## 🔒 Adding SSL / HTTPS with Let's Encrypt (Nginx Reverse Proxy)

To secure your domain with HTTPS:

1. Install Certbot on your host:
   ```bash
   sudo apt update && sudo apt install -y certbot python3-certbot-nginx
   ```
2. In `docker-compose.yml`, map the frontend to an internal port (e.g. `127.0.0.1:3000:80`).
3. Setup an Nginx reverse proxy on the host machine:
   ```nginx
   server {
       server_name yourdomain.com www.yourdomain.com;
       client_max_body_size 50M;

       location / {
           proxy_pass http://127.0.0.1:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
4. Issue free SSL certificate:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## ☁️ Option 2: 1-Click Deployment on Render

DocuMind includes a `render.yaml` infrastructure blueprint that automatically provisions PostgreSQL, Redis, Django API, Celery worker, and React static frontend.

1. Push your DocuMind repository to **GitHub** or **GitLab**.
2. Log in to [Render.com](https://render.com/).
3. Click **New** -> **Blueprint**.
4. Connect your DocuMind repository.
5. Render will automatically detect `render.yaml` and provision:
   - `documind-postgres` (Managed Database)
   - `documind-redis` (Managed Redis)
   - `documind-api` (Docker Web Service with Tesseract OCR)
   - `documind-celery-worker` (Docker Background Worker)
   - `documind-frontend` (Static Web Service)
6. Click **Apply**. Render will build and deploy the entire platform.

---

## 🚆 Option 3: Deploy on Railway

1. Push your repository to **GitHub**.
2. Log in to [Railway.app](https://railway.app/) and create a **New Project**.
3. Add a **PostgreSQL** database service and a **Redis** service from the Railway Marketplace.
4. Deploy the backend:
   - Select **Deploy from GitHub repo**.
   - Point the root directory to `backend/`.
   - Set environment variables:
     - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
     - `CELERY_BROKER_URL`: `${{Redis.REDIS_URL}}`
     - `CELERY_RESULT_BACKEND`: `${{Redis.REDIS_URL}}`
     - `SECRET_KEY`: `<random-secret>`
     - `DEBUG`: `False`
     - `ALLOWED_HOSTS`: `*`
     - `RUN_MIGRATIONS`: `true`
     - `SEED_DATA`: `true`
5. Deploy the frontend:
   - Add another service from the same repo.
   - Point to `frontend/`.
   - Build command: `npm install && npm run build`.

---

## 🖥️ Option 4: Traditional Ubuntu Linux Server (Bare Metal / VPS)

### 1. Install System Packages
```bash
sudo apt update && sudo apt install -y \
    python3-pip python3-venv \
    tesseract-ocr tesseract-ocr-eng libtesseract-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx
```

### 2. Configure PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE documind;
CREATE USER documind WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE documind TO documind;
\q
```

### 3. Setup Backend & Virtual Environment
```bash
cd /var/www/DocuMind/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations and static collection
export DB_NAME=documind DB_USER=documind DB_PASSWORD=secure_password
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

### 4. Create Systemd Service for Gunicorn
Create `/etc/systemd/system/documind.service`:
```ini
[Unit]
Description=DocuMind Gunicorn Daemon
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/DocuMind/backend
ExecStart=/var/www/DocuMind/backend/venv/bin/gunicorn config.wsgi:application \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```
Start and enable Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now documind
```

### 5. Create Systemd Service for Celery Worker
Create `/etc/systemd/system/documind-celery.service`:
```ini
[Unit]
Description=DocuMind Celery Worker
After=network.target redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/DocuMind/backend
ExecStart=/var/www/DocuMind/backend/venv/bin/celery -A config worker -l INFO --concurrency=2
Restart=always

[Install]
WantedBy=multi-user.target
```
Start and enable Celery:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now documind-celery
```

### 6. Build Frontend & Setup Nginx
```bash
cd /var/www/DocuMind/frontend
npm install
npm run build
```
Configure Nginx at `/etc/nginx/sites-available/documind`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    client_max_body_size 50M;

    location / {
        root /var/www/DocuMind/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /var/www/DocuMind/backend/media/;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/documind /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

---

## 🛠️ Maintenance & Management Commands

### Database Backup
```bash
# Docker Compose
docker exec -t documind-db pg_dump -U documind documind > backup_$(date +%Y%m%d).sql

# Native
pg_dump -U documind documind > backup_$(date +%Y%m%d).sql
```

### Re-seeding or Creating Superuser
```bash
# Docker Compose
docker compose exec backend python manage.py createsuperuser

# Native
cd backend && venv/bin/python manage.py createsuperuser
```
