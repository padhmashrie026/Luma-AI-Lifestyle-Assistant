from django.core.exceptions import ValidationError
from django.db import models


class DailyTracking(models.Model):
    profile = models.ForeignKey(
        "body_shape.Profile", on_delete=models.CASCADE, related_name="tracking_days"
    )
    daily_plan = models.OneToOneField(
        "lifestyle.DailyPlan",
        on_delete=models.SET_NULL,
        related_name="tracking_record",
        null=True,
        blank=True,
    )
    track_date = models.DateField()
    outfit_completed = models.BooleanField(default=False)
    meals_completed = models.BooleanField(default=False)
    expenses_reviewed = models.BooleanField(default=False)
    daily_plan_completed = models.BooleanField(default=False)
    notes = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-track_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "track_date"], name="uniq_tracking_profile_day"
            ),
        ]

    def clean(self):
        super().clean()
        if self.daily_plan_id and self.profile_id:
            if self.daily_plan.profile_id != self.profile_id:
                raise ValidationError({"daily_plan": "Choose a plan from this profile."})
            if self.daily_plan.plan_date != self.track_date:
                raise ValidationError({"daily_plan": "The tracking and plan dates must match."})

    def __str__(self):
        return f"Tracking for {self.profile} on {self.track_date}"
