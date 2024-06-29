from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Owner, Tenant
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from admin_dashboard.models import Admin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from datetime import datetime
from django.http import HttpResponse
from datetime import date




####################################### Start registeration for owner and tenant ########################################
def register_user(request, user_data):
    # Extracting user data
    first_name = user_data.get("first_name")
    middle_name = user_data.get("middle_name")
    last_name = user_data.get("last_name")
    email_address = user_data.get("email_address")
    gender = user_data.get("gender")
    date_of_birth = user_data.get("date_of_birth")
    phone_number = user_data.get("phone_number")
    address = user_data.get("address")
    occupation = user_data.get("occupation")
    state = user_data.get("state")
    type_of_user = user_data.get("type_of_user")
    password = user_data.get("password")
    confirm_password = user_data.get("confirm_password")

    # Data cleaning
    if type_of_user:
            type_of_user = type_of_user.capitalize()
    if password and confirm_password:
        password = password.strip()
        confirm_password = confirm_password.strip()
    if email_address:
        email_address = email_address.lower()
        email_address = email_address.strip()

    # Check if any field is empty
    if not all([first_name, middle_name, last_name, email_address, gender, date_of_birth, phone_number, address, occupation, state, type_of_user, password, confirm_password]):
        messages.error(request, "Please fill in all fields")
        return None
    
   
    # Check if password and confirm password match
    if password != confirm_password:
        messages.error(request, "Password and Confirm Password do not match")
        return None
    

     # Perform email check based on type of user
    if type_of_user == "Owner":
        if Owner.objects.filter(email_address=email_address).exists():
            messages.error(request, "Email address already exists in Owner records.")
            return None  # or redirect or return appropriate response
    elif type_of_user == "Tenant":
        if Tenant.objects.filter(email_address=email_address).exists():
            messages.error(request, "Email address already exists in Tenant records.")
            return None  # or redirect or return appropriate response
    
    # Create user
    if type_of_user == "Owner":
        user = Owner(first_name=first_name, middle_name=middle_name, last_name=last_name, email_address=email_address, gender=gender,
                     date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state)
    elif type_of_user == "Tenant":
        user = Tenant(first_name=first_name, middle_name=middle_name, last_name=last_name, email_address=email_address, gender=gender,
                      date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state)
    else:
        messages.error(request, "Invalid type of user")
        return None
    
    # Convert the string date to a date object
    try:
        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()  # Adjust the format string as per your input date format
    except ValueError:
        messages.error(request, "Invalid date format")

    # Calculate age
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    # Check if user is at least 18 years old
    if age < 18:
        messages.error(request, "User must be at least 18 years old")
        return None




   
    
    

    user.set_password(password)
    user.save()
    
    # Email sending logic
    subject = "Welcome to Somali Real Estate"
    message = f"Hi {first_name},\n\nYou have successfully registered as a {type_of_user}.\n\nWelcome to Somali Real Estate.\n\nWe are glad to have you on board.\n\nBest Regards,\nSomali Real Estate Team"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email_address]
    send_mail(subject, message, email_from, recipient_list)

    messages.success(request, "Registration successful")
    return user

####################################### End registeration for owner and tenant ########################################





####################################### Start update user profileyyy ########################################
def update_user_profile(request, user, profile, form_data, user_type):
    """
    Update user and profile data from form data based on user type.
    """

    # Parse and validate date of birth
    dob = form_data.get('date_of_birth')
    if dob:
        try:
            # Check if dob is a string and needs to be parsed
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            elif not isinstance(dob, date):
                raise ValueError("Invalid type for date_of_birth")
            
            # Calculate age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check if user is at least 18 years old
            if age < 18:
                messages.error(request, "User must be at least 18 years old")
                return None
            
        except ValueError as e:
            messages.error(request, f"Invalid date format: {e}")
            return None
        

    if user_type in ['owner', 'tenant']:
        # Common fields for Owner and Tenant
        user.first_name = form_data.get('first_name', user.first_name)
        user.middle_name = form_data.get('middle_name', user.middle_name)
        user.last_name = form_data.get('last_name', user.last_name)
        user.email_address = form_data.get('type_email', user.email_address)
        user.gender = form_data.get('gender', user.gender)
        user.date_of_birth = dob
        user.phone_number = form_data.get('phone_number', user.phone_number)
        user.address = form_data.get('address', user.address)
        user.occupation = form_data.get('occupation', user.occupation)
        user.state = form_data.get('state', user.state) 
    elif user_type == 'admin':
        # Fields specific to Admin
        user.full_name = form_data.get('full_name', user.full_name)
        user.gender = form_data.get('gender', user.gender)
        user.email = form_data.get('email', user.email)
        user.address = form_data.get('address', user.address)
        user.phone_number = form_data.get('phone_number', user.phone_number)
        user.date_of_birth = form_data.get('date_of_birth', user.date_of_birth)

    user.save()

    # Profile specific updates
    profile.bio = form_data.get('bio', profile.bio)
    profile.facebook_link = form_data.get('facebook_link', profile.facebook_link)
    profile.tiktok_link = form_data.get('tiktok_link', profile.tiktok_link)
    profile.youtube_link = form_data.get('youtube_link', profile.youtube_link)
    if 'profile_picture' in request.FILES:
        profile.profile_picture = request.FILES['profile_picture']
    profile.save()

    messages.success(request, "Profile updated successfully!")
    


