from django.contrib import messages
from django.shortcuts import redirect
from .models import Owner, Tenant
from django.core.mail import send_mail
from django.conf import settings

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

