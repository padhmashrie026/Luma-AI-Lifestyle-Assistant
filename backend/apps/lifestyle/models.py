from django.core.exceptions import ValidationError
from django.db import models


class DailyPlan(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="daily_plans"
    )
    plan_date = models.DateField()
    outfit = models.ForeignKey(
        "outfits.Outfit",
        on_delete=models.SET_NULL,
        related_name="daily_plans",
        null=True,
        blank=True,
    )
    meal_plan = models.OneToOneField(
        "diet.MealPlan",
        on_delete=models.SET_NULL,
        related_name="daily_plan",
        null=True,
        blank=True,
    )
    notes = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-plan_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "plan_date"], name="uniq_daily_plan_profile_day"
            ),
        ]

    def clean(self):
        super().clean()
        if self.outfit_id and self.profile_id:
            if self.outfit.profile_id != self.profile_id:
                raise ValidationError({"outfit": "Choose an outfit from this profile."})
        if self.meal_plan_id and self.profile_id:
            if self.meal_plan.profile_id != self.profile_id:
                raise ValidationError({"meal_plan": "Choose a meal plan from this profile."})
            if self.meal_plan.plan_date != self.plan_date:
                raise ValidationError({"meal_plan": "The meal plan and daily plan dates must match."})

    def __str__(self):
        return f"Daily plan for {self.profile} on {self.plan_date}"


class DailyTask(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="daily_tasks"
    )
    daily_plan = models.ForeignKey(
        DailyPlan, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=400, blank=True)
    task_date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["task_date", "created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gt=0), name="daily_task_duration_positive"
            ),
        ]

    def clean(self):
        super().clean()
        if self.daily_plan_id and self.profile_id and self.daily_plan.profile_id != self.profile_id:
            raise ValidationError({"daily_plan": "Choose a daily plan from this profile."})

    def __str__(self):
        return self.title
