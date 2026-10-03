from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

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
