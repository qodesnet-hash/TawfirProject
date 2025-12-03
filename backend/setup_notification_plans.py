"""
سكربت لإنشاء الباقات الافتراضية للإشعارات
قم بتشغيله بعد عمل makemigrations و migrate

python manage.py shell < setup_notification_plans.py
"""

from api.models_push_notifications import NotificationPlan

# حذف الباقات القديمة إن وجدت
NotificationPlan.objects.all().delete()

# إنشاء الباقات الجديدة
plans = [
    {
        'name': 'باقة المبتدئ',
        'scope': 'city',
        'notifications_count': 3,
        'price': 1000,
        'discount_percentage': 0,
        'features': 'إشعارات لمدينتك فقط\nمناسب للتجربة\nسهل وسريع',
        'is_popular': False,
        'is_active': True,
        'order': 1,
    },
    {
        'name': 'باقة الاحترافي',
        'scope': 'city',
        'notifications_count': 10,
        'price': 2500,
        'discount_percentage': 17,
        'features': 'إشعارات لمدينتك فقط\nوفر 17% على السعر\nالأفضل للتجار النشطين',
        'is_popular': True,
        'is_active': True,
        'order': 2,
    },
    {
        'name': 'باقة الشامل',
        'scope': 'all',
        'notifications_count': 5,
        'price': 5000,
        'discount_percentage': 0,
        'features': 'إشعارات لكل المستخدمين\nوصول لكل اليمن\nللحملات الكبيرة',
        'is_popular': False,
        'is_active': True,
        'order': 3,
    },
]

for plan_data in plans:
    plan = NotificationPlan.objects.create(**plan_data)
    print(f'✅ تم إنشاء: {plan.name}')

print(f'\n✅ تم إنشاء {len(plans)} باقة بنجاح!')
