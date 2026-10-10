from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from .models import FoodPreference, Ingredient, Meal, MealIngredient, MealPlan, MealPlanItem


class MealManagementApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="meal-owner")
        self.profile = Profile.objects.create(user=self.user)
        self.other_user = get_user_model().objects.create_user(username="meal-other")
        self.other_profile = Profile.objects.create(user=self.other_user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = "/api/diet/meals/"

    def test_create_and_retrieve_meal_with_supported_fields(self):
        payload = {"name": "Simple bowl", "meal_type": "lunch", "description": "Stored description", "preparation_minutes": 12,
                   "servings": 2, "profile": self.other_profile.id,
                   "ingredients": [{"name": "Rice", "quantity": "100.00", "unit": "g"}]}
        created = self.client.post(self.url, payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["profile"], self.profile.id)
        self.assertEqual(created.data["ingredients"][0]["name"], "Rice")
        listing = self.client.get(self.url)
        self.assertEqual([item["id"] for item in listing.data], [created.data["id"]])

    def test_update_and_delete_owned_meal(self):
        meal = Meal.objects.create(profile=self.profile, name="Old meal")
        response = self.client.patch(f"{self.url}{meal.id}/", {"name": "New meal"}, format="json")
        self.assertEqual(response.status_code, 200)
        meal.refresh_from_db()
        self.assertEqual(meal.name, "New meal")
        self.assertEqual(self.client.delete(f"{self.url}{meal.id}/").status_code, 204)
        self.assertFalse(Meal.objects.filter(pk=meal.pk).exists())

    def test_meal_operations_require_authentication(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
        self.assertIn(self.client.post(self.url, {"name": "Nope"}, format="json").status_code, (401, 403))

    def test_other_users_meals_are_hidden_and_immutable(self):
        meal = Meal.objects.create(profile=self.other_profile, name="Private meal")
        self.assertEqual(self.client.get(self.url).data, [])
        self.assertEqual(self.client.patch(f"{self.url}{meal.id}/", {"name": "Changed"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"{self.url}{meal.id}/").status_code, 404)
        meal.refresh_from_db()
        self.assertEqual(meal.name, "Private meal")


class WeeklyMealPlanApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="meal-planner-test")
        self.profile = Profile.objects.create(user=self.user)
        self.client = APIClient()
        self.url = "/api/diet/plan/"
        self.client.force_authenticate(self.user)
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
        payload = {"week_start": self.week_start.isoformat()}
        payload.update(overrides)
        return self.client.post(self.url, payload, format="json")

    def _save_payload(self):
        meals = {
            "breakfast": Meal.objects.get(profile=self.profile, meal_type=Meal.MealType.BREAKFAST).id,
            "lunch": Meal.objects.get(profile=self.profile, meal_type=Meal.MealType.LUNCH).id,
            "dinner": Meal.objects.get(profile=self.profile, meal_type=Meal.MealType.DINNER).id,
            "snack": None,
        }
        from datetime import timedelta
        return {
            "week_start": self.week_start.isoformat(),
            "weekly_plan": [
                {"date": (self.week_start + timedelta(days=index)).isoformat(), "meals": meals}
                for index in range(7)
            ],
        }

    def test_save_and_retrieve_weekly_plan(self):
        url = "/api/diet/plan/saved/"
        response = self.client.post(url, self._save_payload(), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data["saved"])
        self.assertEqual(len(response.data["weekly_plan"]), 7)
        self.assertEqual(MealPlan.objects.filter(profile=self.profile).count(), 7)
        self.assertEqual(MealPlanItem.objects.filter(meal_plan__profile=self.profile).count(), 21)

        retrieved = self.client.get(url)
        self.assertEqual(retrieved.status_code, 200)
        self.assertTrue(retrieved.data["saved"])
        self.assertEqual(retrieved.data["week_start"], self.week_start.isoformat())
        self.assertEqual(retrieved.data["weekly_plan"][0]["meals"]["breakfast"]["name"], "Oat breakfast")

    def test_saved_week_is_isolated_between_users(self):
        url = "/api/diet/plan/saved/"
        self.client.post(url, self._save_payload(), format="json")
        other_user = get_user_model().objects.create_user(username="saved-plan-other")
        Profile.objects.create(user=other_user)
        self.client.force_authenticate(other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["plan_available"])

    def test_saved_plan_requires_authentication_and_rejects_duplicate_or_invalid_meals(self):
        url = "/api/diet/plan/saved/"
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(url).status_code, (401, 403))
        self.client.force_authenticate(self.user)
        payload = self._save_payload()
        self.assertEqual(self.client.post(url, payload, format="json").status_code, 201)
        self.assertEqual(self.client.post(url, payload, format="json").status_code, 400)

        other_user = get_user_model().objects.create_user(username="foreign-plan-meal")
        other_profile = Profile.objects.create(user=other_user)
        foreign_meal = Meal.objects.create(profile=other_profile, name="Foreign meal", meal_type=Meal.MealType.BREAKFAST)
        payload = self._save_payload()
        payload["weekly_plan"][0]["meals"]["breakfast"] = foreign_meal.id
        payload["week_start"] = "2026-10-12"
        from datetime import timedelta
        payload["weekly_plan"] = [
            {"date": (date(2026, 10, 12) + timedelta(days=index)).isoformat(), "meals": payload["weekly_plan"][index]["meals"]}
            for index in range(7)
        ]
        self.assertEqual(self.client.post(url, payload, format="json").status_code, 400)

    def test_anonymous_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        response = self._request()
        self.assertIn(response.status_code, (401, 403))

    def test_valid_weekly_plan_generation(self):
        response = self._request()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["plan_available"])
        self.assertEqual(len(response.data["weekly_plan"]), 7)

    def test_weekly_plan_rotates_between_multiple_saved_meals(self):
        second = self._create_meal("Second breakfast", Meal.MealType.BREAKFAST, [(self.oats, "35", "g")], 15)
        response = self._request()
        self.assertTrue(response.data["plan_available"])
        breakfasts = {day["meals"]["breakfast"]["id"] for day in response.data["weekly_plan"]}
        self.assertEqual(breakfasts, {Meal.objects.get(name="Oat breakfast").id, second.id})

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
            {},
            {"week_start": "not-a-date"},
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

    def test_new_user_with_no_meals_gets_empty_result(self):
        user = get_user_model().objects.create_user(username="new-diet-user")
        Profile.objects.create(user=user)
        self.client.force_authenticate(user)
        response = self._request()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["plan_available"])
        self.assertTrue(response.data["meals_empty"])
        self.assertEqual(response.data["weekly_plan"], [])

    def test_forged_profile_fields_are_ignored_and_other_users_data_is_isolated(self):
        other_user = get_user_model().objects.create_user(username="other-diet-user")
        other_profile = Profile.objects.create(user=other_user)
        other_meal = Meal.objects.create(
            profile=other_profile, name="Other user's breakfast", meal_type=Meal.MealType.BREAKFAST
        )
        FoodPreference.objects.create(
            profile=other_profile,
            preference_type=FoodPreference.PreferenceType.AVOIDS,
            name="Oat",
        )
        response = self.client.post(
            self.url,
            {"week_start": self.week_start.isoformat(), "profile_id": other_profile.id,
             "profile": other_profile.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["plan_available"])
        breakfast_ids = {
            day["meals"]["breakfast"]["id"] for day in response.data["weekly_plan"]
            if day["meals"]["breakfast"]
        }
        self.assertNotIn(other_meal.id, breakfast_ids)
        self.assertEqual(response.data["preferences_applied"]["avoided_terms_excluded"], [])
        other_meal.refresh_from_db()
        self.assertEqual(other_meal.name, "Other user's breakfast")

    def test_demo_meals_and_preferences_are_not_modified_by_planning(self):
        before_meals = list(Meal.objects.filter(profile=self.profile).values_list("id", "name"))
        before_preferences = list(FoodPreference.objects.filter(profile=self.profile).values_list("id", "name"))
        response = self._request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(Meal.objects.filter(profile=self.profile).values_list("id", "name")), before_meals)
        self.assertEqual(list(FoodPreference.objects.filter(profile=self.profile).values_list("id", "name")), before_preferences)
