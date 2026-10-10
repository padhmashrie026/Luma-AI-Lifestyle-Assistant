from datetime import timedelta

from rest_framework import serializers
from django.db import transaction
from apps.body_shape.models import Profile
from .models import Ingredient, Meal, MealIngredient, MealPlan


class MealIngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    unit = serializers.CharField(max_length=24, required=False, allow_blank=True)


class MealSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredients = MealIngredientSerializer(many=True, required=False)

    class Meta:
        model = Meal
        fields = ["id", "profile", "name", "meal_type", "description", "preparation_minutes", "servings", "ingredients", "created_at", "updated_at"]
        read_only_fields = ["id", "profile", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["ingredients"] = [
            {"name": link.ingredient.name, "quantity": str(link.quantity) if link.quantity is not None else None,
             "unit": link.unit or link.ingredient.default_unit}
            for link in instance.meal_ingredients.select_related("ingredient").all()
        ]
        return data

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients", [])
        meal = Meal.objects.create(profile=Profile.objects.get(user=self.context["request"].user), **validated_data)
        self._save_ingredients(meal, ingredients)
        return meal

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if ingredients is not None:
            instance.meal_ingredients.all().delete()
            self._save_ingredients(instance, ingredients)
        return instance

    @staticmethod
    def _save_ingredients(meal, ingredients):
        for item in ingredients:
            ingredient_name = item["name"].strip()
            if not ingredient_name:
                raise serializers.ValidationError({"ingredients": "Ingredient names cannot be blank."})
            ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
            MealIngredient.objects.create(meal=meal, ingredient=ingredient, quantity=item.get("quantity"), unit=item.get("unit", "").strip())

class WeeklyMealPlanRequestSerializer(serializers.Serializer):
    week_start = serializers.DateField()


class SavedMealPlanDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    meals = serializers.DictField(child=serializers.IntegerField(allow_null=True))

    def validate_meals(self, meals):
        allowed_slots = {"breakfast", "lunch", "dinner", "snack"}
        if set(meals) - allowed_slots:
            raise serializers.ValidationError("Only supported meal slots can be saved.")
        if any(slot not in meals or not meals[slot] for slot in ("breakfast", "lunch", "dinner")):
            raise serializers.ValidationError("Breakfast, lunch and dinner are required for every day.")
        return meals


class SaveWeeklyMealPlanSerializer(serializers.Serializer):
    week_start = serializers.DateField()
    weekly_plan = SavedMealPlanDaySerializer(many=True)

    def validate_weekly_plan(self, days):
        if len(days) != 7:
            raise serializers.ValidationError("A weekly plan must contain exactly seven days.")
        start = self.initial_data.get("week_start")
        start_date = serializers.DateField().to_internal_value(start)
        expected_dates = [start_date + timedelta(days=index) for index in range(7)]
        if [day["date"] for day in days] != expected_dates:
            raise serializers.ValidationError("Plan dates must match the selected seven-day period.")

        request = self.context["request"]
        profile = Profile.objects.get(user=request.user)
        meal_ids = {meal_id for day in days for meal_id in day["meals"].values() if meal_id is not None}
        owned_meals = {meal.id: meal for meal in Meal.objects.filter(profile=profile, id__in=meal_ids)}
        if len(owned_meals) != len(meal_ids):
            raise serializers.ValidationError("One or more selected meals are not in your saved meals.")
        for day in days:
            for slot, meal_id in day["meals"].items():
                if meal_id is not None and owned_meals[meal_id].meal_type != slot:
                    raise serializers.ValidationError(f"The selected meal for {slot} must be a {slot} meal.")
        self._owned_meals = owned_meals
        return days

    def validate(self, attrs):
        end_date = attrs["week_start"] + timedelta(days=6)
        if MealPlan.objects.filter(profile__user=self.context["request"].user,
                                   plan_date__range=(attrs["week_start"], end_date)).exists():
            raise serializers.ValidationError({"week_start": "A meal plan already exists for one or more days in this week."})
        return attrs
