from django.shortcuts import render,redirect
from django.urls import reverse

# Create your views here.


def dashboard_view(request):
    return render(request, "admin_dashboard/dashboard_view.html", {})


def admin_login(request):
    return render(request, "admin_dashboard/admin_login.html", {})


def admin_profile(request):
    return render(request, "admin_dashboard/admin_profile.html", {})


def admin_logout(request):
    return render(request, "admin_dashboard/admin_logout.html", {})


def admin_change_password(request):
    return render(request, "admin_dashboard/admin_change_password.html", {})


def register_owner(request):
    return render(request, "admin_dashboard/register_owner.html", {})


def view_owners(request):
    return render(request, "admin_dashboard/view_owners.html", {})


def register_tenant(request):
    return render(request, "admin_dashboard/register_tenant.html", {})


def view_tenants(request):
    return render(request, "admin_dashboard/view_tenants.html", {})


def view_blacklist(request):
    return render(request, "admin_dashboard/view_blacklist.html", {})

