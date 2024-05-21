from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from .models import Owner, Tenant, Profile
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType


# Create your views here.


############################# Register info #############################
def register_view(request):
    if request.method == "POST":
        # get the form data
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        email_address = request.POST.get("type_email").strip()
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        occupation = request.POST.get("occupation")
        state = request.POST.get("state")
        type_of_user = request.POST.get("type_of_user").capitalize()
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm_password").strip()
        

        # check if the input has empty fields
        if not first_name or not last_name or not middle_name or not email_address or not gender or not date_of_birth or not phone_number or not address or not occupation or not state or not type_of_user or not password or not confirm_password:
            messages.error(request, "Please fill in all fields")
            return render(request, "accounts_app/register.html")
        # check if the password and confirm password are the same
        if password == confirm_password:
            # check the type of user
            if type_of_user == "Owner":
                # save the data to the database
                owner = Owner(first_name=first_name, middle_name=middle_name, last_name=last_name, email_address=email_address, gender=gender,
                date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state)
                owner.set_password(password)  # This hashes the password before saving
                owner.save()

            elif type_of_user == "Tenant":
                # save the data to the database
                tenant = Tenant(first_name=first_name, middle_name=middle_name, last_name=last_name, email_address=email_address, gender=gender,
                                date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state, password=password)
                tenant.set_password(password)  # This hashes the password before saving
                tenant.save()
            else:
                # return error message
                messages.error(request, "Invalid type of user")
                return render(request, "accounts_app/register.html")
            
            # return success message
            messages.success(request, "Registration successful")
            return redirect("accounts_app:login")
        else:
            # return error message
            messages.error(request, "Password and Confirm Password do not match")
            return render(request, "accounts_app/register.html")

    return render(request, "accounts_app/register.html")





############################# Profile info #############################

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
        user.email = request.POST.get('email')
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
            # Save the profile to update the image path
            profile.save()
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('accounts_app:owner_profile' if user_type == 'owner' else 'accounts_app:tenant_profile')

    return render(request, 'accounts_app/edit_profile.html', {
        'user': user,
        'profile': profile,
        'user_type': user_type
    })

# def owner_profile_view(request):
#     user_id = request.session.get('user_id')
#     user = get_object_or_404(Owner, id=user_id)
#     profile, created = Profile.objects.get_or_create(owner=user)
#     return render(request, 'accounts_app/owner_profile.html', {
#         'user': user,
#         'profile': profile,
#         'user_type' : 'owner'
#     })

# def tenant_profile_view(request):
#     user_id = request.session.get('user_id')
#     user = get_object_or_404(Tenant, id=user_id)
#     profile, created = Profile.objects.get_or_create(tenant=user)
#     return render(request, 'accounts_app/tenant_profile.html', {
#         'user': user,
#         'profile': profile,
#         'user_type' : 'tenant'
#     })

# def edit_profile_view(request, id, user_type):
#     model_dict = {'owner': Owner, 'tenant': Tenant}
#     model = model_dict.get(user_type)
#     if not model:
#         return redirect('listings_app:home')

#     user = get_object_or_404(model, id=id)
#     content_type = ContentType.objects.get_for_model(user)
#     profile, created = Profile.objects.get_or_create(person_type=content_type, person_id=user.id)

#     if request.method == 'POST':
#         user.first_name = request.POST.get('first_name')
#         user.middle_name = request.POST.get('middle_name', '')  # Default to empty string if not provided
#         user.last_name = request.POST.get('last_name')
#         user.email = request.POST.get('email')
#         user.gender = request.POST.get('gender')
#         user.date_of_birth = request.POST.get('date_of_birth')
#         user.phone_number = request.POST.get('phone_number')
#         user.address = request.POST.get('address')
#         user.state = request.POST.get('state')
#         user.occupation = request.POST.get('occupation')
#         user.save()
#         profile.bio = request.POST.get('bio')
#         profile.facebook_link = request.POST.get('facebook_link')
#         profile.tiktok_link = request.POST.get('tiktok_link')
#         profile.youtube_link = request.POST.get('youtube_link')
    
#         if 'profile_picture' in request.FILES:
#             profile.image = request.FILES['profile_picture']
#         profile.save()
#         messages.success(request, "Profile updated successfully!")
#         return redirect('accounts_app:owner_profile' if user_type == 'owner' else 'accounts_app:tenant_profile')
#     return render(request, 'accounts_app/edit_profile.html', {
#         'user': user,
#         'profile': profile,
#         'user_type': user_type
#     })