####################################### End update user profile ########################################


####################################### Start Change Password ########################################

def get_user_by_uid(uid):
    """Retrieve user by ID across Owner, Tenant, and Admin."""
    return Owner.objects.filter(id=uid).first() or \
           Tenant.objects.filter(id=uid).first() or \
           Admin.objects.filter(id=uid).first()


def change_user_password(request, uidb64, token, template_name):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_uid(uid)
    except (TypeError, ValueError, OverflowError):
        user = None
        messages.error(request, 'Invalid link or expired token.')
        return None

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
                return True 
        return render(request, template_name, {
            'uidb64': uidb64,
            'token': token,
            'user': user  # pass user also if needed elsewhere in template
        })
    else:
        messages.error(request, "Invalid link or expired token.")
        return None



####################################### End Change Password ########################################


####################################### Start Reset Password ########################################
def process_reset_password(request, template_name, app_name, session_key):
    if request.method == 'POST':
        email = request.POST.get('email1')
        user_type = request.POST.get('role')
        user_model = get_user_model(user_type)

        # Determine the correct email field based on user type
        if user_type in ['Owner', 'Tenant']:
            email_field = 'email_address'  # Assume 'Owner' and 'Tenant' use 'email_address'
            user = user_model.objects.filter(email_address=email).first()
        else:
            email_field = 'email'  # Assume 'Admin' uses 'email'
            user = user_model.objects.filter(email=email).first()

        if not email or not user_type:
            messages.error(request, "Please fill in all fields")
            return render(request, template_name)

        if user:
            display_send_reset_email(user, user_type, request, app_name, email_field)
            return redirect(f'{app_name}:email_sent_confirmation')
        else:
            messages.error(request, "Invalid email address")
    return render(request, template_name)

def display_send_reset_email(user, user_role, request, app_name, email_field):
    token_generator = PasswordResetTokenGenerator()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_path = reverse(f'{app_name}:password_reset_form', args=[uid, token, user_role])
    reset_url = request.build_absolute_uri(reset_path)

    # Construct email and name using direct access based on predefined conditions
    if email_field == 'email_address':
        email = user.email_address
        name = user.first_name  # Assuming 'first_name' exists for Owner/Tenant
    else:
        email = user.email
        name = user.full_name  # Assuming 'full_name' exists for Admin

    subject = "Password Reset Requested"
    message = f"Hi {name},\n\nYou have requested to reset your password as a {user_role}.\nPlease click on the following link to reset your password:\n{reset_url}\n\nIf you did not make this request, please ignore this email and ensure your account is secure."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def get_user_model(user_type):
    user_model = {
        'Owner': Owner,  # Assuming Owner is defined somewhere
        'Tenant': Tenant,  # Assuming Tenant is defined somewhere
        'Admin': Admin  # Assuming Admin is a valid model for admins
    }.get(user_type)
    return user_model




def display_password_reset_form(request, uidb64, token, user_type, app_name, template_name, session_key):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_model = get_user_model(user_type)
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
                return redirect(f'{app_name}:password_reset_done')

        return render(request, template_name, {
            'uidb64': uidb64,
            'token': token,
            'user_type': user_type
        })
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        login_url = 'admin_dashboard:admin_login' if app_name == 'admin_dashboard' else 'accounts_app:login'
        return redirect(login_url)

def display_password_reset_done(request, app_name, template_name, session_key):
    user_id = request.session.get(session_key, None)
    user_role = request.session.get('user_role', None)
    user_model = get_user_model(user_role)

    user = None
    if user_model and user_id:
        user = user_model.objects.filter(id=user_id).first()

    return render(request, template_name, {'user': user})

def display_email_sent_confirmation(request, app_name, template_name, session_key):
    user_id = request.session.get(session_key, None)
    user_role = request.session.get('user_role', None)
    user_model = get_user_model(user_role)

    user = None
    if user_model and user_id:
        user = user_model.objects.filter(id=user_id).first()

    return render(request, template_name, {'user': user})