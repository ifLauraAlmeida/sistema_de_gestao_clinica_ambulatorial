from django.urls import path

from apps.accounts.views import CsrfCookieView, CurrentUserView, LoginView, LogoutView

urlpatterns = [
    path("auth/csrf/", CsrfCookieView.as_view(), name="auth-csrf"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
]
