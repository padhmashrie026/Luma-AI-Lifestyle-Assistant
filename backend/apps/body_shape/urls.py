from django.urls import path

from .profile_views import ProfileView, SettingsView
from .authentication_views import (
    CsrfTokenView,
    CurrentAccountView,
    LoginView,
    LogoutView,
    RegistrationView,
)
from .views import BodyMeasurementView, BodyShapeCalculationView


urlpatterns = [
    path("auth/csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("auth/register/", RegistrationView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentAccountView.as_view(), name="auth-current-account"),
    path("body-shape/calculate/", BodyShapeCalculationView.as_view(), name="body-shape-calculate"),
    path("body-shape/measurements/", BodyMeasurementView.as_view(), name="body-shape-measurements"),
    path("profile/", ProfileView.as_view(), name="profile-detail"),
    path("settings/", SettingsView.as_view(), name="profile-settings"),
]
