from datetime import timedelta

from rest_framework import generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from apps.body_shape.models import Profile
from .models import DailyTracking
from .serializers import DailyTrackingSerializer
from .summaries import build_tracking_summary


class TrackingSummaryQuerySerializer(serializers.Serializer):
    profile_id = serializers.IntegerField(min_value=1)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


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


class DailyTrackingListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyTrackingSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        records = DailyTracking.objects.select_related("profile", "daily_plan").all()
        profile_id = self.request.query_params.get("profile_id")
        if profile_id not in (None, ""):
            try:
                profile_id = int(profile_id)
            except (TypeError, ValueError):
                raise ValidationError({"profile_id": "Enter a valid positive integer."})
            if profile_id < 1:
                raise ValidationError({"profile_id": "Enter a valid positive integer."})
            records = records.filter(profile_id=profile_id)
        start_date = _query_date(self.request.query_params, "start_date")
        end_date = _query_date(self.request.query_params, "end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        if start_date:
            records = records.filter(track_date__gte=start_date)
        if end_date:
            records = records.filter(track_date__lte=end_date)
        return records


class DailyTrackingDetailView(generics.RetrieveUpdateAPIView):
    queryset = DailyTracking.objects.select_related("profile", "daily_plan").all()
    serializer_class = DailyTrackingSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class DailyTrackingSummaryView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        query = TrackingSummaryQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        profile_id = values["profile_id"]
        if not Profile.objects.filter(pk=profile_id).exists():
            raise ValidationError({"profile_id": "No profile exists with this ID."})
        end_date = values.get("end_date") or timezone.localdate()
        start_date = values.get("start_date") or end_date - timedelta(days=6)
        if start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        return Response(build_tracking_summary(profile_id, start_date, end_date))
