from django.urls import path

from .views import (
    DailyTrackingDetailView,
    DailyTrackingListCreateView,
    DailyTrackingSummaryView,
)


urlpatterns = [
    path("summary/", DailyTrackingSummaryView.as_view(), name="tracking-summary"),
    path("", DailyTrackingListCreateView.as_view(), name="tracking-list-create"),
    path("<int:pk>/", DailyTrackingDetailView.as_view(), name="tracking-detail"),
]
