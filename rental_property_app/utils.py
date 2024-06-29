import moviepy.editor as mp
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.core.mail import send_mail
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect


from django.shortcuts import get_object_or_404
from django.contrib import messages

from accounts_app.models import Owner
from .models import (Apartment, ApartmentFeature, ApartmentImages, OwnerIdentification, Room, RoomInvoice,
                      RoomComplaints, HouseInvoice, House, Tenant, TenantIdentification, HouseImage, RoomAssignment,
                      HouseAssignment)

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings




def validate_video_duration(video_path):
    """Validates the duration of a video file."""
    video = mp.VideoFileClip(video_path)
    if video.duration > 180:
        video.close()
        raise ValidationError("Video must not be longer than 3 minutes.")
    video.close()


# Check if the owner has an identification record
def check_owner_identification(request, owner_id):
    owner = get_object_or_404(Owner, id=owner_id)
    identification_exists = OwnerIdentification.objects.filter(owner=owner).exists()
    return JsonResponse({'identification_exists': identification_exists})

def create_apartment(request):
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




"""
Start: Manage apartment utility functions
"""

# -------------------------------------------------------------------> start: Create, and update apartment utility functions <------------------------------------------------
def create_apartment_util(request):
    if request.method != 'POST':
        return None  # Only process POST requests
    
    # check empty fields but the image is only one is required and vedio is not required
    required_fields = ['apartment_name', 'year_built', 'area', 'district_located', 'location', 'description', 'img_1']
    for field in required_fields:
        if not request.POST.get(field) and not request.FILES.get(field):
            return None
        
    
    
    # Try to get owner ID from session first, then from POST data if not found
    owner_id = request.session.get('user_id', None) or request.POST.get('owner_id')

    
    
    if not owner_id:
        messages.error(request, "Owner not specified.")
        return None
    
    owner = get_object_or_404(Owner, id=owner_id)

    

    apartment = Apartment(
        apartment_name=request.POST.get('apartment_name'),
        year_built=request.POST.get('year_built'),
        area=request.POST.get('area'),
        district_located=request.POST.get('district_located'),
        location=request.POST.get('location'),
        apartment_description=request.POST.get('description'),
        owner=owner,
        
    )

    video = request.FILES.get('video') 
    if video:
        # Handle video upload securely
        temp_file_path = default_storage.save('temp/' + video.name, ContentFile(video.read()))
        full_temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_path)

        try:
            validate_video_duration(full_temp_file_path)
            apartment.video = video
        finally:
            # Ensure the temporary file is removed after processing
            os.remove(full_temp_file_path)

    apartment.save()

    features = ApartmentFeature(
        apartment=apartment,
        has_gym='gym' in request.POST,
        has_car_parking='car_parking' in request.POST,
        has_internet='internet' in request.POST,
        has_swimming_pool='swimming_pool' in request.POST,
        has_alarm='alarm' in request.POST,
        has_air_conditioner='air_conditioner' in request.POST
    )
    features.save()

    images_files = [request.FILES.get('img_1'), request.FILES.get('img_2'), request.FILES.get('img_3')]
    for img_file in images_files:
        if img_file:
            ApartmentImages.objects.create(apartment=apartment, image=img_file)

    # Handling unique owner identification
    document_type = request.POST.get('document_type')
    identification_number = request.POST.get('identification_number')
    document_file = request.FILES.get('document_file')
    
    # Check for existing identification record
    if OwnerIdentification.objects.filter(document_type=document_type, identification_number=identification_number).exists():
        messages.error(request, f"Identification number already exists for {document_type}.")
        return None
    

    # Create or update owner identification
    OwnerIdentification.objects.update_or_create(
        owner=owner,
        defaults={
            'document_type': document_type,
            'identification_number': identification_number,
            'document_file': document_file
        }
    )

    messages.success(request, "Apartment created successfully!")
    return apartment


