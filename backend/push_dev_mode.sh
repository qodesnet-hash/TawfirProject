#!/bin/bash
# Script لرفع تعديلات Dev Mode للـ Backend

echo "=========================================="
echo "🚀 رفع تعديلات Dev Mode Login"
echo "=========================================="

cd backend

echo ""
echo "📝 Git Status..."
git status

echo ""
echo "➕ Adding changes..."
git add users/views_gmail_auth.py

echo ""
echo "💬 Committing..."
git commit -m "feat: Add dev_mode support for localhost Google Sign-In

- Added dev_mode parameter to GoogleAuthView
- Skip Google token verification when dev_mode=True and DEBUG=True
- Allows testing authentication in local development
- Production (DEBUG=False) still requires real Google tokens
- Security: Only works in DEBUG mode"

echo ""
echo "⬆️ Pushing to GitHub..."
git push origin main

echo ""
echo "=========================================="
echo "✅ تم رفع التعديلات بنجاح!"
echo "=========================================="
