from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from apps.expenses.models import BudgetCategory, Expense
from apps.tracking.models import DailyTracking


class InsightsApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("insights-a")
        self.profile = Profile.objects.create(user=self.user)
        self.other_user = User.objects.create_user("insights-b")
        self.other_profile = Profile.objects.create(user=self.other_user)
        self.client = APIClient()
        self.url = "/api/insights/"
        self.category = BudgetCategory.objects.create(profile=self.profile, name="Food", monthly_limit=Decimal("200.00"))
        self.other_category = BudgetCategory.objects.create(profile=self.other_profile, name="Private", monthly_limit=Decimal("500.00"))
        Expense.objects.create(profile=self.profile, category=self.category, description="Own", amount=Decimal("25.00"), spent_on=date(2026, 10, 5))
        self.other_expense = Expense.objects.create(profile=self.other_profile, category=self.other_category, description="Private", amount=Decimal("700.00"), spent_on=date(2026, 10, 5))
        DailyTracking.objects.create(profile=self.profile, track_date=date(2026, 10, 5), outfit_completed=True)
        DailyTracking.objects.create(profile=self.other_profile, track_date=date(2026, 10, 5), meals_completed=True)

    def test_anonymous_request_is_rejected(self):
        self.assertIn(self.client.get(self.url).status_code, (401, 403))

    def test_authenticated_summary_uses_own_records_and_ignores_forged_profile_fields(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {"profile_id": self.other_profile.id, "profile": self.other_profile.id, "start_date": "2026-10-05", "end_date": "2026-10-05"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile_id"], self.profile.id)
        self.assertEqual(response.data["period"]["expense_total"], "25.00")
        self.assertEqual(response.data["period"]["tracking_days"], 1)
        self.assertEqual(response.data["period"]["completed_tasks"], 1)
        self.assertEqual(response.data["spending_by_category"][0]["category"], "Food")

    def test_two_users_get_separate_summary_and_statistics(self):
        a, b = APIClient(), APIClient()
        a.force_authenticate(self.user)
        b.force_authenticate(self.other_user)
        params = {"start_date": "2026-10-05", "end_date": "2026-10-05"}
        first, second = a.get(self.url, params), b.get(self.url, params)
        self.assertEqual(first.data["period"]["expense_total"], "25.00")
        self.assertEqual(second.data["period"]["expense_total"], "700.00")
        self.assertEqual(first.data["daily_progress"][0]["completed_tasks"], 1)
        self.assertEqual(second.data["daily_progress"][0]["completed_tasks"], 1)

    def test_new_user_receives_valid_empty_state_data(self):
        user = get_user_model().objects.create_user("insights-new")
        Profile.objects.create(user=user)
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["overview"]["wardrobe_items"], 0)
        self.assertEqual(response.data["period"]["expense_total"], "0.00")
        self.assertEqual(response.data["spending_by_category"], [])
        self.assertEqual(response.data["daily_progress"], [])

    def test_existing_other_user_record_is_preserved(self):
        count = Expense.objects.count()
        self.client.force_authenticate(self.user)
        self.client.get(self.url)
        self.assertEqual(Expense.objects.count(), count)
        self.assertTrue(Expense.objects.filter(pk=self.other_expense.pk, profile=self.other_profile).exists())
