from django.contrib import admin
from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # register onwer and tentant
    path("user_register/", views.register_view, name="user_registration"),


    # change passowrd
    path("change_password/", views.change_password_redirect_view, name="change_password_redirect"),
    path("change_password/<slug:uidb64>/<slug:token>/", views.change_password_view, name="change_password"),

    # profile of owner and tenant
    path("owner_profile/<int:id>/", views.owner_profile_view, name="owner_profile"),
    path("tenant_profile/<int:id>/", views.tenant_profile_view, name="tenant_profile"),
    path("admin_profile/<int:id>/", views.admin_profile_view, name="admin_profile"),


  


    # view all owners, tenants and admins
    path("view_owners/", views.view_owners, name="view_owners"),
    path("view_tenants/", views.view_tenants, name="view_tenants"),
    path("view_admins/", views.view_admins, name="view_admins"),
    
    # delete the admin, owner and tenant
    path('delete_admin/', views.delete_admin, name='delete_admin'),
    path('delete_owner/', views.delete_owner, name='delete_owner'),
    path('delete_tenant/', views.delete_tenant, name='delete_tenant'),


    path("reset_password/", views.reset_password, name="reset_password"),
    path("email_sent_confirmation/", views.email_sent_confirmation, name="email_sent_confirmation"),
    path("password_reset_done/", views.password_reset_done, name="password_reset_done"),
    path("password_reset_form/<uidb64>/<token>/<user_type>/", views.password_reset_form, name="password_reset_form"),


    

    # create apartment
    path("rent/apartment/create/", views.create_apartment_admin, name="create_apartment_admin"),


    
]