from rest_framework import serializers

from apps.body_shape.models import Profile


class WeeklyMealPlanRequestSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField(min_value=1)
    week_start = serializers.DateField()

    def validate_profile_id(self, value):
        if not Profile.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No profile exists with this ID.")
        return value
