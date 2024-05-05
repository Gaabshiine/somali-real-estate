from django.contrib import admin
from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # admin login
    path("login/", views.admin_login, name="admin_login"),

    # admin profile
    path("admin_profile/", views.admin_profile, name="admin_profile"),

    # admin logout
    path("admin_logout/", views.admin_logout, name="admin_logout"),

    # admin change password
    path("admin_change_password/", views.admin_change_password, name="admin_change_password"),

    # register owner
    path("register_owner/", views.register_owner, name="register_owner"),

    # view all owners
    path("view_owners/", views.view_owners, name="view_owners"),

    # register tenant
    path("register_tenant/", views.register_tenant, name="register_tenant"),

    # view all tenants
    path("view_tenants/", views.view_tenants, name="view_tenants"),


    
    # view all blacklisted users
    path("view_blacklist/", views.view_blacklist, name="view_blacklist"),

    

    # path("add_property/", views.add_property, name="add_property"),
    # path("add_owner/", views.add_owner, name="add_owner"),
    # path("add_user/", views.add_user, name="add_user"),
    # path("add_agent/", views.add_agent, name="add_agent"),
    # path("add_admin/", views.add_admin, name="add_admin"),


    


]