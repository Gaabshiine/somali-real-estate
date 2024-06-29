from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from accounts_app.models import Owner, Profile
from .utils import create_apartment_util, update_apartment_util
from django.contrib import messages
from .models import Apartment, ApartmentFeature, ApartmentImages, OwnerIdentification, Room, RoomInvoice


# create_apartment view

def create_apartment(request):
    owners = Owner.objects.all()  # Fetch all owners for the form dropdown
    selected_owner_id = request.POST.get('owner_id')
    owner_identification_exists = False
    apartment = None
    form_data = request.POST if request.method == 'POST' else None  # Initialize form_data appropriately

    if selected_owner_id:
        # Check if the selected owner has existing identification details
        owner_identification_exists = OwnerIdentification.objects.filter(owner_id=selected_owner_id).exists()

        if request.method == 'POST' and 'create_apartment' in request.POST:
            apartment = create_apartment_util(request)
            if apartment:
                messages.success(request, "Apartment created successfully!")
                return redirect('admin_dashboard:view_apartments')
            else:
                messages.error(request, "Failed to create apartment.")

    # Render the template, now form_data is always defined
    return render(request, 'admin_dashboard/admin_apartment_register.html', {
        'user_type': 'admin',
        'owners': owners,
        'selected_owner_id': selected_owner_id,
        'owner_identification_exists': owner_identification_exists,
        'apartment': apartment,
        'form_data': form_data  # Pass the entire form data back to the template safely
    })


# Update apartment view
def update_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    owner_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=owner_id)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')

    # Fetch the features
    try:
        features = ApartmentFeature.objects.get(apartment=apartment)
    except ApartmentFeature.DoesNotExist:
        features = None

 
    


    if request.method == 'POST':
        updated_apartment = update_apartment_util(request, apartment_id)
        if updated_apartment:
            return redirect('listings_app:home')
        else:
            messages.error(request, "Failed to update apartment.")
            return render(request, 'rental_property_app/update_property.html', {
                'apartment': apartment,
                'user': owner,
                'profile': profile,
                'user_type': 'owner',
                'existing_images': apartment.images.all(),
                'features': features  # Pass features to the template
            })
    else:
        # Populate the form with existing data for GET request
        return render(request, 'rental_property_app/update_property.html', {
            'apartment': apartment,
            'user': owner,
            'profile': profile,
            'user_type': 'owner',
            'existing_images': apartment.images.all(),
            'features': features  # Pass features to the template
        })
    

# Delete apartment view
def delete_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    owner_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=owner_id)

    if request.method == 'POST':
        apartment.delete()
        messages.success(request, "Apartment deleted successfully.")
        return redirect('rental_property_app:my_apartments')

    return render(request, 'rental_property_app/apartment_delete.html', {
        'apartment': apartment,
        'user': owner,
        'profile': Profile.objects.get(person_id=owner.id, person_type='owner')
    })


# list all apartments that you own
def my_apartments(request):
    owner_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=owner_id)
    apartments = Apartment.objects.filter(owner=owner)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')
    
    return render(request, 'rental_property_app/apartment_list.html', {
        'apartments': apartments,
        'user': owner,
        'profile': profile,
        'user_type': 'owner'
    })



