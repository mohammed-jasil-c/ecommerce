from django.urls import path
from .views import LoginView, RefreshView, LogoutView , TestProtectedView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("test/", TestProtectedView.as_view()),  # 👈 add this

]
