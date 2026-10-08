from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .planning import generate_weekly_plan
from .serializers import WeeklyMealPlanRequestSerializer
from apps.body_shape.models import Profile


class WeeklyMealPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WeeklyMealPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = get_object_or_404(Profile, user=request.user)
        result = generate_weekly_plan(profile_id=profile.id, **serializer.validated_data)
        return Response(result)
