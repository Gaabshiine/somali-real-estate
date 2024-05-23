from django.shortcuts import render
from accounts_app.models import Owner, Tenant, Profile


# Create your views here.

#################################### starts Helper Functions ####################################

def get_user_from_session(user_id, user_role):
    """
    Retrieve user object based on user ID and role stored in the session.
    """
    if user_role == 'owner':
        return Owner.objects.filter(id=user_id).first()
    elif user_role == 'tenant':
        return Tenant.objects.filter(id=user_id).first()
    return None

#################################### ends Helper Functions ####################################







#################################### starts Home Views ####################################
def home_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        # Assuming you have a method to get user based on role
        user = get_user_from_session(user_id, user_role)
        # Fetch the profile details including the picture
        profile = Profile.objects.filter(person_id=user_id, person_type=user_role).first()
    else:
        profile = None
    return render(request, 'listings_app/home.html', {'user': user, 'profile': profile})


#################################### ends Home Views ####################################






#################################### starts About Views ####################################

def about_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        # Fetch the profile details including the picture
        profile = Profile.objects.filter(person_id=user_id, person_type=user_role).first()
    else:
        profile = None
    return render(request, 'listings_app/about.html', {'user': user, 'profile': profile})

#################################### ends About Views ####################################






#################################### starts Contact Views ####################################
def contact_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        profile = Profile.objects.filter(person_id=user_id, person_type=user_role).first()
    else:
        profile = None
    return render(request, 'listings_app/contact.html', {'user': user, 'profile': profile})


#################################### ends Contact Views ####################################



#################################### starts Search Views ####################################


def search_view(request):
    return render(request, "listings_app/search.html", {})


# property_details_view
def property_details_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        profile = Profile.objects.filter(person_id=user_id, person_type=user_role).first()
    else:
        profile = None
    return render(request, 'listings_app/property_details.html', {'user': user, 'profile': profile})


#################################### ends Search Views ####################################