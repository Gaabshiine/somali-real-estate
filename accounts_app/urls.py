from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts_app"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"), 
    path("owner_profile/", views.owner_profile_view, name="owner_profile"),
    path("user_profile/", views.user_profile_view, name="user_profile"),
    path("edit_profile/<slug:slug>", views.edit_profile_view, name="edit_profile"),
    path('change_password/', views.change_password_redirect_view, name='change_password_redirect'),
    path('change_password/<int:id>/', views.change_password_view, name='change_password'),
    path('password_reset_form/<int:user_id>/', views.password_reset_form, name='password_reset_form'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('email_sent_confirmation/', views.email_sent_confirmation, name='email_sent_confirmation'), 
]
