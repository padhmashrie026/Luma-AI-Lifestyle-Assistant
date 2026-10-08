from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.body_shape.models import Profile

from .models import WardrobeItem
from .serializers import WardrobeItemSerializer


class WardrobeItemListCreateView(generics.ListCreateAPIView):
    serializer_class = WardrobeItemSerializer
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_queryset(self):
        items = WardrobeItem.objects.select_related("profile").filter(profile=self.get_profile())
        category = self.request.query_params.get("category")
        color = self.request.query_params.get("color")
        status = self.request.query_params.get("status")

        if category:
            items = items.filter(category=category)
        if color:
            items = items.filter(color__icontains=color.strip())
        if status:
            items = items.filter(status=status)
        return items

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class WardrobeItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WardrobeItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return WardrobeItem.objects.select_related("profile").filter(profile=profile)
