from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .profile_serializers import ProfileSerializer, SettingsSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, request):
        return Profile.objects.select_related("user").get(user=request.user)

    def get(self, request):
        profile = self.get_profile(request)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile = self.get_profile(request)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        return Response(SettingsSerializer(profile).data)

    def patch(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = SettingsSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
