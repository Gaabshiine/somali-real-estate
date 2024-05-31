from .models import Admin
from accounts_app.models import Profile
from django.shortcuts import get_object_or_404

def admin_context(request):
    user_id = request.session.get('admin_id')
    if user_id:
        
        admin = get_object_or_404(Admin, id=user_id)
        profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')
        return {
            'admin': admin,
            'profile': profile,
            'is_superuser': admin.is_superuser  # Include is_super in the context
        }
    return {}