# Update apartment utility function
def update_apartment_util(request, apartment_id):
    if request.method != 'POST':
        return None  # Only process POST requests
    
    apartment = get_object_or_404(Apartment, id=apartment_id)
    
   

    owner_id = request.session.get('user_id', None) or request.POST.get('owner_id')
    if not owner_id:
        messages.error(request, "Owner not specified.")
        return None

    apartment.apartment_name = request.POST.get('apartment_name')
    apartment.year_built = request.POST.get('year_built')
    apartment.area = request.POST.get('area')
    apartment.district_located = request.POST.get('district_located')
    apartment.location = request.POST.get('location')
    apartment.apartment_description = request.POST.get('description')

    video = request.FILES.get('video')
    if video:
        temp_file_path = default_storage.save('temp/' + video.name, ContentFile(video.read()))
        full_temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_path)
        try:
            validate_video_duration(full_temp_file_path)
            apartment.video = video
        finally:
            os.remove(full_temp_file_path)

    apartment.save()

    ApartmentFeature.objects.update_or_create(
        apartment=apartment,
        defaults={
            'has_gym': 'gym' in request.POST,
            'has_car_parking': 'car_parking' in request.POST,
            'has_internet': 'internet' in request.POST,
            'has_swimming_pool': 'swimming_pool' in request.POST,
            'has_alarm': 'alarm' in request.POST,
            'has_air_conditioner': 'air_conditioner' in request.POST
        }
    )

    
    # Update apartment images
    ApartmentImages.objects.filter(apartment=apartment).delete()  # Remove existing images
    for img_file in request.FILES.getlist('images'):
        if img_file:
            ApartmentImages.objects.create(apartment=apartment, image=img_file)


    messages.success(request, "Apartment updated successfully!")
    return apartment

# -------------------------------------------------------------------> end: Create, and update apartment utility functions <------------------------------------------------    




# -------------------------------------------------------------------> start: create, edit, delete room utility functions <------------------------------------------------

# Create room for an apartment
def create_room_util(apartment_id, room_data, room_image=None):
    apartment = get_object_or_404(Apartment, pk=apartment_id)
    try:
        room = Room(
            room_name=room_data['room_name'],
            room_type=room_data['room_type'],
            floor_number=room_data['floor_number'],
            rent_amount=room_data['rent_amount'],
            deposit_amount=room_data['deposit_amount'],
            room_description=room_data.get('room_description', ''),
            room_image=room_image,
            apartment=apartment
        )
        room.save()
        return room
    except Exception as e:
        # Log the error
        return None


# edit room for an apartment
def edit_room_util(room, post_data, files_data):
    room.room_name = post_data.get('room_name', room.room_name)
    room.room_type = post_data.get('room_type', room.room_type)
    room.floor_number = post_data.get('floor_number', room.floor_number)
    room.rent_amount = post_data.get('rent_amount', room.rent_amount)
    room.deposit_amount = post_data.get('deposit_amount', room.deposit_amount)
    room.room_description = post_data.get('room_description', room.room_description)
    room.room_image = files_data.get('room_image', room.room_image)
    room.save()


# delete room for an apartment
def delete_room_util(room):
    apartment_id = room.apartment.id
    room.delete()
    return apartment_id

# -------------------------------------------------------------------> end: create, edit, delete room utility functions <------------------------------------------------




# -------------------------------------------------------------------> start: create, and edit complaint utility functions <------------------------------------------------
def create_complaint_util(room, post_data, session):
    tenant_id = session.get('user_id') or post_data.get('tenant_id')
    complaint = RoomComplaints(
        complaint_type=post_data.get('complaint_type'),
        complaint_status= post_data.get('complaint_status'),
        complaint_description=post_data.get('complaint_description'),
        room=room,
        tenant_id=tenant_id
    )
    complaint.save()
    return complaint


def edit_complaint_util(complaint, post_data):
    complaint.complaint_type = post_data.get('complaint_type', complaint.complaint_type)
    complaint.complaint_description = post_data.get('complaint_description', complaint.complaint_description)
    complaint.complaint_status = post_data.get('complaint_status', complaint.complaint_status)
    complaint.save()
    return complaint

# -------------------------------------------------------------------> end: create, and edit complaint utility functions <------------------------------------------------



"""
End: Manage apartment utility functions
"""



"""Start: Invoice apartment and house are related functions."""

def generate_unique_invoice_number():
    last_invoice = RoomInvoice.objects.all().order_by('id').last()
    if not last_invoice:
        return 'INV-0001'
    invoice_no = last_invoice.invoice_number
    invoice_int = int(invoice_no.split('INV-')[-1])
    new_invoice_int = invoice_int + 1
    new_invoice_no = 'INV-' + str(new_invoice_int).zfill(4)
    return new_invoice_no

def create_invoice_util(room, tenant, amount_due, amount_paid, invoice_date):
    rest_amount = amount_due - amount_paid
    if rest_amount == 0:
        invoice_status = 'Paid'
    elif amount_paid > 0 and rest_amount > 0:
        invoice_status = 'Pending'
    elif invoice_date < timezone.now().date():
        invoice_status = 'Overdue'
    else:
        invoice_status = 'Pending'

    invoice_number = generate_unique_invoice_number()
    invoice = RoomInvoice(
        invoice_number=invoice_number,
        amount_due=amount_due,
        amount_paid=amount_paid,
        rest_amount=rest_amount,
        invoice_status=invoice_status,
        tenant=tenant,
        room=room,
        invoice_date=invoice_date,
    )
    invoice.save()
    update_invoice_status(invoice.id)
    return invoice

