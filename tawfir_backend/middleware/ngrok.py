class NgrokHeaderMiddleware:
    """
    Middleware to add ngrok-skip-browser-warning header to all responses
    This bypasses ngrok's browser warning page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers explicitly for all origins
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, ngrok-skip-browser-warning'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
