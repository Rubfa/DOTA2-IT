# Deployment Guide

This repository runs with `DOTA2SS.settings`. The `DjangoProject/settings.py` file at the root is not the active settings module for `manage.py`.

## 1. Push Code To Git

Commit your code and push it to your own repository first:

```powershell
git add .
git commit -m "Prepare project for deployment"
git push origin main
```

## 2. Prepare The Server

The simplest first deployment is:

- Linux server
- Python virtual environment
- SQLite database
- `waitress` as the app server
- `nginx` as the reverse proxy

Install the base packages:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv nginx
```

Clone the project and install Python packages:

```bash
cd /var/www
sudo git clone https://github.com/your-name/your-repo.git dota2ss
sudo chown -R $USER:$USER /var/www/dota2ss
cd /var/www/dota2ss
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Create a deployment env file from the example:

```bash
cp .env.example .env.production
```

Edit `.env.production` and set at least:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`

Load the variables into the current shell:

```bash
set -a
source .env.production
set +a
```

## 4. Prepare Django

Run migrations, collect static files, and create an admin account:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Test the production server directly:

```bash
python serve.py
```

If it starts correctly, open `http://server-ip:8000`.

## 5. Run With systemd

Create `/etc/systemd/system/dota2ss.service`:

```ini
[Unit]
Description=DOTA2SS Django service
After=network.target

[Service]
User=your-user
Group=www-data
WorkingDirectory=/var/www/dota2ss
EnvironmentFile=/var/www/dota2ss/.env.production
ExecStart=/var/www/dota2ss/.venv/bin/python /var/www/dota2ss/serve.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dota2ss
sudo systemctl start dota2ss
sudo systemctl status dota2ss
```

## 6. Configure nginx

Create `/etc/nginx/sites-available/dota2ss`:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location /static/ {
        alias /var/www/dota2ss/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and reload nginx:

```bash
sudo ln -s /etc/nginx/sites-available/dota2ss /etc/nginx/sites-enabled/dota2ss
sudo nginx -t
sudo systemctl reload nginx
```

## 7. HTTPS

After the domain points to the server, add HTTPS:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

If HTTPS is enabled, keep `DJANGO_ENABLE_HTTPS=True` in `.env.production`.

## 8. Update The Site Later

For each new deployment:

```bash
cd /var/www/dota2ss
git pull origin main
source .venv/bin/activate
set -a
source .env.production
set +a
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart dota2ss
```

## 9. If You Deploy On A Git-Based Platform

If you use a platform such as Render, Railway, or a similar panel:

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start command: `python serve.py`
- Environment variables: use the values from `.env.example`

If the platform does not provide persistent disk storage, do not keep using SQLite long-term. Move the database to PostgreSQL first.
