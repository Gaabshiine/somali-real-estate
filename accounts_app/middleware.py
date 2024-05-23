# accounts_app/middleware.py

from django.shortcuts import redirect

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define public paths that do not require authentication
        public_paths = [
            '/account/login/', 
            '/account/register/', 
            '/account/reset_password/',
            '/account/reset_password_done/',
            '/account/reset_password_confirm/',
            '/account/reset_password_complete/',
            '/',  # Home page
            '/about/',  # About page
            '/contact/',  # Contact page
            '/search/',  # Search page
            '/property_details/',  # Property details page
            # Add more public paths as necessary
        ]
        
        # Check if the current path is not in public paths and user is not authenticated
        if not request.session.get('user_id') and request.path not in public_paths:
            return redirect('accounts_app:login')
        
        response = self.get_response(request)
        return response
