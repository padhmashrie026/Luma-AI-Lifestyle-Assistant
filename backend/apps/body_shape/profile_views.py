from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .profile_serializers import ProfileSerializer, SettingsSerializer


def get_requested_profile(request):
    raw_profile_id = request.query_params.get("profile_id")
    if raw_profile_id in (None, ""):
        raise ValidationError({"profile_id": "This query parameter is required."})
    try:
        profile_id = int(raw_profile_id)
    except (TypeError, ValueError):
        raise ValidationError({"profile_id": "Enter a valid positive integer."})
    if profile_id < 1:
        raise ValidationError({"profile_id": "Enter a valid positive integer."})
    return get_object_or_404(Profile.objects.select_related("user"), pk=profile_id)


class ProfileView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        profile = get_requested_profile(request)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile = get_requested_profile(request)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SettingsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        profile = get_requested_profile(request)
        return Response(SettingsSerializer(profile).data)

    def patch(self, request):
        profile = get_requested_profile(request)
        serializer = SettingsSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
