from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts_app.models import Owner, Tenant, Profile
from admin_dashboard.models import Admin
from rental_property_app.models import Apartment, ApartmentFeature

from accounts_app.utils import register_user, update_user_profile, process_reset_password, display_email_sent_confirmation, display_password_reset_form, display_password_reset_done
from rental_property_app.utils import create_apartment_util, update_apartment_util
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts_app.utils import get_user_by_uid, change_user_password








""" 
Start: This fuctnion contains a
list of functions that relates to the user registeration, login, logout, dashboard, 
view all users, delete users, view and edit user profile, reset password and change password 
"""

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
    user_id = request.session.get('admin_id')  # assuming you store the admin's ID in session
    if not user_id:
        return redirect('admin_dashboard:admin_login')
    
    admin = get_object_or_404(Admin, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')

    # count the number of owners, tenants and apartments
    owners = Owner.objects.all().count()
    tenants = Tenant.objects.all().count()
    apartments = Apartment.objects.all().count()

    return render(request, 'admin_dashboard/dashboard_view.html', {
        'admin': admin,
        'profile': profile,
        'owners': owners,
        'tenants': tenants,
        'apartments': apartments
    })

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

########################################## End admin accounts(register/login/logout) ##########################################






################################################ Start Change password ################################################
def change_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_uid(uid)
    except (TypeError, ValueError, OverflowError):
        user = None
        messages.error(request, 'Invalid link or expired token.')
        return redirect('admin_dashboard:admin_login')

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        # Handle POST request inside utility function
        if request.method == "POST":
            response = change_user_password(request, uidb64, token, "admin_dashboard/admin_change_password.html")
            # Ensure there is always a response to return
            if response is True:
                return redirect('admin_dashboard:admin_login')
            else:
                return response
        else:
            # Render form for GET requests
            return render(request, "admin_dashboard/admin_change_password.html", {
                'uidb64': uidb64,
                'token': token,
                'user': user
            })
    else:
        messages.error(request, "Invalid link or expired token.")
        return redirect('admin_dashboard:admin_login')

def change_password_redirect_view(request):
    admin_id = request.session.get('admin_id')
    if admin_id:
        user = get_user_by_uid(admin_id)
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            return redirect('admin_dashboard:change_password', uidb64=uidb64, token=token)
        else:
            messages.error(request, "User not found")
            return redirect('admin_dashboard:admin_login')
    else:
        messages.warning(request, "Please login to change your password.")
        return redirect('admin_dashboard:admin_login')

########################################## End Change password  ##########################################



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

# view all admins
def view_admins(request):
    admins = Admin.objects.all()  # Fetch all admins
    profiles = Profile.objects.filter(person_type='admin')  # Fetch profiles related to admins
    profile_dict = {profile.person_id: profile for profile in profiles}  # Create a dictionary of profiles by person_id

    for admin in admins:
        admin.profile = profile_dict.get(admin.id, None)  # Attach profile to each admin

    return render(request, "admin_dashboard/view_admins.html", {
        'admins': admins
    })

########################################## End view all users(owner, tenants, and admins) ##########################################



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



########################################## End delete admin(admin, owner, tenant) ##########################################


########################################## Start view and edit owner, tenant, admin profile ##########################################

# View and edit admin profile
def admin_profile_view(request, id):
    admin = get_object_or_404(Admin, id=id)
    profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')
    # get user type
    if request.method == 'POST':
        # Here you would add the logic to update the profile
        update_user_profile(request, admin, profile, request.POST, 'admin')
        return redirect('admin_dashboard:admin_profile', id=admin.id)

    return render(request, 'admin_dashboard/admin_profile.html', {
        'admin': admin,
        'profile': profile,
        'user_type': 'admin'
    })


# View and edit owner profile
def owner_profile_view(request, id):
    owner = get_object_or_404(Owner, id=id)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')

    if request.method == 'POST':
        # Here you would add the logic to update the profile
        update_user_profile(request, owner, profile, request.POST, 'owner')
        return redirect('admin_dashboard:owner_profile', id=owner.id)

    return render(request, 'admin_dashboard/owner_profile.html', {
        'owner': owner,
        'profile': profile,
        'user_type': 'owner'
    })


# View and edit tenant profile
def tenant_profile_view(request, id):
    tenant = get_object_or_404(Tenant, id=id)
    profile, _ = Profile.objects.get_or_create(person_id=tenant.id, person_type='tenant')

    if request.method == 'POST':
        # Here you would add the logic to update the profile
        update_user_profile(request, tenant, profile, request.POST, 'tenant')
        return redirect('admin_dashboard:tenant_profile', id=tenant.id)

    return render(request, 'admin_dashboard/tenant_profile.html', {
        'tenant': tenant,
        'profile': profile,
        'user_type': 'tenant'
    })

########################################## End view and edit owner, tenant, admin profile ##########################################




########################################## Start reset password ##########################################
def reset_password(request):
    return process_reset_password(request, 'admin_dashbaord/reset_password_modal.html', 'admin_dashboard', 'user_id')
            
def password_reset_form(request, uidb64, token, user_type):
    app_name = 'admin_dashboard'
    template_name = 'admin_dashboard/password_reset_form.html'
    session_key = 'user_id'  # or 'admin_id' if this is for admin users
    return display_password_reset_form(request, uidb64, token, user_type, app_name, template_name, session_key)

def password_reset_done(request):
    return display_password_reset_done(request, 'admin_dashboard', 'admin_dashboard/password_reset_done.html', 'user_id')

def email_sent_confirmation(request):
    return display_email_sent_confirmation(request, 'admin_dashboard', 'admin_dashboard/email_sent_confirmation.html', 'user_id')

########################################## End reset password ##########################################



""" 
End: Function that accounts for user and admin
"""




"""
Start: apartment related functions
"""

   
def create_apartment_admin(request):
    apartment = create_apartment_util(request)
    owners = Owner.objects.all()  # Get all owners

    user_id = request.session.get('admin_id')  # assuming you store the admin's ID in session
    admin = get_object_or_404(Admin, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')
   

    if apartment:
        # Redirect on success redirect to home page
        return redirect('admin_dashboard:dashboard')
    
    else:
        return render(request, 'admin_dashboard/admin_apartment_register.html', {
        'user': admin,
        'profile': profile,
        'user_type': 'admin',
        'owners': owners
        })
    

# Update apartment view
def update_apartment_admin(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    owners = Owner.objects.all()  # Get all owners

    
    user_id = request.session.get('admin_id')  # assuming you store the admin's ID in session
    admin = get_object_or_404(Admin, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')

    # Fetch the features
    try:
        features = ApartmentFeature.objects.get(apartment=apartment)
    except ApartmentFeature.DoesNotExist:
        features = None

    if request.method == 'POST':
        updated_apartment = update_apartment_util(request, apartment_id)
        if updated_apartment:
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, "Failed to update apartment.")
            return render(request, 'admin_dashboard/admin_apartment_update.html', {
                'apartment': apartment,
                'user': admin,
                'profile': profile,
                'user_type': 'admin',
                'owners': owners,
                'existing_images': apartment.images.all(),
                'features': features  # Pass features to the template
            })
    else:
        # Populate the form with existing data for GET request
        return render(request, 'admin_dashboard/admin_apartment_update.html', {
            'apartment': apartment,
            'user': admin,
            'profile': profile,
            'user_type': 'admin',
            'owners': owners,
            'existing_images': apartment.images.all(),
            'features': features  # Pass features to the template
        })
    

# Delete apartment
def delete_apartment_admin(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    apartment.delete()
    messages.success(request, "Apartment successfully deleted.")
    return redirect('admin_dashboard:view_apartments')


# read all apartments
def view_apartments(request):
    apartments = Apartment.objects.all()
    return render(request, "admin_dashboard/view_apartments.html", {'apartments': apartments})