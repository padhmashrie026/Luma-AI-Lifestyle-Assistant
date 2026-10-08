from datetime import date, timedelta

from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from apps.body_shape.models import Profile
from .models import DailyTracking
from .serializers import DailyTrackingSerializer
from .summaries import build_tracking_summary


class TrackingSummaryQuerySerializer(serializers.Serializer):
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
    permission_classes = [IsAuthenticated]

    def get_profile(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_queryset(self):
        records = DailyTracking.objects.select_related("profile", "daily_plan").filter(profile=self.get_profile())
        start_date = _query_date(self.request.query_params, "start_date")
        end_date = _query_date(self.request.query_params, "end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        if start_date:
            records = records.filter(track_date__gte=start_date)
        if end_date:
            records = records.filter(track_date__lte=end_date)
        return records

    def perform_create(self, serializer):
        serializer.save(profile=self.get_profile())


class DailyTrackingDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DailyTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return DailyTracking.objects.select_related("profile", "daily_plan").filter(profile=profile)


class DailyTrackingSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = TrackingSummaryQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        profile = get_object_or_404(Profile, user=request.user)
        end_date = values.get("end_date") or timezone.localdate()
        start_date = values.get("start_date") or end_date - timedelta(days=6)
        if start_date > end_date:
            raise ValidationError({"date_range": "start_date must be on or before end_date."})
        return Response(build_tracking_summary(profile.id, start_date, end_date))
