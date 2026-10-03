from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Income(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="income_records"
    )
    source = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    received_on = models.DateField()
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_on", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="income_amount_positive"),
        ]

    def __str__(self):
        return f"{self.source} income on {self.received_on}"


class BudgetCategory(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="budget_categories"
    )
    name = models.CharField(max_length=80)
    monthly_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="A planned monthly amount in the profile's selected currency.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "name"], name="uniq_budget_category_profile_name"
            ),
            models.CheckConstraint(
                condition=models.Q(monthly_limit__gte=0), name="budget_monthly_limit_nonnegative"
            ),
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="expenses"
    )
    category = models.ForeignKey(
        BudgetCategory, on_delete=models.PROTECT, related_name="expenses"
    )
    daily_plan = models.ForeignKey(
        "lifestyle.DailyPlan",
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
    )
    description = models.CharField(max_length=160)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    spent_on = models.DateField()
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-spent_on", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="expense_amount_positive"),
        ]

    def clean(self):
        super().clean()
        if self.category_id and self.profile_id:
            if self.category.profile_id != self.profile_id:
                raise ValidationError({"category": "Choose a category from this profile."})
        if self.daily_plan_id and self.profile_id:
            if self.daily_plan.profile_id != self.profile_id:
                raise ValidationError({"daily_plan": "Choose a plan from this profile."})
            if self.daily_plan.plan_date != self.spent_on:
                raise ValidationError({"daily_plan": "The expense and plan dates must match."})

    def __str__(self):
        return f"{self.description} ({self.amount})"
