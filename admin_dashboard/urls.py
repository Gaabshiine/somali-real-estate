from django.contrib import admin
from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('profile/', views.admin_profile_view, name='admin_profile'),
    path("change_password/", views.admin_change_password, name="admin_change_password"),
    # register onwer and tentant
    path("user_register/", views.register_view, name="user_registration"),
    # view all owners, tenants and admins
    path("view_owners/", views.view_owners, name="view_owners"),
    path("view_tenants/", views.view_tenants, name="view_tenants"),
    path("view_admins/", views.view_admins, name="view_admins"),
    
    # delete the admin, owner and tenant
    path('delete_admin/', views.delete_admin, name='delete_admin'),
    path('delete_owner/', views.delete_owner, name='delete_owner'),
    path('delete_tenant/', views.delete_tenant, name='delete_tenant'),

    # # edit owner
    # path("edit_owner/<int:owner_id>/", views.edit_owner, name="edit_owner"),

    # # delete owner
    # path("delete_owner/<int:owner_id>/", views.delete_owner, name="delete_owner"),


    # view all blacklisted users
    path("view_blacklist/", views.view_blacklist, name="view_blacklist"),
]