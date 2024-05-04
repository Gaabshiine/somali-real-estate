from django.urls import path
from . import views

app_name = "accounts_app"


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view , name="register"),
    path("logout/", views.logout_view , name="logout"), 
    path("owner_profile/", views.owner_profile_view, name="owner_profile"),
    path("user_profile/", views.user_profile_view, name="user_profile"),
    path("edit_profile/<slug:slug>", views.edit_profile_view, name="edit_profile"),
    path("change_password/<slug:slug>", views.change_password_view, name="change_password"),
    path("forgot_password/", views.forgot_password_view, name="forgot_password"),

]

