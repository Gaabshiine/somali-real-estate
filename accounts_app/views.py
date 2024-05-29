from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from .models import Owner, Tenant, Profile
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from .utils import register_user

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
    user = get_object_or_404(Owner, id=user_id)
    profile, created = Profile.objects.get_or_create(person_id=user.id, person_type='owner')

    return render(request, 'accounts_app/owner_profile.html', {
        'user': user,
        'profile': profile,
        'user_type': 'owner'
    })

def tenant_profile_view(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Tenant, id=user_id)
    profile, created = Profile.objects.get_or_create(person_id=user.id, person_type='tenant')

    return render(request, 'accounts_app/tenant_profile.html', {
        'user': user,
        'profile': profile,
        'user_type': 'tenant'
    })

def edit_profile_view(request, id, user_type):
    model = Owner if user_type == 'owner' else Tenant
    user = get_object_or_404(model, id=id)
    
    profile, created = Profile.objects.get_or_create(
        person_id=user.id, person_type=user_type
    )

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.middle_name = request.POST.get('middle_name', '')
        user.last_name = request.POST.get('last_name')
        user.email_address = request.POST.get('email')
        user.gender = request.POST.get('gender')
        user.date_of_birth = request.POST.get('date_of_birth')
        user.phone_number = request.POST.get('phone_number')
        user.address = request.POST.get('address')
        user.state = request.POST.get('state')
        user.occupation = request.POST.get('occupation')
        user.save()

        profile.bio = request.POST.get('bio')
        profile.facebook_link = request.POST.get('facebook_link')
        profile.tiktok_link = request.POST.get('tiktok_link')
        profile.youtube_link = request.POST.get('youtube_link')

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('accounts_app:owner_profile' if user_type == 'owner' else 'accounts_app:tenant_profile')

    return render(request, 'accounts_app/edit_profile.html', {
        'user': user,
        'profile': profile,
        'user_type': user_type
    })


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
        user = Owner.objects.filter(id=uid).first() or Tenant.objects.filter(id=uid).first()
    except (TypeError, ValueError, OverflowError):
        user = None
        messages.error(request, 'Invalid link or expired token.')
        return redirect('accounts_app:login')

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        if request.method == "POST":
            old_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not user.check_password(old_password):
                messages.error(request, "Current password is incorrect")
            elif new_password != confirm_password:
                messages.error(request, "New password and confirm password do not match")
            elif user.check_password(new_password):
                messages.error(request, "New password should be different from the old one")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Important to keep the user logged in after changing password
                messages.success(request, "Password updated successfully")
                return redirect('accounts_app:login')  # Or redirect to a different success page
        return render(request, "accounts_app/change_password.html", {
            'uidb64': uidb64,
            'token': token,
            'user': user  # pass user also if needed elsewhere in template
        })
    else:
        messages.error(request, "Invalid link or expired token.")
        return redirect('accounts_app:login')


# change_password_redirect_view
def change_password_redirect_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = Owner.objects.filter(id=user_id).first() or Tenant.objects.filter(id=user_id).first()
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
    if request.method == 'POST':
        email = request.POST.get('email1')
        # get id from the session
        user_id = request.session.get('user_id')
        user_type = request.POST.get('role')
        user_model = {
            'Owner': Owner,
            'Tenant': Tenant
        }.get(user_type)

        # check if the input has empty fields
        if not email or not user_type:
            messages.error(request, "Please fill in all fields")
            return render(request, 'accounts_app/reset_password_modal.html')
        if user_model:
            # check the Id of the user has the same email
            user = user_model.objects.filter(email_address=email).first()
            if user:
                send_reset_email(user, user_type, request)
                return redirect('accounts_app:email_sent_confirmation')
            else:
                messages.error(request, "Invalid email address")
        else:
            messages.error(request, "Invalid user type")
    return render(request, 'accounts_app/reset_password_modal.html')


            



def send_reset_email(user, user_role, request):
    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_path = reverse('accounts_app:password_reset_form', args=[uid, token, user_role])
    reset_url = request.build_absolute_uri(reset_path)

    subject = "Password Reset Requested"
    message = f"Hi {user.first_name},\n\nYou have requested to reset your password as a {user_role}.\nPlease click on the following link to reset your password:\n{reset_url}\n\nIf you did not make this request, please ignore this email and ensure your account is secure."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email_address]
    send_mail(subject, message, email_from, recipient_list)
    return redirect('accounts_app:password_reset_done')



def password_reset_form(request, uidb64, token, user_type):
    try:
        # Decode the uidb64 to a user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_model = {'Owner': Owner, 'Tenant': Tenant}.get(user_type)
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist) as e:
        user = None
        messages.error(request, 'Invalid password reset link. Please try resetting your password again.')

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if not password or not confirm_password:
                messages.error(request, "Please fill in all fields.")
            elif password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif check_password(password, user.password):
                messages.error(request, "New password cannot be the same as the old password.")
            else:
                user.set_password(password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('accounts_app:password_reset_done')

        # Display the form if not POST or there were validation errors
        return render(request, 'accounts_app/password_reset_form.html', {
            'uidb64': uidb64,
            'token': token,
            'user_type': user_type
        })
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('accounts_app:login')  # Redirect to login or another appropriate page



def password_reset_done(request):
    user_id = request.session.get('user_id', None)
    user_role = request.session.get('user_role', None)

    # Based on the user_role, determine the model to use
    if user_role == 'owner':
        user_model = Owner
    elif user_role == 'tenant':
        user_model = Tenant
    else:
        user_model = None

    user = None
    if user_model and user_id:
        user = user_model.objects.filter(id=user_id).first()
    
   
    return render(request, 'accounts_app/password_reset_done.html', {'user': user})


def email_sent_confirmation(request):
    user_id = request.session.get('user_id', None)
    user_role = request.session.get('user_role', None)

    # Based on the user_role, determine the model to use
    if user_role == 'owner':
        user_model = Owner
    elif user_role == 'tenant':
        user_model = Tenant
    else:
        user_model = None

    user = None
    if user_model and user_id:
        user = user_model.objects.filter(id=user_id).first()
    
 

    return render(request, 'accounts_app/email_sent_confirmation.html', {'user': user})



############################# End reset_password_view info #############################o