############################# login_view info #############################
def login_view(request):
    if request.method == "POST":
        email_address = request.POST.get("type_email").strip()
        password = request.POST.get("type_password").strip()
        type_of_user = request.POST.get("role").strip().capitalize()
        
        if type_of_user:
            user = None
            if type_of_user == "Owner":
                user = Owner.objects.filter(email_address=email_address).first()
            elif type_of_user == "Tenant":
                user = Tenant.objects.filter(email_address=email_address).first()
            # Continue for other types

            # check if the input has empty fields
            if not email_address or not password:
                messages.error(request, "Please fill in all fields")
                return render(request, 'accounts_app/login.html')
            if user and user.check_password(password):
                login(request, user)
                request.session['user_id'] = user.id
                request.session['type_of_user'] = type_of_user
                messages.success(request, "Login successful")
                return redirect(get_redirect_url(user))
            else:
                messages.error(request, "Invalid email address or password")

        else:
            messages.error(request, "Please select a role.")
            return render(request, 'accounts_app/login.html')
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



############################# Change password info #############################


# change_password_view
def change_password_view(request, id):
    user_id = request.session.get('user_id')
    if user_id:
        
        user = Owner.objects.filter(id=user_id).first() or Tenant.objects.filter(id=user_id).first()  # Extend for other types
        if user:
            if request.method == "POST":
                old_password = request.POST.get("current_password")
                new_password = request.POST.get("new_password")
                confirm_password = request.POST.get("confirm_password")

                if user.check_password(old_password):
                    if new_password == confirm_password:
                        if not user.check_password(new_password): # Check if new password is different from the old one
                            user.set_password(new_password)
                            user.save()
                            update_session_auth_hash(request, user) # Update the session with the new password
                            messages.success(request, "Password updated successfully")
                            return redirect(get_redirect_url(user))
                        else:
                            messages.error(request, "New password should be different from the old one")
                    else:
                        messages.error(request, "New password and confirm password do not match")
                else:
                    messages.error(request, "Current password is incorrect")
            else:
                pass
        else:
            messages.error(request, "User not found")
    else:
        messages.warning(request, "Please login to change your password.")
    return render(request, "accounts_app/change_password.html", {'id': user_id})


# change_password_redirect_view
def change_password_redirect_view(request):
    # Assuming request.session.user_id contains the correct user ID
    user_id = request.session.get('user_id')
    if user_id:
        return redirect('accounts_app:change_password', id=user_id)
    else:
        # Handle the case where user_id is not set in session
        return redirect('accounts_app:login')  # or wherever you want to redirect

############################# Logout view info #############################
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("accounts_app:login")



############################# reset_password_view info #############################
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
            user = user_model.objects.filter(id=user_id, email_address=email).first()
            if user:
                send_reset_email(user, user_type, request)
                return redirect('accounts_app:email_sent_confirmation')
            else:
                messages.error(request, "Invalid email address")
        else:
            messages.error(request, "Invalid user type")
    return render(request, 'accounts_app/reset_password_modal.html')


            



def send_reset_email(user, user_role, request):
    # Generate a reset URL with the user's ID
    reset_path = reverse('accounts_app:password_reset_form', args=[user.id, user_role])
    reset_url = request.build_absolute_uri(reset_path)
    subject = "Password Reset Requested"
    message = f"Hi {user.first_name},\n\nYou have requested to reset your password as a {user_role}.\nPlease click on the following link to reset your password:\n{reset_url}\n\nIf you did not make this request, please ignore this email and ensure your account is secure."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email_address]
    send_mail(subject, message, email_from, recipient_list)
    return redirect('accounts_app:password_reset_done')



def password_reset_form(request, user_id, user_type):
    # Map user_type to the correct model
    model_map = {
        'Owner': Owner,
        'Tenant': Tenant,
    }
    user_model = model_map.get(user_type)
    user = get_object_or_404(user_model, id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if password is empty
        if not password or not confirm_password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'accounts_app/password_reset_form.html', {'user_id': user_id, 'user_type': user_type})
        # Check if new password is the same as the old
        if check_password(password, user.password):
            messages.error(request, "New password cannot be the same as the old password.")
            return render(request, 'accounts_app/password_reset_form.html', {'user_id': user_id, 'user_type': user_type})
        
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('accounts_app:password_reset_done')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'accounts_app/password_reset_form.html', {'user_id': user_id, 'user_type': user_type})


def password_reset_done(request):
    return render(request, 'accounts_app/password_reset_done.html')


def email_sent_confirmation(request):
    return render(request, 'accounts_app/email_sent_confirmation.html')