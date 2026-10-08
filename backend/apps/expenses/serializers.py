from decimal import Decimal

from rest_framework import serializers

from apps.body_shape.models import Profile
from apps.lifestyle.models import DailyPlan
from .models import BudgetCategory, Expense


class CurrentUserProfileDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return Profile.objects.get(user=serializer_field.context["request"].user)


class BudgetCategorySerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserProfileDefault()
    )

    class Meta:
        model = BudgetCategory
        fields = ["id", "profile", "name", "monthly_limit", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value


class ExpenseSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=BudgetCategory.objects.all())
    daily_plan = serializers.PrimaryKeyRelatedField(
        queryset=DailyPlan.objects.all(), required=False, allow_null=True
    )
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            profile = Profile.objects.filter(user=request.user).first()
            if profile:
                self.fields["category"].queryset = BudgetCategory.objects.filter(profile=profile)
                self.fields["daily_plan"].queryset = DailyPlan.objects.filter(profile=profile)

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
        request = self.context.get("request")
        profile = (
            Profile.objects.filter(user=request.user).first()
            if request and request.user.is_authenticated
            else instance.profile if instance else None
        )
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
    month = serializers.RegexField(
        regex=r"^\d{4}-(0[1-9]|1[0-2])$", required=False,
        error_messages={"invalid": "Enter a month in YYYY-MM format."},
    )
