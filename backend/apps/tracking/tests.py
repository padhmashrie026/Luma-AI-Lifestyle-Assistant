from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from apps.lifestyle.models import DailyPlan
from apps.tracking.models import DailyTracking


class DailyTrackingValidationTests(TestCase):
    def test_tracking_day_must_match_its_linked_plan(self):
        user = get_user_model().objects.create_user("tracker")
        profile = Profile.objects.create(user=user)
        plan = DailyPlan.objects.create(profile=profile, plan_date=date(2026, 10, 2))
        tracking = DailyTracking(
            profile=profile,
            daily_plan=plan,
            track_date=date(2026, 10, 3),
        )

        with self.assertRaises(ValidationError):
            tracking.full_clean()


class DailyTrackingApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tracking-api")
        self.profile = Profile.objects.create(user=self.user)
        self.plan = DailyPlan.objects.create(profile=self.profile, plan_date=date(2026, 10, 3))
        self.client = APIClient()
        self.url = "/api/tracking/"

    def payload(self, **overrides):
        return {
            "profile": self.profile.id,
            "daily_plan": self.plan.id,
            "track_date": "2026-10-03",
            "outfit_completed": True,
            "meals_completed": False,
            "expenses_reviewed": True,
            "daily_plan_completed": False,
            "notes": "Tracking notes",
            **overrides,
        }

    def test_create_list_retrieve_and_patch_tracking(self):
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.data["outfit_completed"])
        listed = self.client.get(self.url, {"profile_id": self.profile.id})
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)
        detail_url = f"{self.url}{created.data['id']}/"
        retrieved = self.client.get(detail_url)
        self.assertEqual(retrieved.status_code, 200)
        updated = self.client.patch(detail_url, {"meals_completed": True}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertTrue(updated.data["meals_completed"])

    def test_list_filters_by_date_range(self):
        self.client.post(self.url, self.payload(), format="json")
        response = self.client.get(
            self.url,
            {"profile_id": self.profile.id, "start_date": "2026-10-03", "end_date": "2026-10-03"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_summary_counts_completed_pending_and_percentages(self):
        self.client.post(self.url, self.payload(), format="json")
        self.client.post(
            self.url,
            self.payload(
                daily_plan=None,
                track_date="2026-10-04",
                outfit_completed=True,
                meals_completed=True,
                expenses_reviewed=True,
                daily_plan_completed=True,
            ),
            format="json",
        )
        response = self.client.get(
            f"{self.url}summary/",
            {"profile_id": self.profile.id, "start_date": "2026-10-03", "end_date": "2026-10-04"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["completed_tasks"], 6)
        self.assertEqual(response.data["pending_tasks"], 2)
        self.assertEqual(response.data["completion_percentage"], 75.0)
        self.assertEqual(response.data["progress_by_field"]["meals_completed"]["completed_days"], 1)
        self.assertEqual(len(response.data["daily_progress"]), 2)

    def test_rejects_invalid_dates_duplicates_and_mismatched_plan(self):
        invalid = self.client.post(self.url, self.payload(track_date="2026-02-30"), format="json")
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("track_date", invalid.data)
        self.client.post(self.url, self.payload(), format="json")
        duplicate = self.client.post(self.url, self.payload(daily_plan=None), format="json")
        self.assertEqual(duplicate.status_code, 400)

        mismatch = self.client.post(
            self.url,
            self.payload(track_date="2026-10-04"),
            format="json",
        )
        self.assertEqual(mismatch.status_code, 400)

    def test_rejects_non_boolean_completion_and_cross_profile_plan(self):
        invalid_boolean = self.client.post(self.url, self.payload(outfit_completed="yes"), format="json")
        self.assertEqual(invalid_boolean.status_code, 400)
        other_profile = Profile.objects.create(
            user=get_user_model().objects.create_user("tracking-other")
        )
        other_plan = DailyPlan.objects.create(profile=other_profile, plan_date=date(2026, 10, 3))
        mismatch = self.client.post(self.url, self.payload(daily_plan=other_plan.id), format="json")
        self.assertEqual(mismatch.status_code, 400)
