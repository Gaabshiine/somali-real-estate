from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "rental_property_app"

urlpatterns = [
        
    # # Apartment URLs
    # path('apartments/', views.list_apartments, name='list_apartments'),
    path('apartment/create/', views.create_apartment, name='create_apartment'),
    # path('apartment/edit/<int:pk>/', views.edit_apartment, name='edit_apartment'),
    # path('apartment/delete/<int:pk>/', views.delete_apartment, name='delete_apartment'),

    # # Room URLs
    # path('rooms/list/<int:apartment_id>/', views.list_rooms, name='list_rooms'),
    # path('room/create/<int:apartment_id>/', views.create_room, name='create_room'),
    # path('room/edit/<int:room_id>/', views.edit_room, name='edit_room'),

    # # Room Assignment URLs
    # path('assignment/create/<int:room_id>/', views.create_assignment, name='create_assignment'),
    # path('assignments/list/<int:room_id>/', views.list_assignments, name='list_assignments'),

    # # Complaint URLs
    # path('complaints/list/<int:room_id>/', views.list_complaints, name='list_complaints'),
    # path('complaint/create/<int:room_id>/', views.create_complaint, name='create_complaint'),
    # path('complaint/edit/<int:complaint_id>/', views.edit_complaint, name='edit_complaint'),

    # # Invoice URLs
    # path('invoices/list/<int:room_id>/', views.list_invoices, name='list_invoices'),
    # path('invoice/create/<int:room_id>/', views.create_invoice, name='create_invoice'),
    # path('invoice/edit/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),

    # # Search and Miscellaneous
    # path('search/', views.search_view, name='search'),

]

