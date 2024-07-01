from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts_app.models import Owner, Tenant, Profile
from admin_dashboard.models import Admin
from rental_property_app.models import (Apartment, ApartmentFeature, Room, RoomInvoice, House, TenantIdentification,
                                        OwnerIdentification, RoomComplaints, TenantIdentification, RoomAssignment, HouseAssignment, RoomInvoice)

from accounts_app.utils import (register_user, update_user_profile, process_reset_password, display_send_reset_email, 
                                display_email_sent_confirmation, display_password_reset_form, display_password_reset_done)

from rental_property_app.utils import (create_apartment_util, update_apartment_util, create_room_util, edit_room_util, delete_room_util, update_house_util ,
                                       create_complaint_util, edit_complaint_util, update_invoice_status, create_house_util, create_invoice_util, 
                                       update_invoice_status)


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts_app.utils import get_user_by_uid, change_user_password



"""
Resuable functions

"""
def check_tenant_identification(request, tenant_id):
    try:
        tenant = get_object_or_404(Tenant, id=tenant_id)
        identification_exists = tenant.identification is not None
        return JsonResponse({'identification_exists': identification_exists})
    except Tenant.identification.RelatedObjectDoesNotExist:
        return JsonResponse({'identification_exists': False})






""" 
Start: This fuctnion contains a
list of functions that relates to the user registeration, login, logout, dashboard, 
view all users, delete users, view and edit user profile, reset password and change password 
"""

# ---------------------------------------------------> start: User Registeration(Tenats or Owners) <---------------------------------------------------
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
            return redirect("admin_dashboard:view_owners")

    return render(request, "admin_dashboard/user_registeration.html")
# ---------------------------------------------------> end: User Registeration(Tenats or Owners) <---------------------------------------------------


# ---------------------------------------------------> start: Admin Dashboard <---------------------------------------------------

def dashboard_view(request):
    user_id = request.session.get('admin_id')
    if not user_id:
        return redirect('admin_dashboard:admin_login')
    
    admin = get_object_or_404(Admin, id=user_id)
    profile, _ = Profile.objects.get_or_create(person_id=admin.id, person_type='admin')

    owners = Owner.objects.all().count()
    tenants = Tenant.objects.all().count()
    apartment_filter = Apartment.objects.filter(status='Vacant').count()
    rooms = Room.objects.filter(status='Vacant').count()
    house = House.objects.filter(status='Vacant').count()
    complaint_unresolved = RoomComplaints.objects.filter(complaint_status='Unresolved').count()

    current_month = datetime.now().month
    tenant_data = []
    owner_data = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    labels = []

    for i in range(6):
        month = (current_month - i - 1) % 12 + 1
        month_name = months[month - 1]
        labels.append(month_name)

        tenant_count = Tenant.objects.filter(created_at__month=month).count()
        owner_count = Owner.objects.filter(created_at__month=month).count()
        
        tenant_data.append(tenant_count)
        owner_data.append(owner_count)

    labels.reverse()
    tenant_data.reverse()
    owner_data.reverse()

    payment_data = [500, 1000, 750, 1200, 1100, 1500]
    complaints_data = [
        RoomComplaints.objects.filter(complaint_status='Unresolved').count(),
        RoomComplaints.objects.filter(complaint_status='In Progress').count(),
        RoomComplaints.objects.filter(complaint_status='Resolved').count()
    ]

    room = None
    room_id = request.GET.get('room_id')
    if room_id:
        room = get_object_or_404(Room, pk=room_id)

    context = {
        'admin': admin,
        'profile': profile,
        'owners': owners,
        'tenants': tenants,
        'apartment_count': apartment_filter,
        'rooms': rooms,
        'labels': labels,
        'tenant_data': tenant_data,
        'owner_data': owner_data,
        'payment_data': payment_data,
        'room': room,
        'complaints_data': complaints_data,
        'house': house,
        'complaint_unresolved': complaint_unresolved,
        
    }
    return render(request, 'admin_dashboard/dashboard_view.html', context)

