from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from apps.diet.models import MealPlan
from apps.lifestyle.models import DailyPlan, DailyTask
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


class DailyTaskApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("daily-task-api")
        self.profile = Profile.objects.create(user=self.user)
        self.plan = DailyPlan.objects.create(profile=self.profile, plan_date=date(2026, 10, 3))
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = f"/api/lifestyle/daily-plan/{self.plan.id}/tasks/"

    def payload(self, **overrides):
        return {"title": "Read project notes", "description": "Prepare a short summary", "duration_minutes": 30, **overrides}

    def test_create_and_list_task_persists_with_plan_date_default(self):
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["task_date"], "2026-10-03")
        self.assertEqual(created.data["daily_plan"], self.plan.id)
        self.assertEqual(created.data["profile"], self.profile.id)
        listed = self.client.get(self.url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)
        self.assertTrue(DailyTask.objects.filter(pk=created.data["id"], profile=self.profile).exists())

    def test_task_requires_title_and_positive_duration(self):
        for payload in (
            self.payload(title="  "),
            self.payload(duration_minutes=0),
            self.payload(duration_minutes=-5),
            self.payload(duration_minutes="not-a-number"),
            self.payload(task_date="2026-02-30"),
        ):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post(self.url, payload, format="json").status_code, 400)

    def test_task_can_be_edited_completed_and_deleted(self):
        created = self.client.post(self.url, self.payload(), format="json")
        detail = f"/api/lifestyle/tasks/{created.data['id']}/"
        updated = self.client.patch(detail, {"title": "Updated task", "duration_minutes": 45, "is_completed": True}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["title"], "Updated task")
        self.assertEqual(updated.data["duration_minutes"], 45)
        self.assertTrue(updated.data["is_completed"])
        pending = self.client.patch(detail, {"is_completed": False}, format="json")
        self.assertFalse(pending.data["is_completed"])
        self.assertEqual(self.client.delete(detail).status_code, 204)
        self.assertFalse(DailyTask.objects.exists())

    def test_tasks_require_authentication_and_are_isolated_by_profile(self):
        created = self.client.post(self.url, self.payload(), format="json")
        detail = f"/api/lifestyle/tasks/{created.data['id']}/"
        other_user = get_user_model().objects.create_user("daily-task-other")
        other_profile = Profile.objects.create(user=other_user)
        other_plan = DailyPlan.objects.create(profile=other_profile, plan_date=date(2026, 10, 3))
        other_plan_url = f"/api/lifestyle/daily-plan/{other_plan.id}/tasks/"
        self.assertEqual(self.client.post(other_plan_url, self.payload(), format="json").status_code, 404)
        self.client.force_authenticate(other_user)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.patch(detail, {"title": "Stolen"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(detail).status_code, 404)
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(f"/api/lifestyle/daily-plan/{other_plan.id}/tasks/").status_code, (401, 403))

    def test_task_date_can_be_set_and_forged_ownership_is_ignored(self):
        other_user = get_user_model().objects.create_user("daily-task-forged")
        other_profile = Profile.objects.create(user=other_user)
        created = self.client.post(
            self.url,
            self.payload(task_date="2026-10-04", profile=other_profile.id, daily_plan=99999),
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        task = DailyTask.objects.get(pk=created.data["id"])
        self.assertEqual(task.profile, self.profile)
        self.assertEqual(task.daily_plan, self.plan)
        self.assertEqual(task.task_date, date(2026, 10, 4))
