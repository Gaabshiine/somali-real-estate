# urls.py
from django.urls import path
from . import views

app_name = "accounts_app"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("owner_profile/", views.owner_profile_view, name="owner_profile"),
    path("tenant_profile/", views.tenant_profile_view, name="tenant_profile"),
    path("edit_profile/<int:id>/<str:user_type>/", views.edit_profile_view, name="edit_profile"),
    path("change_password/", views.change_password_redirect_view, name="change_password_redirect"),
    path("change_password/<slug:uidb64>/<slug:token>/", views.change_password_view, name="change_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("email_sent_confirmation/", views.email_sent_confirmation, name="email_sent_confirmation"),
    path("password_reset_done/", views.password_reset_done, name="password_reset_done"),
    path("password_reset_form/<slug:uidb64>/<slug:token>/<str:user_type>/", views.password_reset_form, name="password_reset_form"),
]
