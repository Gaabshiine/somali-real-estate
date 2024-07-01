from django.shortcuts import redirect
from django.urls import reverse
import re


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        skip_paths = [
            reverse('accounts_app:login'),
            reverse('accounts_app:choose_role'),
            reverse('accounts_app:choose_role_reset'),
            reverse('accounts_app:register'),
            reverse('accounts_app:reset_password'),
            reverse('accounts_app:email_sent_confirmation'),
            reverse('accounts_app:password_reset_done'),
            # Add other static paths if needed
        ]

        dynamic_skip_patterns = [
            re.compile(r'^/account/password_reset_form/[^/]+/[^/]+/$'),
            # Add other dynamic patterns if needed
        ]

        if request.path in skip_paths or any(pattern.match(request.path) for pattern in dynamic_skip_patterns):
            return self.get_response(request)

        if request.path.startswith('/account/') or request.path.startswith('/rental_properties/'):
            if not request.session.get('user_id'):
                return redirect(reverse('accounts_app:login'))

        return self.get_response(request)