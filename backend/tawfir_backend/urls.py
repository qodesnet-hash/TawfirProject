from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from django.http import HttpResponse

# ✅ تخصيص Django Admin
admin.site.site_header = 'لوحة تحكم توفير آب'
admin.site.site_title = 'توفير آب - لوحة التحكم'
admin.site.index_title = 'مرحباً بك في لوحة التحكم'

def serve_media_with_cors(request, path):
    """Custom media serve with CORS headers"""
    response = serve(request, path, document_root=settings.MEDIA_ROOT)
    
    # Add comprehensive CORS headers
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = '*'
    response['Cross-Origin-Resource-Policy'] = 'cross-origin'
    response['Access-Control-Expose-Headers'] = '*'
    
    return response

urlpatterns = [
    path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/notifications/', include('api.urls_notifications')),
]

# Media files with CORS
if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve_media_with_cors, name='media'),
    ]