# ---------------------------------------------------> end: Admin Dashboard <---------------------------------------------------


# ---------------------------------------------------> start: admin accounts(register/login/logout) <---------------------------------------------------
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

# ---------------------------------------------------> end: admin accounts(register/login/logout) <---------------------------------------------------





# ---------------------------------------------------> start: Change password <---------------------------------------------------
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

# ---------------------------------------------------> end: Change password <---------------------------------------------------



# ---------------------------------------------------> start: view all users(owners, tenants and admins) <---------------------------------------------------

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

# ---------------------------------------------------> end: view all users(owners, tenants and admins) <---------------------------------------------------



# ---------------------------------------------------> start: Delete admin(admin, owner, tenant) <---------------------------------------------------
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



# ---------------------------------------------------> end: Delete admin(admin, owner, tenant) <---------------------------------------------------


# ---------------------------------------------------> start: View and edit user(admin, owner, tenant) profile <---------------------------------------------------
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


# ---------------------------------------------------> end: View and edit user(admin, owner, tenant) profile <---------------------------------------------------



# ---------------------------------------------------> start: Password reset <---------------------------------------------------
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email1')
        
        if not email:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'admin_dashboard/reset_password_modal.html')

        user = Admin.objects.filter(email=email).first()
        if user:
            display_send_reset_email(user, 'Admin', request, 'admin_dashboard', 'email')
            return redirect('admin_dashboard:email_sent_confirmation')
        else:
            messages.error(request, "Invalid email address")
            return render(request, 'admin_dashboard/reset_password_modal.html')

    return render(request, 'admin_dashboard/reset_password_modal.html')

def password_reset_form(request, uidb64, token):
    app_name = 'admin_dashboard'
    template_name = 'admin_dashboard/password_reset_form.html'
    session_key = 'user_id'
    user_type = request.GET.get('user_type', 'Admin')  # Default to 'Admin' since we are handling admin reset
    return display_password_reset_form(request, uidb64, token, user_type, app_name, template_name, session_key)

def password_reset_done(request):
    return display_password_reset_done(request, 'admin_dashboard', 'admin_dashboard/password_reset_done.html', 'user_id')

def email_sent_confirmation(request):
    return display_email_sent_confirmation(request, 'admin_dashboard', 'admin_dashboard/email_sent_confirmation.html', 'user_id')
# ---------------------------------------------------> end: Password reset <---------------------------------------------------



""" 
End: Function that accounts for user and admin
"""




"""
Start: apartment and room related functions
"""

# ---------------------------------------------------> start: Apartment creation, update, delete and view <---------------------------------------------------
def check_owner_identification(request, owner_id):
    owner = get_object_or_404(Owner, id=owner_id)
    identification_exists = OwnerIdentification.objects.filter(owner=owner).exists()
    return JsonResponse({'identification_exists': identification_exists})

def create_apartment_admin(request):
    owners = Owner.objects.all()
    selected_owner_id = request.POST.get('owner_id')
    owner_identification_exists = False
    apartment = None
    form_data = request.POST if request.method == 'POST' else None

    if selected_owner_id:
        owner_identification_exists = OwnerIdentification.objects.filter(owner_id=selected_owner_id).exists()

        if request.method == 'POST':
            apartment = create_apartment_util(request)
            if apartment:
                messages.success(request, "Apartment created successfully!")
                return redirect('admin_dashboard:view_apartments')
            else:
                messages.error(request, "Failed to create apartment.")

    return render(request, 'admin_dashboard/admin_apartment_register.html', {
        'user_type': 'admin',
        'owners': owners,
        'selected_owner_id': selected_owner_id,
        'owner_identification_exists': owner_identification_exists,
        'apartment': apartment,
        'form_data': form_data
    })


