from django.shortcuts import render,redirect
from django.urls import reverse
from accounts_app.models import Owner, Tenant, Profile
from accounts_app.utils import register_user
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from admin_dashboard.models import Admin
from datetime import datetime
from .utils import get_admin_from_request


# Create your views here.

########################################## Start User Registeration(Tenats or Owners) ##########################################
def register_view(request):
    if request.method == "POST":
        user_data = {
            "first_name": request.POST.get("first_name"),
            "middle_name": request.POST.get("middle_name"),
            "last_name": request.POST.get("last_name"),
            "email_address": request.POST.get("type_email"),
            "gender": request.POST.get("gender"),
            "date_of_birth": request.POST.get("date_of_birth"),
            "phone_number": request.POST.get("phone_number"),
            "address": request.POST.get("address"),
            "occupation": request.POST.get("occupation"),
            "state": request.POST.get("state"),
            "type_of_user": request.POST.get("type_of_user"),
            "password": request.POST.get("password"),
            "confirm_password": request.POST.get("confirm_password")
        }

        user = register_user(request, user_data)
        if user:
            return redirect("admin_dashboard:dashboard")

    return render(request, "admin_dashboard/user_registeration.html")
########################################## End User Registeration ##########################################


########################################## Start Admin Dashboard ##########################################
def dashboard_view(request):
    if not request.session.get('admin_id'):
        return redirect(reverse('admin_dashboard:admin_login'))
    return render(request, "admin_dashboard/dashboard_view.html")

########################################## End Admin Dashboard ##########################################



########################################## Start admin accounts(register/login/logout) ##########################################


# Admin register
def admin_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name").strip()
        gender = request.POST.get("gender")
        email = request.POST.get("email_address").strip()
        address = request.POST.get("address")
        phone = request.POST.get("phone_number")
        date_of_birth = request.POST.get("date_of_birth")
        try:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Invalid date of birth")
            return render(request, "admin_dashboard/admin_register.html")
        password = request.POST.get("password").strip()
        # Check if the admin should be a superuser
        should_be_superuser = request.POST.get("superuser", "off") == "on"

        if Admin.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        else:
            admin = Admin.objects.create_admin(
                full_name=full_name, 
                gender=gender,
                email=email,
                address=address,
                date_of_birth=date_of_birth,
                password=password,
                phone_number=phone,
                is_superuser=should_be_superuser  # Pass true or false based on the form input
            )
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard:dashboard')
    return render(request, "admin_dashboard/admin_register.html")


# Admin login
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email_address").strip()
        password = request.POST.get("password").strip()

        try:
            admin = Admin.objects.get(email=email)
            if admin.check_password(password):
                request.session['admin_id'] = admin.id
                return redirect('admin_dashboard:dashboard')
            else:
                messages.error(request, "Invalid email or password")
        except Admin.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "admin_dashboard/admin_login.html")


# Admin logout
def admin_logout(request):
    request.session.flush()
    return redirect('admin_dashboard:admin_login')




def admin_profile_view(request):
    admin = get_admin_from_request(request)
    if not admin:
        return redirect('admin_dashboard:login')

    profile, created = Profile.objects.get_or_create(person_id=admin.id, person_type='admin', defaults={'bio': 'No additional details provided.'})

    context = {
        'admin': admin,
        'profile': profile
    }
    return render(request, 'admin_dashboard/admin_profile.html', context)



def admin_change_password(request):
    return render(request, "admin_dashboard/admin_change_password.html", {})


########################################## End admin accounts ##########################################


########################################## Start view all users(owners, tenants and admins) ##########################################
# Fetch all owners and their related profiles.
def view_owners(request):
    owners = Owner.objects.all()  # Fetch all owners
    profiles = Profile.objects.filter(person_type='owner')  # Fetch profiles related to owners
    profile_dict = {profile.person_id: profile for profile in profiles}  # Create a dictionary of profiles by person_id

    # Attach each profile to its respective owner
    for owner in owners:
        owner.profile = profile_dict.get(owner.id, None)  # Default to None if no profile is found
    return render(request, "admin_dashboard/view_owners.html", {'owners': owners})



# view all tenants
def view_tenants(request):
    tenants = Tenant.objects.all()  # Fetch all tenants
    profiles = Profile.objects.filter(person_type='tenant')  # Fetch profiles related to tenants
    profile_dict = {profile.person_id: profile for profile in profiles}  # Create a dictionary of profiles by person_id

    # Attach each profile to its respective Tenant
    for owner in tenants:
        owner.profile = profile_dict.get(owner.id, None)  # Default to None if no profile is found
    return render(request, "admin_dashboard/view_tenants.html", {'tenants': tenants})


def view_admins(request):
    admins = Admin.objects.all()  # Fetch all admins
    profiles = Profile.objects.filter(person_type='admin')  # Fetch profiles related to admins
    profile_dict = {profile.person_id: profile for profile in profiles}  # Create a dictionary of profiles by person_id

    # Attach each profile to its respective Tenant
    for admin in admins:
        admin.profile = profile_dict.get(admin.id, None)  # Default to None if no profile is found
    return render(request, "admin_dashboard/view_admins.html", {'admins': admins})
########################################## End view all users ##########################################



########################################## Start delete admin, owner, tenant ##########################################
def delete_admin(request):
    if request.method == "POST":
        admin_id = request.POST.get('admin_id')
        Admin.objects.filter(id=admin_id).delete()
        messages.success(request, "Admin successfully deleted.")
        return redirect('admin_dashboard:view_admins')
    else:
        messages.error(request, "Invalid request")
        return redirect('admin_dashboard:view_admins')
    
def delete_owner(request):
    if request.method == "POST":
        owner_id = request.POST.get('owner_id')
        Owner.objects.filter(id=owner_id).delete()
        messages.success(request, "Owner successfully deleted.")
        return redirect('admin_dashboard:view_owners')

def delete_tenant(request):
    if request.method == "POST":
        tenant_id = request.POST.get('tenant_id')
        Tenant.objects.filter(id=tenant_id).delete()
        messages.success(request, "Tenant successfully deleted.")
        return redirect('admin_dashboard:view_tenants')



########################################## End delete admin ##########################################






def view_blacklist(request):
    return render(request, "admin_dashboard/view_blacklist.html", {})




