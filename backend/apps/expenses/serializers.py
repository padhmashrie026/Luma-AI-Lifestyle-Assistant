from decimal import Decimal

from rest_framework import serializers

from apps.body_shape.models import Profile
from apps.lifestyle.models import DailyPlan
from .models import BudgetCategory, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=BudgetCategory.objects.all())
    daily_plan = serializers.PrimaryKeyRelatedField(
        queryset=DailyPlan.objects.all(), required=False, allow_null=True
    )
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )

    class Meta:
        model = Expense
        fields = [
            "id", "profile", "category", "daily_plan", "description", "amount",
            "spent_on", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_description(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_notes(self, value):
        return value.strip()

    def validate(self, attrs):
        instance = self.instance
        profile = attrs.get("profile", instance.profile if instance else None)
        category = attrs.get("category", instance.category if instance else None)
        daily_plan = attrs.get("daily_plan", instance.daily_plan if instance else None)
        spent_on = attrs.get("spent_on", instance.spent_on if instance else None)

        if profile and category and category.profile_id != profile.id:
            raise serializers.ValidationError({
                "category": "Choose a budget category from this profile."
            })
        if daily_plan and profile and daily_plan.profile_id != profile.id:
            raise serializers.ValidationError({
                "daily_plan": "Choose a daily plan from this profile."
            })
        if daily_plan and spent_on and daily_plan.plan_date != spent_on:
            raise serializers.ValidationError({
                "daily_plan": "The expense and daily plan dates must match."
            })
        return attrs


class ExpenseSummaryQuerySerializer(serializers.Serializer):
    profile_id = serializers.IntegerField(min_value=1)
    month = serializers.RegexField(
        regex=r"^\d{4}-(0[1-9]|1[0-2])$", required=False,
        error_messages={"invalid": "Enter a month in YYYY-MM format."},
    )

    def validate_profile_id(self, value):
        if not Profile.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No profile exists with this ID.")
        return value
