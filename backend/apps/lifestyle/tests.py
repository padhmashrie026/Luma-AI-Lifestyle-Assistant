from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.body_shape.models import Profile
from apps.diet.models import MealPlan
from apps.lifestyle.models import DailyPlan
from apps.outfits.models import Outfit


class DailyPlanValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.profile = Profile.objects.create(user=user_model.objects.create_user("planner"))
        self.other_profile = Profile.objects.create(
            user=user_model.objects.create_user("someone_else")
        )

    def test_daily_plan_cannot_use_another_profiles_outfit(self):
        outfit = Outfit.objects.create(profile=self.other_profile, name="Other person's look")
        plan = DailyPlan(profile=self.profile, plan_date=date(2026, 10, 2), outfit=outfit)

        with self.assertRaises(ValidationError):
            plan.full_clean()

    def test_daily_plan_meal_plan_must_be_for_the_same_date(self):
        meal_plan = MealPlan.objects.create(profile=self.profile, plan_date=date(2026, 10, 1))
        plan = DailyPlan(
            profile=self.profile,
            plan_date=date(2026, 10, 2),
            meal_plan=meal_plan,
        )

        with self.assertRaises(ValidationError):
            plan.full_clean()
