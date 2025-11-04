from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_root(request):
    """
    صفحة رئيسية لـ API تعرض جميع endpoints المتاحة
    """
    api_info = {
        "message": "مرحباً بك في Tawfir API",
        "version": "1.0",
        "endpoints": {
            "admin": "/admin/",
            "cities": {
                "list": "/api/v1/cities/",
                "description": "قائمة المدن المتاحة"
            },
            "offers": {
                "list": "/api/v1/offers/",
                "detail": "/api/v1/offers/{id}/",
                "featured": "/api/v1/featured-offers/",
                "description": "العروض والخصومات"
            },
            "auth": {
                "send_otp": "/api/v1/auth/send-otp/",
                "verify_otp": "/api/v1/auth/verify-otp/",
                "description": "نظام المصادقة"
            },
            "favorites": {
                "list": "/api/v1/favorites/",
                "toggle": "/api/v1/offers/{id}/favorite/",
                "description": "المفضلات (يتطلب تسجيل دخول)"
            },
            "reviews": {
                "merchant_reviews": "/api/v1/merchants/{id}/reviews/",
                "create_review": "/api/v1/merchants/{id}/reviews/create/",
                "description": "التقييمات"
            }
        },
        "documentation": {
            "note": "استخدم Postman أو أي أداة API لاختبار هذه النقاط",
            "authentication": "استخدم Token في header: Authorization: Token YOUR_TOKEN"
        }
    }
    
    return JsonResponse(api_info, json_dumps_params={'ensure_ascii': False, 'indent': 2})
