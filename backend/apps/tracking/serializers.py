from rest_framework import serializers

from apps.body_shape.models import Profile
from apps.lifestyle.models import DailyPlan
from .models import DailyTracking


class StrictBooleanField(serializers.BooleanField):
    def to_internal_value(self, data):
        if not isinstance(data, bool):
            raise serializers.ValidationError("Must be a valid boolean.")
        return data


class DailyTrackingSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    daily_plan = serializers.PrimaryKeyRelatedField(
        queryset=DailyPlan.objects.all(), required=False, allow_null=True
    )
    outfit_completed = StrictBooleanField(required=False)
    meals_completed = StrictBooleanField(required=False)
    expenses_reviewed = StrictBooleanField(required=False)
    daily_plan_completed = StrictBooleanField(required=False)

    class Meta:
        model = DailyTracking
        fields = [
            "id", "profile", "daily_plan", "track_date", "outfit_completed",
            "meals_completed", "expenses_reviewed", "daily_plan_completed",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_notes(self, value):
        return value.strip()

    def validate(self, attrs):
        instance = self.instance
        profile = attrs.get("profile", instance.profile if instance else None)
        track_date = attrs.get("track_date", instance.track_date if instance else None)
        daily_plan = attrs.get("daily_plan", instance.daily_plan if instance else None)
        if daily_plan and profile and daily_plan.profile_id != profile.id:
            raise serializers.ValidationError({"daily_plan": "Choose a plan from this profile."})
        if daily_plan and track_date and daily_plan.plan_date != track_date:
            raise serializers.ValidationError({"daily_plan": "The tracking and plan dates must match."})
        return attrs
