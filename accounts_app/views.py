from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Owner, Tenant
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login





# Create your views here.



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
                               date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state, password=password)
                owner.save()
            elif type_of_user == "Tenant":
                # save the data to the database
                tenant = Tenant(first_name=first_name, middle_name=middle_name, last_name=last_name, email_address=email_address, gender=gender,
                                date_of_birth=date_of_birth, phone_number=phone_number, address=address, occupation=occupation, state=state, password=password)
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


# login_view
def login_view(request):
    if request.method == "POST":
        email_address = request.POST.get("type_email").strip()
        password = request.POST.get("type_password").strip()
        type_of_user = request.POST.get("role").strip()

        if type_of_user == "Owner":
            owner = Owner.objects.filter(email_address=email_address).first()
            if owner and owner.password == password:
                login(request, owner)
                request.session['user_id'] = owner.id
                messages.success(request, "Login successful")
                return redirect("accounts_app:owner_profile")
            else:
                messages.error(request, "Invalid email address or password")
        elif type_of_user == "Tenant":
            tenant = Tenant.objects.filter(email_address=email_address).first()
            if tenant and tenant.password == password:
                login(request, tenant)
                request.session['user_id'] = tenant.id
                messages.success(request, "Login successful")
                return redirect("accounts_app:user_profile")
            else:
                messages.error(request, "Invalid email address or password")
        else:
            messages.error(request, "Invalid type of user")
    
    return render(request, "accounts_app/login.html")

     

# logout_view
def logout_view(request):
    # remove the session
    Session.objects.all().delete()

     # return success message
    messages.success(request, "Logout successful")

    # return to the login page
    return redirect("accounts_app:login")



# owner_profile_view
def owner_profile_view(request):

    return render(request, "accounts_app/owner_profile.html", {})  # render owner profile page

# user_profile_view
def user_profile_view(request):
    return render(request, "accounts_app/user_profile.html", {})  # render user profile page


# edit_profile_view
def edit_profile_view(request, slug):
    return redirect(request, "accounts_app/edit_profile.html", {}) # render edit profile page


# change_password_view
def change_password_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        if request.method == "POST":
            old_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            owner = Owner.objects.filter(id=user_id).first()
            tenant = Tenant.objects.filter(id=user_id).first()

            if owner:
                if owner.check_password(old_password):
                    if new_password == confirm_password:
                        owner.set_password(new_password)
                        owner.save()
                        messages.success(request, "Password updated successfully")
                        return redirect("accounts_app:owner_profile")
                    else:
                        messages.error(request, "New password and confirm password do not match")
                else:
                    messages.error(request, "Current password is incorrect")
            elif tenant:
                if tenant.check_password(old_password):
                    if new_password == confirm_password:
                        tenant.set_password(new_password)
                        tenant.save()
                        messages.success(request, "Password updated successfully")
                        return redirect("accounts_app:user_profile")
                    else:
                        messages.error(request, "New password and confirm password do not match")
                else:
                    messages.error(request, "Current password is incorrect")
            else:
                messages.error(request, "User not found")
    else:
        messages.warning(request, "Please login to change your password.")
        return redirect(reverse('accounts_app:login'))
    
    return render(request, "accounts_app/change_password.html", {})



# reset_password_view
def forgot_password_view(request):

    return render(request, "accounts_app/forget_password.html", ) # render reset password page



