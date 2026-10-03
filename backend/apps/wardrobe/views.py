from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import WardrobeItem
from .serializers import WardrobeItemSerializer


class WardrobeItemListCreateView(generics.ListCreateAPIView):
    serializer_class = WardrobeItemSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        items = WardrobeItem.objects.select_related("profile").all()
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


class WardrobeItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WardrobeItem.objects.select_related("profile").all()
    serializer_class = WardrobeItemSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
