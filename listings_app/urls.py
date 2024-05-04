from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "listings_app"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("property_details/", views.property_details_view, name="property_details"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("search/", views.search_view, name="search"),

]