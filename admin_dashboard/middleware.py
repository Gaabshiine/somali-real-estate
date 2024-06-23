from django.shortcuts import redirect
from django.urls import reverse
from .models import AdminActivityLog
from .utils import get_admin_from_request


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin-specific paths
        admin_public_paths = [
            reverse('admin_dashboard:admin_login'),
            reverse('admin_dashboard:admin_register'),
            reverse('admin_dashboard:reset_password'),
            reverse('admin_dashboard:email_sent_confirmation'),
            reverse('admin_dashboard:password_reset_done'),
            # You can add more admin public paths if necessary
        ]

        dynamic_paths = [
            '/admin_dashboard/password_reset_form/',  # this is a dynamic path, check based on starts with
        ]

        # Allow unauthenticated access to public paths or if the path is for password resetting
        if request.path in admin_public_paths or any(request.path.startswith(path) for path in dynamic_paths):
            return self.get_response(request)
        

        # Apply this middleware only to admin paths
        if request.path.startswith('/admin_dashboard/'):
            if not request.session.get('admin_id') and request.path not in admin_public_paths:
                return redirect(reverse('admin_dashboard:admin_login'))

        # Log admin activity if an admin is logged in
        admin = get_admin_from_request(request)
        if admin:
            AdminActivityLog.objects.create(
                admin=admin,
                action=f"Accessed URL {request.path}"
            )
        return self.get_response(request)
