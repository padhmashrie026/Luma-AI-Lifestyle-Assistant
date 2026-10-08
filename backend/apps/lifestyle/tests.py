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
        self.user = get_user_model().objects.create_user("daily-plan-api")
        self.profile = Profile.objects.create(user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = "/api/lifestyle/daily-plan/"

    def payload(self, **overrides):
        return {"plan_date": "2026-10-03", "notes": "Plan notes", **overrides}

    def test_anonymous_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
        self.assertIn(self.client.post(self.url, self.payload(), format="json").status_code, (401, 403))

    def test_create_list_retrieve_update_and_delete_daily_plan(self):
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["plan_date"], "2026-10-03")
        self.assertEqual(created.data["notes"], "Plan notes")

        listed = self.client.get(self.url)
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

    def test_forged_profile_fields_cannot_change_plan_owner(self):
        other_profile = Profile.objects.create(
            user=get_user_model().objects.create_user("daily-plan-forged")
        )
        response = self.client.post(
            self.url,
            self.payload(profile=other_profile.id, profile_id=other_profile.id),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DailyPlan.objects.get(plan_date="2026-10-03").profile, self.profile)

    def test_user_cannot_list_retrieve_update_or_delete_another_users_plan(self):
        other_profile = Profile.objects.create(
            user=get_user_model().objects.create_user("daily-plan-private")
        )
        other_plan = DailyPlan.objects.create(profile=other_profile, plan_date=date(2026, 10, 3))
        self.assertEqual(self.client.get(self.url, {"profile_id": other_profile.id}).data, [])
        detail = f"{self.url}{other_plan.id}/"
        self.assertEqual(self.client.get(detail).status_code, 404)
        self.assertEqual(self.client.patch(detail, {"notes": "changed"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(detail).status_code, 404)

    def test_new_user_has_empty_plan_list_and_can_create_for_selected_date(self):
        user = get_user_model().objects.create_user("daily-plan-new-user")
        Profile.objects.create(user=user)
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get(self.url).data, [])
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
