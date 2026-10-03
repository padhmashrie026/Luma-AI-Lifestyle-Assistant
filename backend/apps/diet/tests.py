from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from .models import FoodPreference, Ingredient, Meal, MealIngredient


class WeeklyMealPlanApiTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="meal-planner-test")
        self.profile = Profile.objects.create(user=user)
        self.client = APIClient()
        self.url = "/api/diet/plan/"
        self.week_start = date(2026, 10, 5)

        self.oats = Ingredient.objects.create(name="Oats", default_unit="g")
        self.lentils = Ingredient.objects.create(name="Lentils", default_unit="g")
        self.spinach = Ingredient.objects.create(name="Spinach", default_unit="g")
        self._create_meal("Oat breakfast", Meal.MealType.BREAKFAST, [(self.oats, "50", "g")], 10)
        self._create_meal("Lentil lunch", Meal.MealType.LUNCH, [(self.lentils, "80", "g"), (self.spinach, "30", "g")], 25)
        self._create_meal("Spinach dinner", Meal.MealType.DINNER, [(self.spinach, "50", "g")], 20)
        self._create_meal("Oat snack", Meal.MealType.SNACK, [(self.oats, "20", "g")], 5)

    def _create_meal(self, name, meal_type, ingredients, preparation_minutes):
        meal = Meal.objects.create(
            profile=self.profile,
            name=name,
            meal_type=meal_type,
            description=f"Saved description for {name}.",
            preparation_minutes=preparation_minutes,
            servings=1,
        )
        for ingredient, quantity, unit in ingredients:
            MealIngredient.objects.create(
                meal=meal,
                ingredient=ingredient,
                quantity=Decimal(quantity),
                unit=unit,
            )
        return meal

    def _request(self, **overrides):
        payload = {"profile_id": self.profile.id, "week_start": self.week_start.isoformat()}
        payload.update(overrides)
        return self.client.post(self.url, payload, format="json")

    def test_valid_weekly_plan_generation(self):
        response = self._request()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["plan_available"])
        self.assertEqual(len(response.data["weekly_plan"]), 7)

    def test_week_has_all_supported_meal_slots(self):
        response = self._request()
        first_day = response.data["weekly_plan"][0]["meals"]
        self.assertEqual(set(first_day), {"breakfast", "lunch", "dinner", "snack"})
        self.assertTrue(first_day["breakfast"])
        self.assertTrue(first_day["lunch"])
        self.assertTrue(first_day["dinner"])

    def test_grocery_list_aggregates_stored_quantities(self):
        response = self._request()
        groceries = {entry["ingredient"]: entry for entry in response.data["grocery_list"]}
        self.assertEqual(groceries["Oats"]["quantity"], "490.00")
        self.assertEqual(groceries["Oats"]["planned_occurrences"], 14)
        self.assertEqual(groceries["Spinach"]["quantity"], "560.00")

    def test_stored_avoids_exclude_matching_meals_and_explain_missing_slots(self):
        FoodPreference.objects.create(
            profile=self.profile,
            preference_type=FoodPreference.PreferenceType.AVOIDS,
            name="lentils",
        )
        response = self._request()
        self.assertFalse(response.data["plan_available"])
        self.assertEqual(response.data["missing_meal_types"], ["lunch"])
        self.assertEqual(response.data["weekly_plan"], [])

    def test_stored_likes_are_reported_and_prioritize_matching_meals(self):
        FoodPreference.objects.create(
            profile=self.profile,
            preference_type=FoodPreference.PreferenceType.LIKES,
            name="spinach",
        )
        response = self._request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["preferences_applied"]["likes_used_to_prioritize"], ["spinach"])

    def test_budget_is_reported_as_unavailable_without_price_fields(self):
        response = self._request()
        self.assertFalse(response.data["budget"]["available"])
        self.assertIsNone(response.data["budget"]["estimated_weekly"])
        self.assertIn("do not store prices", response.data["budget"]["reason"])

    def test_invalid_inputs_are_rejected(self):
        for payload in (
            {"week_start": self.week_start.isoformat()},
            {"profile_id": self.profile.id},
            {"profile_id": self.profile.id, "week_start": "not-a-date"},
            {"profile_id": 99999, "week_start": self.week_start.isoformat()},
            {"profile_id": 0, "week_start": self.week_start.isoformat()},
        ):
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, 400)

    def test_response_includes_week_groceries_budget_and_disclaimers(self):
        response = self._request()
        self.assertEqual(response.status_code, 200)
        for key in ("weekly_plan", "grocery_list", "budget", "nutrition_note", "preparation_note", "saved"):
            self.assertIn(key, response.data)
        self.assertFalse(response.data["saved"])
        self.assertIn("medical advice", response.data["nutrition_note"])

    def test_plan_is_not_generated_when_required_stored_meals_are_missing(self):
        Meal.objects.filter(profile=self.profile, meal_type=Meal.MealType.DINNER).delete()
        response = self._request()
        self.assertFalse(response.data["plan_available"])
        self.assertEqual(response.data["missing_meal_types"], ["dinner"])
        self.assertEqual(response.data["grocery_list"], [])
