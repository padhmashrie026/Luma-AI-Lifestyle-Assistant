from django.urls import path

from .views import DailyPlanDetailView, DailyPlanListCreateView


urlpatterns = [
    path("daily-plan/", DailyPlanListCreateView.as_view(), name="daily-plan-list-create"),
    path("daily-plan/<int:pk>/", DailyPlanDetailView.as_view(), name="daily-plan-detail"),
]
