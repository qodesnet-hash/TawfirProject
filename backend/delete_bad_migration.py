import os

# حذف migration الخاطئ
migration_path = "api/migrations/0002_update_position_choices.py"

if os.path.exists(migration_path):
    os.remove(migration_path)
    print(f"✅ تم حذف الملف الخاطئ: {migration_path}")
else:
    print(f"❌ الملف غير موجود: {migration_path}")

print("\n✅ الآن يمكنك تشغيل:")
print("python manage.py migrate")
print("python manage.py runserver")
