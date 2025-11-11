#!/bin/bash
# Script للـ Deploy على DigitalOcean

echo "=========================================="
echo "🌊 Deploy to DigitalOcean"
echo "=========================================="

echo ""
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo ""
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo ""
echo "✅ Checking service status..."
sudo systemctl status gunicorn --no-pager

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
