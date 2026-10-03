from django.urls import path

from .views import WardrobeItemDetailView, WardrobeItemListCreateView


urlpatterns = [
    path("items/", WardrobeItemListCreateView.as_view(), name="wardrobe-item-list-create"),
    path("items/<int:pk>/", WardrobeItemDetailView.as_view(), name="wardrobe-item-detail"),
]
