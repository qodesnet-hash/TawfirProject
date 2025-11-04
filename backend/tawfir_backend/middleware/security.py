"""
Security Middleware for Tawfir App
Middleware أمني لتطبيق توفير
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings

logger = logging.getLogger('django.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    إضافة Headers أمنية لجميع الردود
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy
        response['Permissions-Policy'] = 'geolocation=(self), microphone=(), camera=()'
        
        if not settings.DEBUG:
            # Content-Security-Policy (في الإنتاج فقط)
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response['Content-Security-Policy'] = csp
            
            # HSTS (في الإنتاج فقط)
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting بسيط لحماية من Brute Force
    Simple rate limiting for brute force protection
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.failed_attempts = {}  # {ip: {'count': n, 'timestamp': t}}
        super().__init__(get_response)
    
    def process_request(self, request):
        # تطبيق rate limiting على endpoints الحساسة فقط
        sensitive_paths = [
            '/api/v1/auth/api/google-auth/',
            '/admin/login/',
        ]
        
        if not any(request.path.startswith(path) for path in sensitive_paths):
            return None
        
        # الحصول على IP
        ip = self.get_client_ip(request)
        
        # تحقق من عدد المحاولات
        if ip in self.failed_attempts:
            attempts = self.failed_attempts[ip]
            if attempts['count'] > 10:  # 10 محاولات فاشلة
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return JsonResponse({
                    'error': 'محاولات كثيرة جداً. حاول مرة أخرى لاحقاً',
                    'error_en': 'Too many attempts. Try again later.'
                }, status=429)
        
        return None
    
    def process_response(self, request, response):
        # تسجيل المحاولات الفاشلة
        if response.status_code in [401, 403] and hasattr(request, 'path'):
            ip = self.get_client_ip(request)
            
            if ip not in self.failed_attempts:
                self.failed_attempts[ip] = {'count': 0}
            
            self.failed_attempts[ip]['count'] += 1
            
            logger.info(f"Failed authentication attempt from IP: {ip}")
        
        # Reset على نجاح
        elif response.status_code in [200, 201] and hasattr(request, 'path'):
            ip = self.get_client_ip(request)
            if ip in self.failed_attempts:
                del self.failed_attempts[ip]
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """الحصول على IP الحقيقي للمستخدم"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    حماية بسيطة من SQL Injection
    Basic SQL injection protection
    """
    
    SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION',
        'SELECT', '--', ';', 'OR 1=1', 'OR 1 = 1'
    ]
    
    def process_request(self, request):
        # فحص GET parameters
        for key, value in request.GET.items():
            if self.contains_sql_injection(value):
                logger.critical(f"SQL Injection attempt detected in GET: {key}={value}")
                return HttpResponseForbidden("Invalid request")
        
        # فحص POST data
        if request.method == 'POST':
            try:
                for key, value in request.POST.items():
                    if isinstance(value, str) and self.contains_sql_injection(value):
                        logger.critical(f"SQL Injection attempt detected in POST: {key}={value}")
                        return HttpResponseForbidden("Invalid request")
            except:
                pass
        
        return None
    
    def contains_sql_injection(self, value):
        """فحص إذا كان النص يحتوي على SQL injection"""
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        return any(keyword in value_upper for keyword in self.SQL_KEYWORDS)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    تسجيل الأحداث الأمنية المهمة
    Log important security events
    """
    
    def process_request(self, request):
        # تسجيل الطلبات المهمة
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            logger.info(
                f"Request: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
            )
        
        return None
    
    def process_response(self, request, response):
        # تسجيل الأخطاء الأمنية
        if response.status_code in [401, 403, 404, 500]:
            logger.warning(
                f"Response: {response.status_code} for {request.method} {request.path} "
                f"from {self.get_client_ip(request)}"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
