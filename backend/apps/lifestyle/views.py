from datetime import date

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

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
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        plans = DailyPlan.objects.select_related("profile", "outfit", "meal_plan").all()
        params = self.request.query_params
        profile_id = params.get("profile_id")
        if profile_id not in (None, ""):
            try:
                profile_id = int(profile_id)
            except (TypeError, ValueError):
                raise ValidationError({"profile_id": "Enter a valid positive integer."})
            if profile_id < 1:
                raise ValidationError({"profile_id": "Enter a valid positive integer."})
            plans = plans.filter(profile_id=profile_id)
        start_date = _query_date(params, "start_date")
        end_date = _query_date(params, "end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        if start_date:
            plans = plans.filter(plan_date__gte=start_date)
        if end_date:
            plans = plans.filter(plan_date__lte=end_date)
        return plans


class DailyPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyPlan.objects.select_related("profile", "outfit", "meal_plan").all()
    serializer_class = DailyPlanSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
