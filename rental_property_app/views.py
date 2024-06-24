from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from accounts_app.models import Owner, Profile
from .utils import validate_video_duration, update_apartment_status, create_apartment_util, update_apartment_util
from django.contrib import messages
from .models import Apartment, ApartmentFeature, ApartmentImages


# create_apartment view
def create_apartment(request):
    apartment = create_apartment_util(request)
    owner_id = request.session.get('user_id')
    owner = get_object_or_404(Owner, id=owner_id)
    profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')

    if apartment:
        # Redirect on success to home page in accouont app
        return redirect('listings_app:home')

    else:
        return render(request, 'rental_property_app/add_property.html', {
        'user': owner,
        'profile': profile,
        'user_type': 'owner'
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