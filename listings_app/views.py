from django.shortcuts import render
from accounts_app.models import Owner, Tenant


# Create your views here.

# sesson_view
def get_user_from_session(user_id, user_role):
    """
    Retrieve user object based on user ID and role stored in the session.
    """
    if user_role == 'owner':
        return Owner.objects.filter(id=user_id).first()
    elif user_role == 'tenant':
        return Tenant.objects.filter(id=user_id).first()
    return None

# home_view
def home_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    if user_id and user_role:
        # Assuming you have a method to get user based on role
        user = get_user_from_session(user_id, user_role)
        return render(request, 'listings_app/home.html', {'user': user})
    return render(request, 'listings_app/home.html')


# about_view
def about_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        return render(request, 'listings_app/about.html', {'user': user})
    return render(request, 'listings_app/about.html')


# contact_view
def contact_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        return render(request, 'listings_app/contact.html', {'user': user})
    return render(request, 'listings_app/contact.html')


# search_view
def search_view(request):
    return render(request, "listings_app/search.html", {})


# property_details_view
def property_details_view(request):
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')
    user = None
    if user_id and user_role:
        user = get_user_from_session(user_id, user_role)
        return render(request, 'listings_app/property_details.html', {'user': user})
    return render(request, "listings_app/property_details.html", {})