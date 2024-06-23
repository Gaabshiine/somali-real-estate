import moviepy.editor as mp
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Apartment # Room, RoomInvoice

from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Owner, Apartment, ApartmentFeature, ApartmentImages, OwnerIdentification

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings


######################################################## create apartment Start ########################################################
def create_apartment_util(request):
    if request.method != 'POST':
        return None  # Only process POST requests
    
    # check empty fields but the image is only one is required and vedio is not required
    required_fields = ['apartment-name', 'year-built', 'area', 'district-located', 'location', 'description', 'img-1', 'document-type', 'identification-number', 'document-file']
    for field in required_fields:
        if not request.POST.get(field) and not request.FILES.get(field):
            messages.error(request, f"{field.replace('-', ' ').title()} is required.")
            return None
    
    # Try to get owner ID from session first, then from POST data if not found
    owner_id = request.session.get('user_id', None) or request.POST.get('owner-id')

    
    if not owner_id:
        messages.error(request, "Owner not specified.")
        return None
    
    owner = get_object_or_404(Owner, id=owner_id)

    apartment = Apartment(
        apartment_name=request.POST.get('apartment-name'),
        year_built=request.POST.get('year-built'),
        area=request.POST.get('area'),
        district_located=request.POST.get('district-located'),
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
        has_car_parking='car-parking' in request.POST,
        has_internet='internet' in request.POST,
        has_swimming_pool='swimming-pool' in request.POST,
        has_alarm='alarm' in request.POST,
        has_air_conditioner='air-conditioner' in request.POST
    )
    features.save()

    images_files = [request.FILES.get('img-1'), request.FILES.get('img-2'), request.FILES.get('img-3')]
    for img_file in images_files:
        if img_file:
            ApartmentImages.objects.create(apartment=apartment, image=img_file)

    # Handle owner identification document upload
    document_type = request.POST.get('document-type')
    identification_number = request.POST.get('identification-number')
    document_file = request.FILES.get('document-file')

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
    return apartment  # Return the apartment object upon successful creation

######################################################## create apartment End ########################################################




def validate_video_duration(video_path):
    """Validates the duration of a video file."""
    video = mp.VideoFileClip(video_path)
    if video.duration > 180:
        video.close()
        raise ValidationError("Video must not be longer than 3 minutes.")
    video.close()




def update_apartment_status(apartment_id):
    """Updates the status of an apartment based on the occupancy of its rooms."""
    apartment = Apartment.objects.get(pk=apartment_id)
    if apartment.room_set.filter(status='Vacant').exists():
        apartment.status = 'Vacant'
    else:
        apartment.status = 'Occupied'
    apartment.save()




# def update_room_status_on_assignment(room_id):
#     """Updates the status of a room based on current assignments."""
#     room = Room.objects.get(pk=room_id)
#     # Assuming a check for current date against move-in/out dates in assignments
#     active_assignments = room.assignments.filter(move_in_date__lte=timezone.now(), move_out_date__gte=timezone.now())
#     room.status = 'Occupied' if active_assignments.exists() else 'Vacant'
#     room.save()



# def update_invoice_status(invoice_id):
#     """Updates the status of an invoice based on payment details."""
#     invoice = RoomInvoice.objects.get(pk=invoice_id)
#     invoice.rest_amount = invoice.amount_due - invoice.amount_paid
#     if invoice.rest_amount == 0:
#         invoice.invoice_status = 'Paid'
#     elif invoice.rest_amount > 0 and invoice.amount_paid > 0:
#         invoice.invoice_status = 'Pending'
#     else:
#         invoice.invoice_status = 'Overdue'
#     invoice.save()
