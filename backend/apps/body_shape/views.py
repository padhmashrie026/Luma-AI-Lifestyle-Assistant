from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .calculations import calculate_body_shape
from .models import BodyMeasurement, Profile
from .serializers import BodyMeasurementSerializer, BodyShapeCalculationSerializer


class BodyShapeCalculationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = BodyShapeCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = calculate_body_shape(**serializer.validated_data)
        return Response(result)


class BodyMeasurementView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, request):
        return get_object_or_404(Profile, user=request.user)

    def get_latest_measurement(self, request):
        measurement = (
            BodyMeasurement.objects.filter(profile=self.get_profile(request))
            .order_by("-measured_on", "-id")
            .first()
        )
        if measurement is None:
            raise Http404
        return measurement

    def get(self, request):
        measurement = self.get_latest_measurement(request)
        return Response(BodyMeasurementSerializer(measurement).data)

    def post(self, request):
        profile = self.get_profile(request)
        existing = BodyMeasurement.objects.filter(
            profile=profile, measured_on=request.data.get("measured_on")
        ).first()
        serializer = BodyMeasurementSerializer(
            existing, data=request.data, partial=existing is not None
        )
        serializer.is_valid(raise_exception=True)
        measurement = serializer.save(profile=profile)
        return Response(
            BodyMeasurementSerializer(measurement).data,
            status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED,
        )

    def patch(self, request):
        measurement = self.get_latest_measurement(request)
        serializer = BodyMeasurementSerializer(
            measurement, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(BodyMeasurementSerializer(serializer.save()).data)
