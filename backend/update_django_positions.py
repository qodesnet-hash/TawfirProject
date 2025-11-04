"""
سكريبت Python لتحديث نموذج Django بالمواضع الجديدة
"""

# في ملف api/models.py، تحديث OnlineUsersSettings:

UPDATE_MODEL = """
# تحديث POSITION_CHOICES في نموذج OnlineUsersSettings
POSITION_CHOICES = [
    ('bottom', 'وسط الأسفل'),
    ('bottom-left', 'يسار الأسفل'),
    ('bottom-right', 'يمين الأسفل'),
    ('floating-center', 'عائم في الوسط'),
    ('floating-left', 'عائم يسار'),
    ('floating-right', 'عائم يمين'),
]
"""

print("قم بتحديث ملف api/models.py:")
print("=" * 50)
print(UPDATE_MODEL)
print("=" * 50)
print("\nثم قم بتشغيل:")
print("python manage.py makemigrations")
print("python manage.py migrate")
print("\nوأضف هذا في Django Admin:")
print("- ادخل إلى لوحة التحكم")
print("- اذهب إلى 'إعدادات المتواجدين'")
print("- ستجد المواضع الجديدة متاحة في القائمة")
