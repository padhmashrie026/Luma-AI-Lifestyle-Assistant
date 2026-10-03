from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from apps.expenses.models import BudgetCategory, Expense
from apps.lifestyle.models import DailyPlan


class ExpenseValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.profile = Profile.objects.create(user=user_model.objects.create_user("spender"))
        self.other_profile = Profile.objects.create(
            user=user_model.objects.create_user("other_spender")
        )
        self.other_category = BudgetCategory.objects.create(
            profile=self.other_profile,
            name="Other household",
            monthly_limit=Decimal("100.00"),
        )

    def test_expense_cannot_use_another_profiles_category(self):
        expense = Expense(
            profile=self.profile,
            category=self.other_category,
            description="Lunch",
            amount=Decimal("12.50"),
            spent_on=date(2026, 10, 2),
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_expense_uses_decimal_amount(self):
        category = BudgetCategory.objects.create(
            profile=self.profile,
            name="Food",
            monthly_limit=Decimal("200.00"),
        )
        Expense.objects.create(
            profile=self.profile,
            category=category,
            description="Lunch",
            amount=Decimal("12.50"),
            spent_on=date(2026, 10, 2),
        )

        saved_expense = Expense.objects.get(description="Lunch")
        self.assertEqual(saved_expense.amount, Decimal("12.50"))
        self.assertIsInstance(saved_expense.amount, Decimal)


class ExpenseApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.profile = Profile.objects.create(user=user_model.objects.create_user("expense-api-user"))
        self.other_profile = Profile.objects.create(
            user=user_model.objects.create_user("expense-api-other")
        )
        self.food = BudgetCategory.objects.create(
            profile=self.profile, name="Food", monthly_limit=Decimal("60.00")
        )
        self.transport = BudgetCategory.objects.create(
            profile=self.profile, name="Transport", monthly_limit=Decimal("50.00")
        )
        self.client = APIClient()
        self.collection_url = "/api/expenses/"
        self.expense = Expense.objects.create(
            profile=self.profile,
            category=self.food,
            description="Groceries",
            amount=Decimal("40.00"),
            spent_on=date(2026, 10, 5),
        )

    def _payload(self, **overrides):
        payload = {
            "profile": self.profile.id,
            "category": self.food.id,
            "description": "Market shopping",
            "amount": "12.50",
            "spent_on": "2026-10-10",
            "notes": "Weekly shop",
        }
        payload.update(overrides)
        return payload

    def test_list_expenses(self):
        response = self.client.get(self.collection_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["description"], "Groceries")

    def test_create_expense(self):
        response = self.client.post(self.collection_url, self._payload(), format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["amount"], "12.50")
        self.assertEqual(response.data["category"], self.food.id)

    def test_retrieve_expense(self):
        response = self.client.get(f"{self.collection_url}{self.expense.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.expense.id)

    def test_update_expense(self):
        response = self.client.patch(
            f"{self.collection_url}{self.expense.id}/",
            {"amount": "45.25", "description": "Grocery run"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["amount"], "45.25")
        self.assertEqual(response.data["description"], "Grocery run")

    def test_delete_expense(self):
        response = self.client.delete(f"{self.collection_url}{self.expense.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Expense.objects.filter(pk=self.expense.id).exists())

    def test_invalid_amount_and_required_fields_are_rejected(self):
        for amount in ("0", "-1", "not-a-number"):
            with self.subTest(amount=amount):
                response = self.client.post(
                    self.collection_url, self._payload(amount=amount), format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("amount", response.data)
        response = self.client.post(
            self.collection_url, self._payload(description="   "), format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)

    def test_invalid_date_and_cross_profile_category_are_rejected(self):
        response = self.client.post(
            self.collection_url, self._payload(spent_on="2026-02-30"), format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("spent_on", response.data)

        other_category = BudgetCategory.objects.create(
            profile=self.other_profile, name="Other", monthly_limit=Decimal("10.00")
        )
        response = self.client.post(
            self.collection_url, self._payload(category=other_category.id), format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("category", response.data)

    def test_daily_plan_must_match_profile_and_expense_date(self):
        plan = DailyPlan.objects.create(profile=self.profile, plan_date=date(2026, 10, 11))
        response = self.client.post(
            self.collection_url,
            self._payload(daily_plan=plan.id, spent_on="2026-10-10"),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("daily_plan", response.data)

    def test_filter_by_month_category_and_search(self):
        Expense.objects.create(
            profile=self.profile,
            category=self.transport,
            description="Bus pass",
            amount=Decimal("20.00"),
            spent_on=date(2026, 10, 6),
        )
        Expense.objects.create(
            profile=self.profile,
            category=self.food,
            description="Old groceries",
            amount=Decimal("8.00"),
            spent_on=date(2026, 9, 6),
        )
        response = self.client.get(
            self.collection_url,
            {"month": "2026-10", "category_id": self.food.id, "q": "grocer"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data], [self.expense.id])

    def test_summary_calculates_totals_and_budget_status(self):
        Expense.objects.create(
            profile=self.profile,
            category=self.transport,
            description="Taxi",
            amount=Decimal("70.00"),
            spent_on=date(2026, 10, 6),
        )
        Expense.objects.create(
            profile=self.profile,
            category=self.food,
            description="September meal",
            amount=Decimal("8.00"),
            spent_on=date(2026, 9, 6),
        )
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"profile_id": self.profile.id, "month": "2026-10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_spending"], "118.00")
        self.assertEqual(response.data["monthly_spending"], "110.00")
        self.assertEqual(response.data["monthly_budget"]["monthly_limit"], "110.00")
        self.assertEqual(response.data["monthly_budget"]["status"], "at_limit")
        by_name = {row["category"]: row for row in response.data["spending_by_category"]}
        self.assertEqual(by_name["Food"]["spent"], "40.00")
        self.assertEqual(by_name["Transport"]["budget_status"], "over_limit")

    def test_summary_requires_profile_and_valid_month(self):
        response = self.client.get(f"{self.collection_url}summary/", {"month": "2026-10"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("profile_id", response.data)
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"profile_id": self.profile.id, "month": "2026-13"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("month", response.data)

    def test_summary_reports_budget_unavailable_without_categories(self):
        profile = Profile.objects.create(user=get_user_model().objects.create_user("no-budget"))
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"profile_id": profile.id, "month": "2026-10"},
        )
        self.assertFalse(response.data["monthly_budget"]["available"])
        self.assertEqual(response.data["monthly_budget"]["status"], "not_set")
