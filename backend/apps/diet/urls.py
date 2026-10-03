from django.urls import path

from .views import WeeklyMealPlanView


urlpatterns = [
    path("plan/", WeeklyMealPlanView.as_view(), name="diet-weekly-plan"),
]
