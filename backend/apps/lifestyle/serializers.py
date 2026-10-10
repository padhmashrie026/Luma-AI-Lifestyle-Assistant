from rest_framework import serializers

from apps.body_shape.models import Profile
from apps.diet.models import MealPlan
from apps.outfits.models import Outfit
from .models import DailyPlan, DailyTask


class CurrentUserProfileDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return Profile.objects.get(user=serializer_field.context["request"].user)


class DailyPlanSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserProfileDefault()
    )
    outfit = serializers.PrimaryKeyRelatedField(
        queryset=Outfit.objects.all(), required=False, allow_null=True
    )
    meal_plan = serializers.PrimaryKeyRelatedField(
        queryset=MealPlan.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = DailyPlan
        fields = [
            "id", "profile", "plan_date", "outfit", "meal_plan", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_notes(self, value):
        return value.strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            profile = Profile.objects.filter(user=request.user).first()
            if profile:
                self.fields["outfit"].queryset = Outfit.objects.filter(profile=profile)
                self.fields["meal_plan"].queryset = MealPlan.objects.filter(profile=profile)

    def validate(self, attrs):
        instance = self.instance
        request = self.context.get("request")
        profile = (
            Profile.objects.filter(user=request.user).first()
            if request and request.user.is_authenticated
            else instance.profile if instance else None
        )
        plan_date = attrs.get("plan_date", instance.plan_date if instance else None)
        outfit = attrs.get("outfit", instance.outfit if instance else None)
        meal_plan = attrs.get("meal_plan", instance.meal_plan if instance else None)
        if outfit and profile and outfit.profile_id != profile.id:
            raise serializers.ValidationError({"outfit": "Choose an outfit from this profile."})
        if meal_plan and profile and meal_plan.profile_id != profile.id:
            raise serializers.ValidationError({"meal_plan": "Choose a meal plan from this profile."})
        if meal_plan and plan_date and meal_plan.plan_date != plan_date:
            raise serializers.ValidationError({"meal_plan": "The meal plan and daily plan dates must match."})
        return attrs


class DailyTaskSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    daily_plan = serializers.PrimaryKeyRelatedField(read_only=True)
    task_date = serializers.DateField(required=False)
    duration_minutes = serializers.IntegerField(min_value=1)

    class Meta:
        model = DailyTask
        fields = [
            "id", "profile", "daily_plan", "title", "description", "task_date",
            "duration_minutes", "is_completed", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "profile", "daily_plan", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("A task title is required.")
        return value

    def validate_description(self, value):
        return value.strip()
