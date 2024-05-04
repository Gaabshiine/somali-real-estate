from django.shortcuts import render

# Create your views here.

# property_list_view
def rental_list(request):
    return render(request, "rental_property_app/rental_property_list.html", {})

# add_view
def add_view(request):
    return render(request, "rental_property_app/add_property.html", {})

# edit_property
def edit_property(request, slug):
    return render(request, "rental_property_app/edit_property.html", {})

# delete_view
def delete_view(request, slug):
    return render(request, "rental_property_app/delete_property.html", {})

# assign_view
def assign_view(request):
    return render(request, "rental_property_app/assign_property.html", {})


# search_view
def search_view(request):
    return render(request, "rental_property_app/search.html", {})