# Update apartment view
def update_apartment_admin(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    owners = Owner.objects.all()  # Get all owners


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
                'user_type': 'admin',
                'owners': owners,
                'existing_images': apartment.images.all(),
                'features': features  # Pass features to the template
            })
    else:
        # Populate the form with existing data for GET request
        return render(request, 'admin_dashboard/admin_apartment_update.html', {
            'apartment': apartment,
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
    # Fetch owner for each apartment
    for apartment in apartments:
        apartment.owner = Owner.objects.get(id=apartment.owner_id)
    return render(request, 'admin_dashboard/view_apartments.html', {    
        'apartments': apartments
    })

# ---------------------------------------------------> end: Apartment creation, update, delete and view <---------------------------------------------------


# ---------------------------------------------------> start: Room creation, update, delete and view <---------------------------------------------------
# Create room for an apartment
def create_room_admin(request, apartment_id):
    apartment = get_object_or_404(Apartment, pk=apartment_id)
    if request.method == 'POST':
        room_data = {
            'room_name': request.POST.get('room_name'),
            'room_type': request.POST.get('room_type'),
            'floor_number': request.POST.get('floor_number'),
            'rent_amount': request.POST.get('rent_amount'),
            'deposit_amount': request.POST.get('deposit_amount'),
            'room_description': request.POST.get('room_description'),
        }
        room_image = request.FILES.get('room_image')
        room = create_room_util(apartment_id, room_data, room_image)
        if room:
            messages.success(request, "Room created successfully!")
            return redirect('admin_dashboard:create_room', apartment_id=apartment_id)
    
    rooms = Room.objects.filter(apartment=apartment).order_by('-created_at')
    return render(request, 'admin_dashboard/admin_apartment_room_reigister.html', {
        'apartment': apartment,
        'rooms': rooms
    })

# read all rooms in an apartment
def view_rooms(request, apartment_id):
    apartment = get_object_or_404(Apartment, pk=apartment_id)
    rooms = Room.objects.filter(apartment=apartment).order_by('-created_at')
    return render(request, 'admin_dashboard/view_rooms.html', {
        'apartment': apartment,
        'rooms': rooms
    })


# edit room for an apartment
def edit_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    rooms = Room.objects.filter(apartment=room.apartment).order_by('-created_at')
    apartment = room.apartment
    if request.method == 'POST':
        edit_room_util(room, request.POST, request.FILES)
        return redirect('admin_dashboard:view_rooms', apartment_id=apartment.id)
    return render(request, 'admin_dashboard/admin_apartment_room_update.html', {
        'room': room,
        'rooms': rooms,
        'apartment': apartment
    })

# delete room for an apartment
def delete_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    apartment_id = room.apartment.id
    delete_room_util(room)
    return redirect('admin_dashboard:view_rooms', apartment_id=apartment_id)

# ---------------------------------------------------> end: Room creation, update, delete and view <---------------------------------------------------



# ---------------------------------------------------> start: Room Assignments <---------------------------------------------------

def get_rooms(request, apartment_id):
    rooms = Room.objects.filter(apartment_id=apartment_id, status='Vacant').values('id', 'room_name')
    return JsonResponse({'rooms': list(rooms)})

def get_room_details(request, room_id):
    room = Room.objects.get(id=room_id)
    data = {
        'rent_amount': room.rent_amount,
        'deposit_amount': room.deposit_amount
    }
    return JsonResponse(data)

def assign_room(request):
    if request.method == 'POST':
        apartment_id = request.POST.get('apartment_id')
        room_id = request.POST.get('room_id')
        tenant_id = request.POST.get('tenant_id')
        move_in_date = request.POST.get('move_in_date')
        move_out_date = request.POST.get('move_out_date')

        # Validation
        errors = []
        if not apartment_id:
            errors.append('Apartment is required.')
        if not room_id:
            errors.append('Room is required.')
        if not tenant_id:
            errors.append('Tenant is required.')
        if not move_in_date:
            errors.append('Move-in date is required.')
        if not move_out_date:
            errors.append('Move-out date is required.')

        # Check for tenant identification fields if needed
        document_type = request.POST.get('document_type')
        identification_number = request.POST.get('identification_number')
        document_file = request.FILES.get('document_file')

        if not document_type and not identification_number and not document_file:
            errors.append('Identification details are required for new tenants.')

        if errors:
            apartments = Apartment.objects.filter(status='Vacant')
            tenants = Tenant.objects.all()
            return render(request, 'admin_dashboard/admin_apartment_room_assign_register.html', {
                'apartments': apartments,
                'tenants': tenants,
                'errors': errors
            })

        # Parse the dates
        move_in_date = datetime.strptime(move_in_date, "%Y-%m-%d").date()
        move_out_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()

        room = get_object_or_404(Room, id=room_id)
        tenant = get_object_or_404(Tenant, id=tenant_id)

        assignment = RoomAssignment(
            room=room,
            tenant=tenant,
            move_in_date=move_in_date,
            move_out_date=move_out_date
        )
        assignment.save()

        check_and_update_room_status(assignment)

        # Check if tenant identification exists and create if not
        if document_type and identification_number and document_file:
            TenantIdentification.objects.create(
                tenant=tenant,
                document_type=document_type,
                identification_number=identification_number,
                document_file=document_file
            )

        return redirect('admin_dashboard:view_room_assignments')

    apartments = Apartment.objects.filter(status='Vacant')
    tenants = Tenant.objects.all()

    return render(request, 'admin_dashboard/admin_apartment_room_assign_register.html', {
        'apartments': apartments,
        'tenants': tenants
    })



def check_and_update_room_status(assignment):
    today = timezone.now().date()
    move_out_date = assignment.move_out_date

    # Check if the move out date is within 5 days
    if move_out_date and (move_out_date - today).days <= 5 and (move_out_date - today).days >= 0:
        send_room_vacancy_notification(assignment.tenant)

    # Update the room status based on the move out date
    if move_out_date and move_out_date <= today:
        assignment.room.status = 'Vacant'
    else:
        assignment.room.status = 'Occupied'
    assignment.room.save()
    assignment.room.apartment.update_status()

def send_room_vacancy_notification(tenant):
    subject = "Upcoming Room Vacancy - Action Required"
    message = (
        f"Dear {tenant.first_name},\n\n"
        "We hope you have enjoyed your stay with us at Somali Real Estate. This is a friendly reminder that your current room assignment is set to end in 5 days.\n\n"
        "To ensure a smooth transition, please take the following actions:\n"
        "- Confirm your move-out date with our office.\n"
        "- If you wish to extend your stay, please contact us immediately to discuss your options.\n\n"
        "We are here to assist you with any questions or concerns you may have. Thank you for choosing Somali Real Estate, and we hope to continue serving your housing needs.\n\n"
        "Best regards,\n"
        "The Somali Real Estate Team"
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [tenant.email_address]
    send_mail(subject, message, email_from, recipient_list)

def view_room_assignments(request):
    assignments = RoomAssignment.objects.all()
    today = timezone.now().date()

    for assignment in assignments:
        move_out_date = assignment.move_out_date
        if move_out_date:
            days_until_move_out = (move_out_date - today).days
            if 0 <= days_until_move_out <= 5:
                assignment.warning_status = "Move-out Soon"
            elif move_out_date <= today:
                assignment.warning_status = "Past Move-out Date"
            else:
                assignment.warning_status = "OK"
        else:
            assignment.warning_status = "OK"

    return render(request, 'admin_dashboard/view_room_assignments.html', {'assignments': assignments, 'today': today})

def edit_room_assignment(request, assignment_id):
    assignment = get_object_or_404(RoomAssignment, pk=assignment_id)
    if request.method == 'POST':
        move_in_date = request.POST.get('move_in_date')
        move_out_date = request.POST.get('move_out_date')

        # Parse the date strings into datetime.date objects
        if move_in_date:
            move_in_date = datetime.strptime(move_in_date, "%Y-%m-%d").date()
        if move_out_date:
            move_out_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()

        assignment.move_in_date = move_in_date
        assignment.move_out_date = move_out_date
        assignment.save()


        check_and_update_room_status(assignment)

        return redirect('admin_dashboard:view_room_assignments')

    return render(request, 'admin_dashboard/admin_apartment_room_assign_update.html', {'assignment': assignment})


def delete_room_assignment(request, assignment_id):
    assignment = get_object_or_404(RoomAssignment, pk=assignment_id)
    room_id = assignment.room.id
    assignment.delete()
    update_room_status(room_id)
    return redirect('admin_dashboard:view_room_assignments')

def update_room_status(room_id):
    room = Room.objects.get(id=room_id)
    if room.assignments.filter(move_out_date__isnull=True).exists():
        room.status = 'Occupied'
    else:
        room.status = 'Vacant'
    room.save()
    room.apartment.update_status()

# ---------------------------------------------------> end: Room Assignments <---------------------------------------------------




# ---------------------------------------------------> start: Room Complaints <---------------------------------------------------
def view_complaints(request):
    # Fetch all complaints
    complaints = RoomComplaints.objects.all()

    # Fetch the room for each complaint
    for complaint in complaints:
        complaint.room = Room.objects.get(id=complaint.room_id)

    return render(request, 'admin_dashboard/view_complaints.html', {
        'complaints': complaints
    })


# Create a complaint for a room
def create_complaint(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tenants = Tenant.objects.all()

    if request.method == 'POST':
        create_complaint_util(room, request.POST, request.session)
        return redirect('admin_dashboard:view_complaints')
    
    return render(request, 'admin_dashboard/admin_apartment_room_compalint_register.html', {
        'room': room,
        'tenants': tenants
    })

# def login_view(request):
#     # ... your login logic ...
#     request.session['user_id'] = tenant.id  # Save tenant ID in session after successful login

# Edit a complaint for a room
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(RoomComplaints, pk=complaint_id)
    if request.method == 'POST':
        edit_complaint_util(complaint, request.POST)
        return redirect('admin_dashboard:view_complaints')
    return render(request, 'admin_dashboard/admin_apartment_room_complaint_update.html', {'complaint': complaint})

# Delete a complaint for a room
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(RoomComplaints, pk=complaint_id)
    room_id = complaint.room.id
    complaint.delete()
    return redirect('admin_dashboard:view_complaints')

# ---------------------------------------------------> end: Room Complaints <---------------------------------------------------


# ---------------------------------------------------> start: Assingning Invoices room  <---------------------------------------------------






def create_invoice(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tenants = Tenant.objects.all()
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        amount_due = float(request.POST.get('amount_due'))
        amount_paid = float(request.POST.get('amount_paid'))
        invoice_date = request.POST.get('invoice_date')
        tenant = get_object_or_404(Tenant, id=tenant_id)
        create_invoice_util(room, tenant, amount_due, amount_paid, invoice_date)
        return redirect('admin_dashboard:view_invoices', room_id=room.id)
    return render(request, 'admin_dashboard/apartment_invoice_register.html', {'room': room, 'tenants': tenants})

def view_invoices(request, room_id):
    invoices = RoomInvoice.objects.filter(room_id=room_id)
    return render(request, 'admin_dashboard/view_invoices.html', {'invoices': invoices})

def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(RoomInvoice, pk=invoice_id)
    if request.method == 'POST':
        invoice.amount_due = float(request.POST.get('amount_due'))
        invoice.amount_paid = float(request.POST.get('amount_paid'))
        invoice.invoice_date = request.POST.get('invoice_date')
        invoice.save()
        update_invoice_status(invoice.id)
        return redirect('admin_dashboard:view_invoices', room_id=invoice.room.id)
    return render(request, 'admin_dashboard/edit_invoice.html', {'invoice': invoice})

def select_room_for_invoice(request):
    apartments = Apartment.objects.all()
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        return redirect('admin_dashboard:create_invoice', room_id=room_id)
    return render(request, 'admin_dashboard/admin_select_room_for_invoice.html', {'apartments': apartments})

def select_room_for_view_invoice(request):
    apartments = Apartment.objects.all()
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        return redirect('admin_dashboard:view_invoices', room_id=room_id)
    return render(request, 'admin_dashboard/admin_select_room_for_view_invoice.html', {'apartments': apartments})


# ---------------------------------------------------> end: Room Invoices <---------------------------------------------------

""" 
End: apartment and room related functions
"""




"""
Start: Manages houses related functions
"""



# ---------------------------------------------------> start: House creation, update, delete and view <---------------------------------------------------

def create_house_admin(request):


    owners = Owner.objects.all()
    selected_owner_id = request.POST.get('owner_id')
    owner_identification_exists = False
    house = None

    form_data = request.POST if request.method == 'POST' else None

    if selected_owner_id:
        owner_identification_exists = OwnerIdentification.objects.filter(owner_id=selected_owner_id).exists()

    if request.method == 'POST':

        house = create_house_util(request)
        if house:
            messages.success(request, "House created successfully!")
            return redirect('admin_dashboard:view_houses')
        
    
    return render(request, 'admin_dashboard/admin_house_register.html', {
        'user_type': 'admin',
        'owners': owners,
        'selected_owner_id': selected_owner_id,
        'owner_identification_exists': owner_identification_exists,
        'house': house,
        'form_data': form_data
    })

def update_house_admin(request, house_id):
    house = get_object_or_404(House, id=house_id)
    owners = Owner.objects.all()

    if request.method == 'POST':
        updated_house = update_house_util(request, house_id)
        if updated_house:
            return redirect('admin_dashboard:view_houses')
        else:
            messages.error(request, "Failed to update house.")
            return render(request, 'admin_dashboard/admin_house_update.html', {
                'house': house,
                'user_type': 'admin',
                'owners': owners,
                'existing_images': house.images.all()
            })
    else:
        return render(request, 'admin_dashboard/admin_house_update.html', {
            'house': house,
            'user_type': 'admin',
            'owners': owners,
            'existing_images': house.images.all()
        })

def view_houses(request):
    houses = House.objects.all()
    for house in houses:
        house.owner = Owner.objects.get(id=house.owner_id)
    return render(request, 'admin_dashboard/view_houses.html', {    
        'houses': houses
    })

def delete_house_admin(request, house_id):
    house = get_object_or_404(House, id=house_id)
    house.delete()
    messages.success(request, "House successfully deleted.")
    return redirect('admin_dashboard:view_houses')

# ---------------------------------------------------> End: House creation, update, delete and view <---------------------------------------------------


# ---------------------------------------------------> Start: House Assignments <---------------------------------------------------

def get_house_details(request, house_id):
    house = get_object_or_404(House, id=house_id)
    data = {
        'rent_amount': house.rent_amount,
        'deposit_amount': house.deposit_amount
    }
    return JsonResponse(data)

def assign_house(request):
    if request.method == 'POST':
        house_id = request.POST.get('house_id')
        tenant_id = request.POST.get('tenant_id')
        move_in_date = request.POST.get('move_in_date')
        move_out_date = request.POST.get('move_out_date')
        
        errors = []

        if not house_id:
            errors.append("House is required.")
        if not tenant_id:
            errors.append("Tenant is required.")
        if not move_in_date:
            errors.append("Move-in date is required.")
        if not move_out_date:
            errors.append("Move-out date is required.")

        if errors:
            houses = House.objects.filter(status='Vacant')
            tenants = Tenant.objects.all()
            return render(request, 'admin_dashboard/admin_house_assign_register.html', {'houses': houses, 'tenants': tenants, 'errors': errors})

        # Parse the dates
        move_in_date = datetime.strptime(move_in_date, "%Y-%m-%d").date()
        move_out_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()

        house = get_object_or_404(House, id=house_id)
        tenant = get_object_or_404(Tenant, id=tenant_id)

        assignment = HouseAssignment(
            house=house,
            tenant=tenant,
            move_in_date=move_in_date,
            move_out_date=move_out_date
        )
        assignment.save()

        check_and_update_house_status(assignment)

        return redirect('admin_dashboard:view_house_assignments')

    houses = House.objects.filter(status='Vacant')
    tenants = Tenant.objects.all()
    return render(request, 'admin_dashboard/admin_house_assign_register.html', {'houses': houses, 'tenants': tenants})



def edit_house_assignment(request, assignment_id):
    assignment = get_object_or_404(HouseAssignment, pk=assignment_id)
    if request.method == 'POST':
        move_in_date = request.POST.get('move_in_date')
        move_out_date = request.POST.get('move_out_date')

        # Parse the dates
        move_in_date = datetime.strptime(move_in_date, "%Y-%m-%d").date()
        move_out_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()

        assignment.move_in_date = move_in_date
        assignment.move_out_date = move_out_date
        assignment.save()

        check_and_update_house_status(assignment, send_email=False)

        return redirect('admin_dashboard:view_house_assignments')

    return render(request, 'admin_dashboard/admin_house_assign_update.html', {'assignment': assignment})

def check_and_update_house_status(assignment, send_email=False):
    today = timezone.now().date()
    move_out_date = assignment.move_out_date

    # Check if the move out date is within 5 days
    if move_out_date and (move_out_date - today).days <= 5 and (move_out_date - today).days >= 0:
        if send_email:
            send_house_vacancy_notification(assignment.tenant)

    # Update the house status based on the move out date
    if move_out_date and move_out_date <= today:
        assignment.house.status = 'Vacant'
    else:
        assignment.house.status = 'Occupied'
    assignment.house.save()

def send_house_vacancy_notification(tenant):
    subject = "Upcoming House Vacancy - Action Required"
    message = (
        f"Dear {tenant.first_name},\n\n"
        "We hope you have enjoyed your stay with us at Somali Real Estate. This is a friendly reminder that your current room assignment is set to end in 5 days.\n\n"
        "To ensure a smooth transition, please take the following actions:\n"
        "- Confirm your move-out date with our office.\n"
        "- If you wish to extend your stay, please contact us immediately to discuss your options.\n\n"
        "We are here to assist you with any questions or concerns you may have. Thank you for choosing Somali Real Estate, and we hope to continue serving your housing needs.\n\n"
        "Best regards,\n"
        "The Somali Real Estate Team"
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [tenant.email_address]
    send_mail(subject, message, email_from, recipient_list)

def view_house_assignments(request):
    assignments = HouseAssignment.objects.all()
    today = timezone.now().date()
    for assignment in assignments:
        check_and_update_house_status(assignment)
        # Calculate the warning status
        assignment.warning_status = 'OK'
        if assignment.move_out_date:
            days_to_move_out = (assignment.move_out_date - today).days
            if 0 <= days_to_move_out <= 5:
                assignment.warning_status = 'Move-out Soon'
            elif days_to_move_out < 0:
                assignment.warning_status = 'Past Move-out Date'
    
    return render(request, 'admin_dashboard/view_house_assignments.html', {'assignments': assignments, 'today': today})


def delete_house_assignment(request, assignment_id):
    assignment = get_object_or_404(HouseAssignment, pk=assignment_id)
    house_id = assignment.house.id
    assignment.delete()
    update_house_status(house_id)
    return redirect('admin_dashboard:view_house_assignments')

def update_house_status(house_id):
    house = House.objects.get(id=house_id)
    if house.assignments.filter(move_out_date__isnull=True).exists():
        house.status = 'Occupied'
    else:
        house.status = 'Vacant'
    house.save()


# ---------------------------------------------------> End: House Assignments <---------------------------------------------------

"""
End: Manages houses related functions
"""


