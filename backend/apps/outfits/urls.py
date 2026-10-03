from django.urls import path

from .views import OutfitRecommendationView


urlpatterns = [
    path("recommend/", OutfitRecommendationView.as_view(), name="outfit-recommend"),
]
