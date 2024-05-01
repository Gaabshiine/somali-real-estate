from django.shortcuts import render, redirect

# Create your views here.

# prepare comments and for each view function that related to the urls



# login_view
def login_view(request):
    return render(request, "accounts_app/login.html", {})

# register_view
def register_view(request):
    return render(request, "accounts_app/register.html", {})




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
def edit_profile_view(request, id):
    return render(request, "accounts_app/edit_profile.html", {}) # render edit profile page


# change_password_view
def change_password_view(request, id):
    return render(request, "accounts_app/change_password.html", {}) # render change password page


# reset_password_view
def forgot_password_view(request, id):
    return render(request, "accounts_app/reset_password.html", ) # render reset password page



