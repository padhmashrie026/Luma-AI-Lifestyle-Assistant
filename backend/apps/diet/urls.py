from django.urls import path

from .views import MealDetailView, MealListCreateView, SavedWeeklyMealPlanView, WeeklyMealPlanView


urlpatterns = [
    path("meals/", MealListCreateView.as_view(), name="diet-meal-list-create"),
    path("meals/<int:pk>/", MealDetailView.as_view(), name="diet-meal-detail"),
    path("plan/", WeeklyMealPlanView.as_view(), name="diet-weekly-plan"),
    path("plan/saved/", SavedWeeklyMealPlanView.as_view(), name="diet-weekly-plan-saved"),
]
