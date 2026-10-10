from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wardrobe.serializers import WardrobeItemSerializer
from apps.body_shape.models import Profile
from .recommendations import recommend_outfit
from .serializers import OutfitRecommendationRequestSerializer


class OutfitRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OutfitRecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = get_object_or_404(Profile, user=request.user)
        result = recommend_outfit(profile_id=profile.id, **serializer.validated_data)
        if result["recommendation"]:
            result["recommendations"] = [
                {key: WardrobeItemSerializer(value).data if value else None for key, value in combination.items()}
                for combination in result["recommendations"]
            ]
            result["recommendation"] = result["recommendations"][0]
        return Response(result)
