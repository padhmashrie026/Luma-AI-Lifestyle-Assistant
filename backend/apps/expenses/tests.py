from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.body_shape.models import Profile
from apps.expenses.models import BudgetCategory, Expense


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
