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
        self.user = user_model.objects.create_user("expense-api-user")
        self.profile = Profile.objects.create(user=self.user)
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
        self.client.force_authenticate(self.user)
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

    def test_anonymous_expenses_and_summary_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        for response in (
            self.client.get(self.collection_url),
            self.client.post(self.collection_url, self._payload(), format="json"),
            self.client.get(f"{self.collection_url}summary/"),
            self.client.get(f"{self.collection_url}{self.expense.id}/"),
        ):
            self.assertIn(response.status_code, (401, 403))

    def test_create_expense(self):
        response = self.client.post(self.collection_url, self._payload(), format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["amount"], "12.50")
        self.assertEqual(response.data["category"], self.food.id)
        created = Expense.objects.get(description="Market shopping")
        self.assertEqual(created.profile, self.profile)

    def test_forged_profile_values_cannot_change_expense_owner(self):
        response = self.client.post(
            self.collection_url,
            self._payload(profile=self.other_profile.id, profile_id=self.other_profile.id),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Expense.objects.get(description="Market shopping").profile, self.profile)

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

    def test_list_and_detail_never_expose_another_profiles_expense(self):
        other_category = self.other_category = BudgetCategory.objects.create(
            profile=self.other_profile, name="Other travel", monthly_limit=Decimal("30.00")
        )
        other_expense = Expense.objects.create(
            profile=self.other_profile, category=other_category, description="Other spend",
            amount=Decimal("5.00"), spent_on=date(2026, 10, 5),
        )
        listed = self.client.get(self.collection_url, {"profile_id": self.other_profile.id})
        self.assertEqual([row["id"] for row in listed.data], [self.expense.id])
        self.assertEqual(self.client.get(f"{self.collection_url}{other_expense.id}/").status_code, 404)
        self.assertEqual(
            self.client.patch(f"{self.collection_url}{other_expense.id}/", {"amount": "9.00"}, format="json").status_code,
            404,
        )
        self.assertEqual(self.client.delete(f"{self.collection_url}{other_expense.id}/").status_code, 404)

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
            {"month": "2026-10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_spending"], "118.00")
        self.assertEqual(response.data["monthly_spending"], "110.00")
        self.assertEqual(response.data["monthly_budget"]["monthly_limit"], "110.00")
        self.assertEqual(response.data["monthly_budget"]["status"], "at_limit")
        by_name = {row["category"]: row for row in response.data["spending_by_category"]}
        self.assertEqual(by_name["Food"]["spent"], "40.00")
        self.assertEqual(by_name["Transport"]["budget_status"], "over_limit")

    def test_summary_uses_signed_in_profile_and_validates_month(self):
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"profile_id": self.other_profile.id, "month": "2026-13"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("month", response.data)

    def test_summary_reports_budget_unavailable_without_categories(self):
        user = get_user_model().objects.create_user("no-budget")
        Profile.objects.create(user=user)
        self.client.force_authenticate(user)
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"month": "2026-10"},
        )
        self.assertFalse(response.data["monthly_budget"]["available"])
        self.assertEqual(response.data["monthly_budget"]["status"], "not_set")

    def test_summary_never_includes_other_users_totals_or_categories(self):
        other_category = BudgetCategory.objects.create(
            profile=self.other_profile, name="Other food", monthly_limit=Decimal("900.00")
        )
        Expense.objects.create(
            profile=self.other_profile, category=other_category, description="Other payment",
            amount=Decimal("800.00"), spent_on=date(2026, 10, 5),
        )
        response = self.client.get(
            f"{self.collection_url}summary/",
            {"profile_id": self.other_profile.id, "month": "2026-10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_spending"], "40.00")
        self.assertEqual([row["category"] for row in response.data["spending_by_category"]], ["Food", "Transport"])


class BudgetCategoryApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_a = user_model.objects.create_user("category-user-a")
        self.user_b = user_model.objects.create_user("category-user-b")
        self.profile_a = Profile.objects.create(user=self.user_a)
        self.profile_b = Profile.objects.create(user=self.user_b)
        self.category_b = BudgetCategory.objects.create(
            profile=self.profile_b, name="Private category", monthly_limit=Decimal("50.00")
        )
        self.url = "/api/expenses/categories/"
        self.client = APIClient()
        self.client.force_authenticate(self.user_a)

    def test_anonymous_category_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
        self.assertIn(
            self.client.post(self.url, {"name": "Food", "monthly_limit": "100.00"}, format="json").status_code,
            (401, 403),
        )

    def test_user_can_create_and_list_own_categories(self):
        created = self.client.post(
            self.url, {"name": " Food ", "monthly_limit": "100.00"}, format="json"
        )
        self.assertEqual(created.status_code, 201)
        category = BudgetCategory.objects.get(name="Food")
        self.assertEqual(category.profile, self.profile_a)
        listed = self.client.get(self.url)
        self.assertEqual([row["id"] for row in listed.data], [category.id])

    def test_user_cannot_see_or_use_another_users_category(self):
        listed = self.client.get(self.url)
        self.assertNotIn(self.category_b.id, [row["id"] for row in listed.data])
        expense = self.client.post(
            "/api/expenses/",
            {"category": self.category_b.id, "description": "Blocked", "amount": "12.00", "spent_on": "2026-10-08"},
            format="json",
        )
        self.assertEqual(expense.status_code, 400)
        self.assertFalse(Expense.objects.filter(description="Blocked").exists())

    def test_forged_profile_id_cannot_change_category_owner(self):
        created = self.client.post(
            self.url,
            {"name": "Own category", "monthly_limit": "75.00", "profile": self.profile_b.id, "profile_id": self.profile_b.id},
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        category = BudgetCategory.objects.get(name="Own category")
        self.assertEqual(category.profile, self.profile_a)

    def test_new_category_can_be_used_for_an_expense(self):
        created = self.client.post(
            self.url, {"name": "New user food", "monthly_limit": "125.00"}, format="json"
        )
        self.assertEqual(created.status_code, 201)
        expense = self.client.post(
            "/api/expenses/",
            {"category": created.data["id"], "description": "First expense", "amount": "12.00", "spent_on": "2026-10-08"},
            format="json",
        )
        self.assertEqual(expense.status_code, 201)
        saved = Expense.objects.get(description="First expense")
        self.assertEqual(saved.profile, self.profile_a)
        self.assertEqual(saved.category_id, created.data["id"])
