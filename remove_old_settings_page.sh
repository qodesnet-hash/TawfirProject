#!/bin/bash

# حذف ملفات صفحة الإعدادات القديمة
echo "حذف صفحة الإعدادات القديمة..."
rm -rf tawfir_app/src/app/pages/online-users-settings/

echo "تم حذف صفحة الإعدادات القديمة بنجاح!"
echo "الآن يتم التحكم من Django Admin فقط"
