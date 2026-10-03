from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wardrobe.serializers import WardrobeItemSerializer
from .recommendations import recommend_outfit
from .serializers import OutfitRecommendationRequestSerializer


class OutfitRecommendationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OutfitRecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = recommend_outfit(**serializer.validated_data)
        if result["recommendation"]:
            result["recommendation"] = {
                key: WardrobeItemSerializer(value).data if value else None
                for key, value in result["recommendation"].items()
            }
        return Response(result)
