from django.http import JsonResponse
from rest_framework.status import HTTP_401_UNAUTHORIZED

def strict_auth_middleware(get_response):
    # Inner function to process each request
    def middleware(request):
        # Extract the Authorization header from the request
        auth_header = request.headers.get('Authorization', None)
        
        # If the Authorization header is present
        if auth_header:
            # Check if the user is anonymous or authentication failed
            if request.user.is_anonymous or request.auth is None:
                # Return a 401 Unauthorized response
                return JsonResponse({'detail': 'Invalid token.'}, status=HTTP_401_UNAUTHORIZED)
        
        # If no Authorization header is present or authentication is successful,
        # continue processing the request as normal
        return get_response(request)

    return middleware