def update_invoice_status(invoice_id):
    invoice = RoomInvoice.objects.get(id=invoice_id)
    invoice.rest_amount = invoice.amount_due - invoice.amount_paid
    if invoice.rest_amount == 0:
        invoice.invoice_status = 'Paid'
    elif invoice.amount_paid > 0 and invoice.rest_amount > 0:
        invoice.invoice_status = 'Pending'
    elif invoice.invoice_date < timezone.now().date():
        invoice.invoice_status = 'Overdue'
    invoice.save()

    # Send email notifications if needed
    if invoice.invoice_status == 'Overdue':
        subject = "Invoice Overdue"
        message = f"Dear {invoice.tenant.first_name},\n\nYour invoice {invoice.invoice_number} is overdue. Please make the payment as soon as possible.\n\nBest regards,\nSomali Real Estate Team"
    elif invoice.invoice_status == 'Pending' and (invoice.invoice_date - timezone.now().date()).days <= 5:
        subject = "Invoice Due Soon"
        message = f"Dear {invoice.tenant.first_name},\n\nYour invoice {invoice.invoice_number} is due in { (invoice.invoice_date - timezone.now().date()).days } days. Please make the payment before the due date.\n\nBest regards,\nSomali Real Estate Team"

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [invoice.tenant.email]
    send_mail(subject, message, email_from, recipient_list)




"""End: Invoice apartment and house are related functions."""






"""Start: Manage house utility functions"""


def create_house_util(request):

    if request.method != 'POST':
        return None  # Only process POST requests

    # Check for empty fields (not including the optional fields)
    required_fields = ['house_name', 'year_built', 'area', 'district_located', 'location', 'rent_amount', 'no_of_bathrooms', 'no_of_rooms']
    for field in required_fields:
        field_value = request.POST.get(field)
        if not field_value:
            return None

    # Get owner ID from session or POST data
    owner_id = request.session.get('user_id') or request.POST.get('owner_id')
    if not owner_id:
        messages.error(request, "Owner not specified.")
        return None

    owner = get_object_or_404(Owner, id=owner_id)


    # Create the house instance
    house = House(
        house_name=request.POST.get('house_name'),
        year_built=request.POST.get('year_built'),
        area=request.POST.get('area'),
        district_located=request.POST.get('district_located'),
        location=request.POST.get('location'),
        rent_amount=request.POST.get('rent_amount'),
        deposit_amount=request.POST.get('deposit_amount'),
        house_description=request.POST.get('house_description'),
        no_of_bathrooms=request.POST.get('no_of_bathrooms'),
        no_of_rooms=request.POST.get('no_of_rooms'),
        owner=owner
    )
    house.save()

    # Save house images if provided
    image_files = request.FILES.getlist('images')
    for image_file in image_files:
        HouseImage.objects.create(house=house, image=image_file)

    # Handling owner identification
    document_type = request.POST.get('document_type')
    identification_number = request.POST.get('identification_number')
    document_file = request.FILES.get('document_file')

    if document_type and identification_number and document_file:
        OwnerIdentification.objects.update_or_create(
            owner=owner,
            defaults={
                'document_type': document_type,
                'identification_number': identification_number,
                'document_file': document_file
            }
        )

    messages.success(request, "House created successfully!")
    return house



def update_house_util(request, house_id):
    if request.method != 'POST':
        return None

    house = get_object_or_404(House, id=house_id)

    owner_id = request.session.get('user_id', None) or request.POST.get('owner_id')
    if not owner_id:
        messages.error(request, "Owner not specified.")
        return None

    house.house_name = request.POST.get('house_name')
    house.year_built = request.POST.get('year_built')
    house.area = request.POST.get('area')
    house.district_located = request.POST.get('district_located')
    house.location = request.POST.get('location')
    house.rent_amount = request.POST.get('rent_amount')
    house.deposit_amount = request.POST.get('deposit_amount')
    house.no_of_bathrooms = request.POST.get('no_of_bathrooms')
    house.no_of_rooms = request.POST.get('no_of_rooms')
    house.house_description = request.POST.get('house_description')

    house.save()

    HouseImage.objects.filter(house=house).delete()
    for img_file in request.FILES.getlist('images'):
        if img_file:
            HouseImage.objects.create(house=house, image=img_file)

    messages.success(request, "House updated successfully!")
    return house



"""End: Manage house utility functions"""