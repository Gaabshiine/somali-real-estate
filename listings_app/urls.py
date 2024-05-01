from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "listings_app"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
]