from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Owner, Tenant, Profile
from django.conf import settings
from .utils import register_user, update_user_profile, get_user_by_uid, change_user_password, process_reset_password, display_email_sent_confirmation, display_password_reset_form, display_password_reset_done
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str



token_generator = PasswordResetTokenGenerator()


# Create your views here.


############################# Register info #############################
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
            return redirect("accounts_app:login")

    return render(request, "accounts_app/register.html")





############################# Start Profile info #############################


def owner_profile_view(request):
    user_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')

    return render(request, 'accounts_app/owner_profile.html', {
        'user': owner,
        'profile': profile,
        'user_type': 'owner'
    })




def tenant_profile_view(request):
    user_id = request.session.get('user_id')
    tenant = get_object_or_404(Tenant, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=tenant.id, person_type='tenant')

    return render(request, 'accounts_app/tenant_profile.html', {
        'user': tenant,
        'profile': profile,
        'user_type': 'tenant'
    })



def edit_owner_profile_view(request, id): 
    user_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')
    if request.method == 'POST':
        update_user_profile(request, owner, profile, request.POST, 'owner')
        return redirect('accounts_app:owner_profile')
    return render(request, 'accounts_app/edit_profile.html', {'user': owner, 'profile': profile})


def edit_tenant_profile_view(request, id):
    user_id = request.session.get('user_id')
    tenant = get_object_or_404(Tenant, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=tenant.id, person_type='tenant')
    if request.method == 'POST':
        update_user_profile(request, tenant, profile, request.POST, 'tenant')
        return redirect('accounts_app:tenant_profile')
    return render(request, 'accounts_app/edit_profile.html', {'user': tenant, 'profile': profile})

############################# End Profile info #############################




############################# start Login info #############################

def login_view(request):
    if request.method == "POST":
        email_address = request.POST.get("type_email", "").strip()
        password = request.POST.get("type_password", "").strip()
        type_of_user = request.POST.get("role", "").strip().lower()  # Ensure it's in lowercase

        # Check for missing input fields
        if not email_address or not password or not type_of_user:
            messages.error(request, "Please fill in all fields.")
            return render(request, "accounts_app/login.html")

        # Attempt to fetch the user based on type and email
        user = None
        if type_of_user == "owner":
            user = Owner.objects.filter(email_address=email_address).first()
        elif type_of_user == "tenant":
            user = Tenant.objects.filter(email_address=email_address).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            request.session['user_id'] = user.id
            request.session['user_role'] = type_of_user  # Set the user role in session
            messages.success(request, "Login successful.")
            return redirect(get_redirect_url(user))
        else:
            # Display error message if user not found or password is incorrect
            messages.error(request, "Invalid email address or password.")
    
    # Render the login page again with error message
    return render(request, "accounts_app/login.html")


# get_redirect_url
def get_redirect_url(user):
    """
    Simple function to determine the redirect URL based on user type.
    """
    if isinstance(user, Owner):
        return 'accounts_app:owner_profile'
    elif isinstance(user, Tenant):
        return 'accounts_app:tenant_profile'
    # Add checks for other user types as necessary
    # Example:
    # elif isinstance(user, Seller):
    #     return 'accounts_app:seller_profile'
    # elif isinstance(user, Buyer):
    #     return 'accounts_app:buyer_profile'
    return 'accounts_app:login'  # Default redirect URL


############################# End Login info #############################




############################# start change_password_view info #############################

def change_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_uid(uid)
    except (TypeError, ValueError, OverflowError):
        user = None
        messages.error(request, 'Invalid link or expired token.')
        return redirect('accounts_app:login')

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        # Handle POST request inside utility function
        if request.method == "POST":
            response = change_user_password(request, uidb64, token, "accounts_app/change_password.html")
            # Ensure there is always a response to return
            if response is True:
                return redirect('accounts_app:login')
            else:
                return response
        else:
            # Render form for GET requests
            return render(request, "accounts_app/change_password.html", {
                'uidb64': uidb64,
                'token': token,
                'user': user
            })
    else:
        messages.error(request, "Invalid link or expired token.")
        return redirect('accounts_app:login')

def change_password_redirect_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = get_user_by_uid(user_id)
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            return redirect('accounts_app:change_password', uidb64=uidb64, token=token)
        else:
            messages.error(request, "User not found")
            return redirect('accounts_app:login')
    else:
        messages.warning(request, "Please login to change your password.")
        return redirect('accounts_app:login')


############################# End change_password_view info #############################





############################# start Logout view info #############################
def logout_view(request):
    request.session.clear()
    messages.success(request, "You have been logged out successfully")
    return redirect('accounts_app:login')


############################# End Logout view info #############################






############################# start reset_password_view info #############################

def reset_password(request):
    return process_reset_password(request, 'accounts_app/reset_password_modal.html', 'accounts_app', 'user_id')
            
def password_reset_form(request, uidb64, token, user_type):
    app_name = 'accounts_app'
    template_name = 'accounts_app/password_reset_form.html'
    session_key = 'user_id'  # or 'admin_id' if this is for admin users
    return display_password_reset_form(request, uidb64, token, user_type, app_name, template_name, session_key)

def password_reset_done(request):
    return display_password_reset_done(request, 'accounts_app', 'accounts_app/password_reset_done.html', 'user_id')

def email_sent_confirmation(request):
    return display_email_sent_confirmation(request, 'accounts_app', 'accounts_app/email_sent_confirmation.html', 'user_id')



############################# End reset_password_view info #############################o