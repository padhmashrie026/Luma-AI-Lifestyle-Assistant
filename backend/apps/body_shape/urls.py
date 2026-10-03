from django.urls import path

from .profile_views import ProfileView, SettingsView
from .views import BodyShapeCalculationView


urlpatterns = [
    path("body-shape/calculate/", BodyShapeCalculationView.as_view(), name="body-shape-calculate"),
    path("profile/", ProfileView.as_view(), name="profile-detail"),
    path("settings/", SettingsView.as_view(), name="profile-settings"),
]
