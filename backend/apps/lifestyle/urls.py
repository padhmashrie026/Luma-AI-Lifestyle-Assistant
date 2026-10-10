from django.urls import path

from .views import DailyPlanDetailView, DailyPlanListCreateView, DailyTaskDetailView, DailyTaskListCreateView


urlpatterns = [
    path("daily-plan/", DailyPlanListCreateView.as_view(), name="daily-plan-list-create"),
    path("daily-plan/<int:pk>/", DailyPlanDetailView.as_view(), name="daily-plan-detail"),
    path("daily-plan/<int:plan_id>/tasks/", DailyTaskListCreateView.as_view(), name="daily-task-list-create"),
    path("tasks/<int:pk>/", DailyTaskDetailView.as_view(), name="daily-task-detail"),
]
