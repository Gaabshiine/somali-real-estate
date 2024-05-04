from django.shortcuts import render

# Create your views here.


# home_view
def home_view(request):
    return render(request, "listings_app/home.html", {})


# about_view
def about_view(request):
    return render(request, "listings_app/about.html", {})


# contact_view
def contact_view(request):
    return render(request, "listings_app/contact.html", {})


# search_view
def search_view(request):
    return render(request, "listings_app/search.html", {})


# property_details_view
def property_details_view(request):
    return render(request, "listings_app/property_details.html", {})