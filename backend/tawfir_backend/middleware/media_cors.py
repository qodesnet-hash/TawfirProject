"""
Middleware to add CORS headers to media files
"""

class MediaCORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers for media files
        if request.path.startswith('/media/'):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response['Access-Control-Allow-Headers'] = '*'
            response['Cross-Origin-Resource-Policy'] = 'cross-origin'
            response['Access-Control-Expose-Headers'] = '*'
            
        return response
