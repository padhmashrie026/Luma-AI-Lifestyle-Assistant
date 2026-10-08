from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.body_shape.models import Profile
from .models import DailyPlan
from .serializers import DailyPlanSerializer


def _query_date(params, key):
    value = params.get(key)
    if value in (None, ""):
        return None
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError({key: "Enter a valid date in YYYY-MM-DD format."})
    if parsed.isoformat() != value:
        raise ValidationError({key: "Enter a valid date in YYYY-MM-DD format."})
    return parsed


class DailyPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_queryset(self):
        plans = DailyPlan.objects.select_related("profile", "outfit", "meal_plan").filter(profile=self.get_profile())
        params = self.request.query_params
        start_date = _query_date(params, "start_date")
        end_date = _query_date(params, "end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        if start_date:
            plans = plans.filter(plan_date__gte=start_date)
        if end_date:
            plans = plans.filter(plan_date__lte=end_date)
        return plans

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class DailyPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return DailyPlan.objects.select_related("profile", "outfit", "meal_plan").filter(profile=profile)
