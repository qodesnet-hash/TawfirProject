# api/middleware.py
"""
Middleware للتصحيح ومراقبة المصادقة
"""
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class AuthDebugMiddleware(MiddlewareMixin):
    """
    Middleware لتصحيح مشاكل المصادقة
    يطبع معلومات مفيدة عن كل طلب API
    """
    
    def process_request(self, request):
        # للطلبات المتعلقة بالمراجعات أو Auth
        if '/reviews/' in request.path or '/auth/' in request.path:
            print("\n" + "="*60)
            print(f"🔍 AUTH DEBUG - {request.method} {request.path}")
            print("="*60)
            
            # معلومات الهيدر
            auth_header = request.META.get('HTTP_AUTHORIZATION', 'None')
            print(f"📋 Authorization Header: {auth_header}")
            
            # نوع المصادقة
            if auth_header and auth_header != 'None':
                auth_type = auth_header.split()[0] if ' ' in auth_header else 'Unknown'
                print(f"🔑 Auth Type: {auth_type}")
                
                # التوكن
                if ' ' in auth_header:
                    token = auth_header.split()[1]
                    print(f"🎫 Token (first 20 chars): {token[:20]}...")
            
            # معلومات المستخدم
            if hasattr(request, 'user'):
                print(f"👤 User: {request.user}")
                print(f"✅ Is Authenticated: {request.user.is_authenticated}")
                if request.user.is_authenticated:
                    print(f"📱 Phone: {getattr(request.user, 'phone_number', 'N/A')}")
                    print(f"🆔 User ID: {request.user.id}")
            
            # الجلسة
            if hasattr(request, 'session'):
                print(f"🍪 Session Key: {request.session.session_key}")
            
            print("="*60 + "\n")
        
        return None
    
    def process_response(self, request, response):
        # للطلبات المتعلقة بالمراجعات أو Auth
        if '/reviews/' in request.path or '/auth/' in request.path:
            print("\n" + "-"*60)
            print(f"📤 RESPONSE - {request.method} {request.path}")
            print(f"   Status: {response.status_code}")
            
            # إذا كان هناك خطأ في المصادقة
            if response.status_code == 401:
                print("   ⚠️ Authentication Failed!")
            elif response.status_code == 400:
                print("   ⚠️ Bad Request - Check data!")
            elif response.status_code in [200, 201]:
                print("   ✅ Success!")
            
            print("-"*60 + "\n")
        
        return response
