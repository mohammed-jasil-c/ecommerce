from django.urls import path
from .views import LoginView, RefreshView, LogoutView , AdminOnlyView, Register

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("register/", Register.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("admin/", AdminOnlyView.as_view()), 

]
    