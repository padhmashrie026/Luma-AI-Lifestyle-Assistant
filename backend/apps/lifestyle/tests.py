from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from apps.diet.models import MealPlan
from apps.lifestyle.models import DailyPlan
from apps.outfits.models import Outfit


class DailyPlanValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.profile = Profile.objects.create(user=user_model.objects.create_user("planner"))
        self.other_profile = Profile.objects.create(
            user=user_model.objects.create_user("someone_else")
        )

    def test_daily_plan_cannot_use_another_profiles_outfit(self):
        outfit = Outfit.objects.create(profile=self.other_profile, name="Other person's look")
        plan = DailyPlan(profile=self.profile, plan_date=date(2026, 10, 2), outfit=outfit)

        with self.assertRaises(ValidationError):
            plan.full_clean()


class DailyPlanApiTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            user=get_user_model().objects.create_user("daily-plan-api")
        )
        self.client = APIClient()
        self.url = "/api/lifestyle/daily-plan/"

    def payload(self, **overrides):
        return {"profile": self.profile.id, "plan_date": "2026-10-03", "notes": "Plan notes", **overrides}

    def test_create_list_retrieve_update_and_delete_daily_plan(self):
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["plan_date"], "2026-10-03")
        self.assertEqual(created.data["notes"], "Plan notes")

        listed = self.client.get(self.url, {"profile_id": self.profile.id})
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)

        detail_url = f"{self.url}{created.data['id']}/"
        retrieved = self.client.get(detail_url)
        self.assertEqual(retrieved.status_code, 200)
        updated = self.client.patch(detail_url, {"notes": "Updated plan"}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["notes"], "Updated plan")
        deleted = self.client.delete(detail_url)
        self.assertEqual(deleted.status_code, 204)

    def test_rejects_invalid_date_and_duplicate_profile_date(self):
        invalid = self.client.post(self.url, self.payload(plan_date="2026-02-30"), format="json")
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("plan_date", invalid.data)
        self.client.post(self.url, self.payload(), format="json")
        duplicate = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(duplicate.status_code, 400)

    def test_rejects_outfit_from_another_profile(self):
        other_profile = Profile.objects.create(
            user=get_user_model().objects.create_user("daily-plan-other")
        )
        outfit = Outfit.objects.create(profile=other_profile, name="Other profile outfit")
        response = self.client.post(self.url, self.payload(outfit=outfit.id), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("outfit", response.data)

    def test_daily_plan_meal_plan_must_be_for_the_same_date(self):
        meal_plan = MealPlan.objects.create(profile=self.profile, plan_date=date(2026, 10, 1))
        plan = DailyPlan(
            profile=self.profile,
            plan_date=date(2026, 10, 2),
            meal_plan=meal_plan,
        )

        with self.assertRaises(ValidationError):
            plan.full_clean()
