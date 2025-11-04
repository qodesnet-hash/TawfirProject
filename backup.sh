#!/bin/bash
# Backup Script for TawfirProject
# يقوم بإنشاء نسخة احتياطية مع التاريخ والوقت

# تعيين المتغيرات
PROJECT_DIR="."
BACKUP_DIR="../TawfirProject_Backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="TawfirProject_backup_$DATE"

# إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
mkdir -p "$BACKUP_DIR"

echo "🔄 بدء النسخ الاحتياطي..."

# 1. حفظ حالة Git الحالية
echo "📝 حفظ حالة Git..."
git add .
git commit -m "Auto-backup: $DATE" --allow-empty

# 2. إنشاء Git Bundle (نسخة كاملة من المستودع)
echo "📦 إنشاء Git Bundle..."
git bundle create "$BACKUP_DIR/${BACKUP_NAME}.bundle" --all

# 3. إنشاء ZIP archive (اختياري - للملفات بدون .git)
echo "🗜️ إنشاء ملف مضغوط..."
zip -r "$BACKUP_DIR/${BACKUP_NAME}.zip" . \
    -x "*.git*" \
    -x "*node_modules*" \
    -x "*venv*" \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*www*" \
    -x "*.angular*" \
    -x "*dist*"

# 4. حفظ معلومات النسخة
echo "📋 حفظ معلومات النسخة..."
cat > "$BACKUP_DIR/${BACKUP_NAME}_info.txt" << EOF
===========================================
TawfirProject Backup Information
===========================================
Date: $(date)
Git Branch: $(git branch --show-current)
Last Commit: $(git log -1 --oneline)
Total Commits: $(git rev-list --count HEAD)
Modified Files: $(git status --porcelain | wc -l)
===========================================

Recent Commits:
$(git log --oneline -10)

===========================================
Modified Files:
$(git status --short)
EOF

# 5. تنظيف النسخ القديمة (الاحتفاظ بآخر 10 نسخ فقط)
echo "🧹 تنظيف النسخ القديمة..."
ls -t "$BACKUP_DIR"/*.zip 2>/dev/null | tail -n +11 | xargs -r rm
ls -t "$BACKUP_DIR"/*.bundle 2>/dev/null | tail -n +11 | xargs -r rm

echo "✅ تم إنشاء النسخة الاحتياطية بنجاح!"
echo "📍 موقع النسخة: $BACKUP_DIR/$BACKUP_NAME"
echo ""
echo "📊 معلومات النسخة:"
echo "   - Git Bundle: ${BACKUP_NAME}.bundle"
echo "   - ZIP Archive: ${BACKUP_NAME}.zip"
echo "   - Info File: ${BACKUP_NAME}_info.txt"

# عرض حجم النسخة
if [ -f "$BACKUP_DIR/${BACKUP_NAME}.zip" ]; then
    SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.zip" | cut -f1)
    echo "   - حجم النسخة: $SIZE"
fi
