from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "rental_property_app"

urlpatterns = [
    path("", views.rental_list, name="rental_property_list"),
    path("add_property/", views.add_view, name="add_property"),
    path("edit_property/<slug:slug>/", views.edit_property, name="edit_property"),
    path("delete_property/<slug:slug>/", views.delete_view, name="delete_property"),
    path("assign_property", views.assign_view, name="assign_property"),
    path("search/", views.search_view, name="search"),
]