from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Owner, Tenant

# Create your views here.

# prepare comments and for each view function that related to the urls





def register_view(request):
    if request.method == "POST":
        # get the form data
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        email_address = request.POST.get("type_email")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        occupation = request.POST.get("occupation")
        state = request.POST.get("state")
        type_of_user = request.POST.get("type_of_user")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        

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
        # get the form data
        email_address = request.POST.get("type_email").strip()  # Remove leading and trailing whitespace
        password = request.POST.get("type_password").strip()  # Remove leading and trailing whitespace
        type_of_user = request.POST.get("role").strip()  # Remove leading and trailing whitespace

        # check the type of user
        if type_of_user == "Owner":
            # check if the user exists
            owner = Owner.objects.filter(email_address=email_address, password=password).first()
            print(owner)
            if owner:
                return redirect("accounts_app:owner_profile")
            else:
                messages.error(request, "Invalid email or password")
                return render(request, "accounts_app/login.html", {})
        elif type_of_user == "Tenant":
            # check if the user exists
            tenant = Tenant.objects.filter(email_address=email_address, password=password).first()
            if tenant:
                return redirect("accounts_app:user_profile")
            else:
                messages.error(request, "Invalid email or password")
                return render(request, "accounts_app/login.html", {})
        else:
            messages.error(request, "Invalid type of user")
            return render(request, "accounts_app/login.html", {})
    return render(request, "accounts_app/login.html", {})

# logout_view
def logout_view(request):
    return redirect("listings_app:home")  # redirect to home page


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
def change_password_view(request, slug):
    return render(request, "accounts_app/change_password.html", {}) # render change password page


# reset_password_view
def forgot_password_view(request):
    return render(request, "accounts_app/forget_password.html", ) # render reset password page



