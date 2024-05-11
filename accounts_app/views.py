from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Owner, Tenant
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash

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
        type_of_user = request.POST.get("type_of_user")
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm_password").strip()
        

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





############################# profile info #############################

# owner_profile_view
def owner_profile_view(request):

    return render(request, "accounts_app/owner_profile.html", {})  # render owner profile page

# user_profile_view
def user_profile_view(request):
    return render(request, "accounts_app/user_profile.html", {})  # render user profile page


# edit_profile_view
def edit_profile_view(request, slug):
    return redirect(request, "accounts_app/edit_profile.html", {}) # render edit profile page




############################# login_view info #############################
def login_view(request):
    if request.method == "POST":
        email_address = request.POST.get("type_email").strip()
        password = request.POST.get("type_password").strip()
        type_of_user = request.POST.get("role").strip()

        user = None
        if type_of_user == "Owner":
            user = Owner.objects.filter(email_address=email_address).first()
        elif type_of_user == "Tenant":
            user = Tenant.objects.filter(email_address=email_address).first()
        # Continue for other types

        if user and user.check_password(password):
            login(request, user)
            request.session['user_id'] = user.id
            messages.success(request, "Login successful")
            return redirect(get_redirect_url(user))
        else:
            messages.error(request, "Invalid email address or password")
    return render(request, "accounts_app/login.html")




############################# Change password info #############################

# get_redirect_url
def get_redirect_url(user):
    """
    Simple function to determine the redirect URL based on user type.
    """
    if isinstance(user, Owner):
        return 'accounts_app:owner_profile'
    elif isinstance(user, Tenant):
        return 'accounts_app:user_profile'
    # Add checks for other user types as necessary
    # Example:
    # elif isinstance(user, Seller):
    #     return 'accounts_app:seller_profile'
    # elif isinstance(user, Buyer):
    #     return 'accounts_app:buyer_profile'
    return 'accounts_app:login'  # Default redirect



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
                messages.error(request, "Invalid request method")
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
def forgot_password_view(request):
    return render(request, "accounts_app/forget_password.html", ) # render reset password page



# 