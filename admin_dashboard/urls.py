from django.contrib import admin
from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # register onwer and tentant urls
    path("user_register/", views.register_view, name="user_registration"),


    # change passowrd urls
    path("change_password/", views.change_password_redirect_view, name="change_password_redirect"),
    path("change_password/<slug:uidb64>/<slug:token>/", views.change_password_view, name="change_password"),

    # profile of owner and tenant urls
    path("owner_profile/<int:id>/", views.owner_profile_view, name="owner_profile"),
    path("tenant_profile/<int:id>/", views.tenant_profile_view, name="tenant_profile"),
    path("admin_profile/<int:id>/", views.admin_profile_view, name="admin_profile"),


  


    # view all owners, tenants and admins urls
    path("view_owners/", views.view_owners, name="view_owners"),
    path("view_tenants/", views.view_tenants, name="view_tenants"),
    path("view_admins/", views.view_admins, name="view_admins"),
    
    # delete the admin, owner and tenant urls
    path('delete_admin/', views.delete_admin, name='delete_admin'),
    path('delete_owner/', views.delete_owner, name='delete_owner'),
    path('delete_tenant/', views.delete_tenant, name='delete_tenant'),


    # edit the admin, owner and tenant urls
    path("reset_password/", views.reset_password, name="reset_password"),
    path("email_sent_confirmation/", views.email_sent_confirmation, name="email_sent_confirmation"),
    path("password_reset_done/", views.password_reset_done, name="password_reset_done"),
    path("password_reset_form/<uidb64>/<token>/<user_type>/", views.password_reset_form, name="password_reset_form"),


    

    #  apartment urls
    path('check_owner_identification/<int:owner_id>/', views.check_owner_identification, name='check_owner_identification'),
    path("view_apartments/", views.view_apartments, name="view_apartments"),
    path("rent/apartment/create/", views.create_apartment_admin, name="create_apartment_admin"),
    path("rent/apartment/edit/<int:apartment_id>/", views.update_apartment_admin, name="update_apartment_admin"),
    path("rent/apartment/delete/<int:apartment_id>/", views.delete_apartment_admin, name="delete_apartment_admin"),


    #  room urls
    path('room/create/<int:apartment_id>/', views.create_room_admin, name='create_room'),
    path('rooms/<int:apartment_id>/', views.view_rooms, name='view_rooms'),
    path('room/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('room/delete/<int:room_id>/', views.delete_room, name='delete_room'),



    # complaints urls
    path('complaints/list/', views.view_complaints, name='view_complaints'),
    path('complaint/create/<int:room_id>/', views.create_complaint, name='create_complaint'),
    path('complaint/edit/<int:complaint_id>/', views.edit_complaint, name='edit_complaint'),
    path('complaint/delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),




    # houses urls
    path('house/create/', views.create_house_admin, name='create_house_admin'),
    path('house/edit/<int:house_id>/', views.update_house_admin, name='update_house_admin'),
    path('house/delete/<int:house_id>/', views.delete_house_admin, name='delete_house_admin'),
    path('houses/', views.view_houses, name='view_houses'),

    # rent urls
    path('create_invoice/<int:room_id>/', views.create_invoice, name='create_invoice'),
    path('view_invoices/<int:room_id>/', views.view_invoices, name='view_invoices'),
    path('edit_invoice/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
    path('select_room_for_invoice/', views.select_room_for_invoice, name='select_room_for_invoice'),
    path('select_room_for_view_invoice/', views.select_room_for_view_invoice, name='select_room_for_view_invoice'),


    # assign room and house urls
    path('get_rooms/<int:apartment_id>/', views.get_rooms, name='get_rooms'), # get rooms by using AJAX
    path('get_room_details/<int:room_id>/', views.get_room_details, name='get_room_details'), # get room details by using AJAX
    path('assign_room/', views.assign_room, name='assign_room'),
    path('view_room_assignments/', views.view_room_assignments, name='view_room_assignments'),
    path('edit_room_assignment/<int:assignment_id>/', views.edit_room_assignment, name='edit_room_assignment'),
    path('delete_room_assignment/<int:assignment_id>/', views.delete_room_assignment, name='delete_room_assignment'),


    # assign house urls
    path('get_house_details/<int:house_id>/', views.get_house_details, name='get_house_details'), # get house details by using AJAX
    path('view_house_assignments/', views.view_house_assignments, name='view_house_assignments'),
    path('assign_house/', views.assign_house, name='assign_house'),
    path('edit_house_assignment/<int:assignment_id>/', views.edit_house_assignment, name='edit_house_assignment'),
    path('delete_house_assignment/<int:assignment_id>/', views.delete_house_assignment, name='delete_house_assignment'),
    
    # tenant identification urls by using AJAX
    path('check_tenant_identification/<int:tenant_id>/', views.check_tenant_identification, name='check_tenant_identification'),

    

    
]