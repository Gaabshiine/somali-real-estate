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
            # You can add more admin public paths if necessary
        ]

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
