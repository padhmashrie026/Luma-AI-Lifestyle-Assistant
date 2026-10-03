from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .planning import generate_weekly_plan
from .serializers import WeeklyMealPlanRequestSerializer


class WeeklyMealPlanView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WeeklyMealPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_weekly_plan(**serializer.validated_data)
        return Response(result)
