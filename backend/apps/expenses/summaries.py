"""Expense totals and budget comparisons based on stored expense records."""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Sum

from apps.body_shape.models import Profile
from .models import BudgetCategory, Expense


def _money(value):
    return format(value or Decimal("0.00"), ".2f")


def build_expense_summary(profile_id, month):
    start = date(month.year, month.month, 1)
    end = date(month.year, month.month, monthrange(month.year, month.month)[1])
    profile = Profile.objects.get(pk=profile_id)
    profile_expenses = Expense.objects.filter(profile_id=profile_id)
    monthly_expenses = profile_expenses.filter(spent_on__range=(start, end))

    total_spending = profile_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    monthly_spending = monthly_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    category_spend = {
        row["category_id"]: row["total"] or Decimal("0.00")
        for row in monthly_expenses.values("category_id").annotate(total=Sum("amount"))
    }

    categories = BudgetCategory.objects.filter(profile_id=profile_id).order_by("name", "id")
    spending_by_category = []
    for category in categories:
        spent = category_spend.get(category.id, Decimal("0.00"))
        limit = category.monthly_limit
        if not category.is_active:
            status = "inactive"
        elif spent < limit:
            status = "under_limit"
        elif spent == limit:
            status = "at_limit"
        else:
            status = "over_limit"
        spending_by_category.append({
            "category_id": category.id,
            "category": category.name,
            "spent": _money(spent),
            "monthly_limit": _money(limit),
            "budget_status": status,
            "is_active": category.is_active,
        })

    active_categories = [category for category in categories if category.is_active]
    if active_categories:
        budget_limit = sum((category.monthly_limit for category in active_categories), Decimal("0.00"))
        if monthly_spending < budget_limit:
            overall_status = "under_limit"
        elif monthly_spending == budget_limit:
            overall_status = "at_limit"
        else:
            overall_status = "over_limit"
        remaining = max(budget_limit - monthly_spending, Decimal("0.00"))
    else:
        budget_limit = None
        remaining = None
        overall_status = "not_set"

    return {
        "profile_id": profile_id,
        "currency_code": profile.currency_code,
        "month": month.strftime("%Y-%m"),
        "total_spending": _money(total_spending),
        "monthly_spending": _money(monthly_spending),
        "spending_by_category": spending_by_category,
        "monthly_budget": {
            "available": budget_limit is not None,
            "monthly_limit": _money(budget_limit) if budget_limit is not None else None,
            "monthly_spending": _money(monthly_spending),
            "remaining": _money(remaining) if remaining is not None else None,
            "status": overall_status,
        },
    }
