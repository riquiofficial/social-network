
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("like/<int:post_id>", views.index, name="like"),
    path("edit/<int:post_id>", views.index, name="edit"),
    path("following/<str:following>", views.index, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("profile/<str:user>", views.profile, name="user_profile"),
    path("profile/<str:user>/<str:follow>", views.profile, name="follow"),
]
