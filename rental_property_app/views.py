from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from accounts_app.models import Owner, Profile
from .utils import validate_video_duration, update_apartment_status, create_apartment_util
from django.contrib import messages


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



# def add_view(request):
#     user_id = request.session.get('user_id')
#     owner = get_object_or_404(Owner, id=user_id)
#     profile, _ = Profile.objects.get_or_create(person_id=owner.id, person_type='owner')
#     return render(request, "rental_property_app/add_property.html", {
#         'user': owner,
#         'profile': profile,
#         'user_type': 'owner'
#     })

# # edit_property
# def edit_property(request, slug):
#     return render(request, "rental_property_app/edit_property.html", {})

# # delete_view
# def delete_view(request, slug):
#     return render(request, "rental_property_app/delete_property.html", {})

# # assign_view
# def assign_view(request):
#     return render(request, "rental_property_app/assign_property.html", {})


# # search_view
# def search_view(request):
#     return render(request, "rental_property_app/search.html", {})


