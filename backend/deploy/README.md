# Deploying the Resilient Routes API to EC2

The API is a FastAPI app served by Uvicorn, running behind nginx (which
terminates TLS). The frontend on Vercel is HTTPS, so the backend **must** be
HTTPS too — a browser will block an HTTPS page from calling `http://<ip>`.

```
Vercel (HTTPS)  ──▶  api.yourdomain.com  ──▶  nginx :443 (TLS)  ──▶  uvicorn 127.0.0.1:8000
```

## 0. Before you start: commit the datasets

The API reads `backend/datasets/connectivity_graph_{small,middle,large}/` on
every request, but those files are **not currently tracked in git**, so a fresh
clone on the server won't have them. Either commit them:

```bash
git add -f backend/datasets/connectivity_graph_*
git commit -m "Add connectivity graph datasets for deployment"
```

…or `scp` them to the instance after cloning (step 2). They total ~4.3 MB.

## 1. Launch the instance

- Ubuntu 22.04 or 24.04, t3.small or larger.
- **Security group inbound:** 22 (SSH), 80 (HTTP), 443 (HTTPS).
- Allocate an **Elastic IP** and associate it, then add a DNS **A record** for
  `api.yourdomain.com` → that IP.

## 2. Install dependencies and the app

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
# Ubuntu 24.04 ships Python 3.12; 22.04 ships 3.10 — numpy 2.3.4 needs 3.11+.
# On 22.04 install a newer Python (deadsnakes) before creating the venv.

git clone <your-repo-url> /home/ubuntu/resilient-routes
cd /home/ubuntu/resilient-routes/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# If you did NOT commit the datasets, copy them up now, e.g. from your laptop:
#   scp -r backend/datasets/connectivity_graph_* \
#       ubuntu@<elastic-ip>:/home/ubuntu/resilient-routes/backend/datasets/
```

Quick smoke test before wiring up services:

```bash
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 &
curl -s localhost:8000/api/graph/small | head -c 120 ; echo ; kill %1
```

## 3. Environment (CORS origins)

```bash
sudo mkdir -p /etc/resilient-routes
sudo cp deploy/api.env.example /etc/resilient-routes/api.env
sudo nano /etc/resilient-routes/api.env   # set FRONTEND_URL / ALLOWED_ORIGINS
```

## 4. systemd service

```bash
sudo cp deploy/resilient-routes-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now resilient-routes-api
sudo systemctl status resilient-routes-api      # should be active (running)
```

## 5. nginx + TLS

```bash
# set server_name to your real subdomain first:
sudo cp deploy/nginx-resilient-routes.conf /etc/nginx/sites-available/resilient-routes
sudo ln -s /etc/nginx/sites-available/resilient-routes /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Issue a Let's Encrypt cert (rewrites the config to add the 443 block + redirect):
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

Verify: `curl https://api.yourdomain.com/api/graph/small` returns JSON.

## 6. Point the frontend at it

In the Vercel project settings → Environment Variables:

```
NEXT_PUBLIC_API_URL = https://api.yourdomain.com
```

Redeploy the frontend so the build picks it up (it's inlined at build time).

## Updating a deployment

```bash
cd /home/ubuntu/resilient-routes && git pull
cd backend && .venv/bin/pip install -r requirements.txt   # if deps changed
sudo systemctl restart resilient-routes-api
```

## Logs / troubleshooting

```bash
journalctl -u resilient-routes-api -f     # app logs
sudo tail -f /var/log/nginx/error.log     # proxy / TLS
```

- **502 Bad Gateway** → uvicorn isn't running; check the service status/logs.
- **CORS errors in the browser** → `FRONTEND_URL` / `ALLOWED_ORIGINS` don't match
  the exact Vercel origin (scheme + host, no trailing slash).
- **`FileNotFoundError` for a pickle** → datasets missing; see step 0.
