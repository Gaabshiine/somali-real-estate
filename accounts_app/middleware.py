from django.shortcuts import redirect
from django.urls import reverse


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that should skip this user authentication check
        skip_paths = [
            '/account/login/', 
            '/account/register/', 
            '/account/reset_password/',
            '/account/email_sent_confirmation/',
            '/account/password_reset_done/',
            '/account/password_reset_form/',  # This should ideally check dynamically for the presence of user_id and user_type in the path
            '/',  # Home page
            '/about/',  # About page
            '/contact/',  # Contact page
            '/search/',  # Search page
            '/property_details/',  # Property details page
        ]

        # Allow unauthenticated access to public paths or if the path is for password resetting
        if request.path in skip_paths or '/account/password_reset_form/' in request.path:
            return self.get_response(request)

        # Apply this middleware only to admin paths
        if request.path.startswith('/account/'):
            if not request.session.get('user_id') and request.path not in skip_paths:
                return redirect(reverse('accounts_app:login'))
            
        # Check for user authentication for other paths
        # if not request.session.get('user_id'):
        #     return redirect(reverse('accounts_app:login'))

        return self.get_response(request)
