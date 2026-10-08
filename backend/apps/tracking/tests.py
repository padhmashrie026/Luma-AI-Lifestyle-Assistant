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
        self.client.force_authenticate(self.user)
        self.url = "/api/tracking/"

    def payload(self, **overrides):
        return {
            "daily_plan": self.plan.id,
            "track_date": "2026-10-03",
            "outfit_completed": True,
            "meals_completed": False,
            "expenses_reviewed": True,
            "daily_plan_completed": False,
            "notes": "Tracking notes",
            **overrides,
        }

    def test_anonymous_tracking_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
        self.assertIn(self.client.post(self.url, self.payload(), format="json").status_code, (401, 403))
        self.assertIn(self.client.get(f"{self.url}summary/").status_code, (401, 403))

    def test_create_list_retrieve_and_patch_tracking(self):
        created = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.data["outfit_completed"])
        listed = self.client.get(self.url)
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
            {"start_date": "2026-10-03", "end_date": "2026-10-03"},
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
            {"start_date": "2026-10-03", "end_date": "2026-10-04"},
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

    def test_forged_profile_fields_are_ignored_and_other_users_records_are_hidden(self):
        other_user = get_user_model().objects.create_user("tracking-private")
        other_profile = Profile.objects.create(user=other_user)
        other_plan = DailyPlan.objects.create(profile=other_profile, plan_date=date(2026, 10, 3))
        other_record = DailyTracking.objects.create(
            profile=other_profile, daily_plan=other_plan, track_date=date(2026, 10, 3)
        )
        created = self.client.post(
            self.url,
            self.payload(daily_plan=None, profile=other_profile.id, profile_id=other_profile.id),
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(DailyTracking.objects.get(pk=created.data["id"]).profile, self.profile)
        listed = self.client.get(self.url, {"profile_id": other_profile.id})
        self.assertEqual([row["id"] for row in listed.data], [created.data["id"]])
        self.assertEqual(self.client.get(f"{self.url}{other_record.id}/").status_code, 404)
        self.assertEqual(self.client.patch(f"{self.url}{other_record.id}/", {"notes": "forged"}, format="json").status_code, 404)

    def test_tracking_summary_ignores_forged_profile_id(self):
        response = self.client.get(
            f"{self.url}summary/",
            {"profile_id": 99999, "start_date": "2026-10-03", "end_date": "2026-10-03"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile_id"], self.profile.id)

    def test_new_user_has_empty_tracking_and_summary(self):
        user = get_user_model().objects.create_user("tracking-new-user")
        Profile.objects.create(user=user)
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get(self.url).data, [])
        summary = self.client.get(
            f"{self.url}summary/", {"start_date": "2026-10-03", "end_date": "2026-10-03"}
        )
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data["tracking_days"], 0)
