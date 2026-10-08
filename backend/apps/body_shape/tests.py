from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient
from io import StringIO

from .models import BodyMeasurement, Profile
from .calculations import calculate_body_shape
from ..diet.models import Meal, MealPlan, MealPlanItem
from ..expenses.models import BudgetCategory, Expense, Income
from ..lifestyle.models import DailyPlan
from ..outfits.models import Outfit, OutfitItem
from ..tracking.models import DailyTracking
from ..wardrobe.models import WardrobeItem


class BodyShapeCalculationTests(SimpleTestCase):
    def test_hourglass_measurements(self):
        result = calculate_body_shape(shoulder=90, bust=90, waist=65, hip=92)
        self.assertEqual(result["estimated_body_shape"], "hourglass")
        self.assertIn("not a scientific or medical diagnosis", result["note"])

    def test_pear_measurements(self):
        result = calculate_body_shape(shoulder=85, bust=88, waist=72, hip=105)
        self.assertEqual(result["estimated_body_shape"], "pear")

    def test_api_returns_guidance_for_valid_measurements(self):
        response = APIClient().post(
            "/api/body-shape/calculate/",
            {"shoulder": 90, "bust": 90, "waist": 65, "hip": 92},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["estimated_body_shape"], "hourglass")
        self.assertIn("styling_suggestion", response.data)
        self.assertIn("approximate_size_guidance", response.data)

    def test_api_rejects_non_numeric_and_non_positive_measurements(self):
        base = {"shoulder": 90, "bust": 90, "waist": 65, "hip": 92}
        for invalid in ("90", 0, -1, True):
            payload = {**base, "shoulder": invalid}
            with self.subTest(value=invalid):
                response = APIClient().post(
                    "/api/body-shape/calculate/", payload, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("shoulder", response.data)

    def test_api_rejects_missing_measurement(self):
        response = APIClient().post(
            "/api/body-shape/calculate/",
            {"shoulder": 90, "bust": 90, "waist": 65},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("hip", response.data)


class ProfileAndSettingsApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="profile-settings-user", email="old@example.com"
        )
        self.profile = Profile.objects.create(user=self.user, display_name="Old name")
        self.client = APIClient()
        self.profile_url = "/api/profile/"
        self.settings_url = "/api/settings/"
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_returns_existing_profile_and_user_fields(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.profile.id)
        self.assertEqual(response.data["username"], "profile-settings-user")
        self.assertEqual(response.data["display_name"], "Old name")
        self.assertEqual(response.data["email"], "old@example.com")

    def test_update_profile_persists_profile_and_builtin_user_fields(self):
        response = self.client.patch(
            self.profile_url,
            {
                "display_name": "  Riley  ",
                "first_name": "  Riley ",
                "last_name": " Example  ",
                "email": "riley@example.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.display_name, "Riley")
        self.assertEqual(self.user.first_name, "Riley")
        self.assertEqual(self.user.last_name, "Example")
        self.assertEqual(self.user.email, "riley@example.com")

    def test_profile_allows_supported_empty_name_values_and_empty_patch(self):
        response = self.client.patch(
            self.profile_url,
            {"display_name": "", "first_name": "", "last_name": "", "email": ""},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["display_name"], "")
        self.assertEqual(self.client.patch(self.profile_url, {}, format="json").status_code, 200)

    def test_profile_rejects_invalid_email_and_fields_not_in_model(self):
        invalid_email = self.client.patch(
            self.profile_url, {"email": "not-an-email"}, format="json"
        )
        self.assertEqual(invalid_email.status_code, 400)
        self.assertIn("email", invalid_email.data)
        unsupported = self.client.patch(
            self.profile_url, {"age": 30}, format="json"
        )
        self.assertEqual(unsupported.status_code, 400)
        self.assertIn("age", unsupported.data)

    def test_profile_requests_ignore_forged_profile_ids(self):
        other = get_user_model().objects.create_user(username="another-profile")
        other_profile = Profile.objects.create(user=other, display_name="Other")
        response = self.client.get(f"/api/profile/?profile_id={other_profile.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.profile.id)
        updated = self.client.patch(
            f"/api/profile/?profile_id={other_profile.id}",
            {"display_name": "Changed own", "email": "own@example.com"},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        other_profile.refresh_from_db()
        self.assertEqual(other_profile.display_name, "Other")

    def test_profile_requires_authentication(self):
        response = APIClient().get(self.profile_url)
        self.assertIn(response.status_code, (401, 403))

    def test_retrieve_and_update_settings_use_existing_currency_preference(self):
        retrieved = self.client.get(self.settings_url)
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.data, {"currency_code": "INR"})
        updated = self.client.patch(
            self.settings_url, {"currency_code": " usd "}, format="json"
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["currency_code"], "USD")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.currency_code, "USD")

    def test_settings_reject_empty_malformed_and_unsupported_fields(self):
        for value in ("", "US", "USDX", "1NZ"):
            with self.subTest(currency_code=value):
                response = self.client.patch(
                    self.settings_url, {"currency_code": value}, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("currency_code", response.data)
        unknown = self.client.patch(self.settings_url, {"theme": "dark"}, format="json")
        self.assertEqual(unknown.status_code, 400)
        self.assertIn("theme", unknown.data)


class BodyMeasurementOwnershipTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user_a = User.objects.create_user(username="measure-a")
        self.user_b = User.objects.create_user(username="measure-b")
        self.profile_a = Profile.objects.create(user=self.user_a)
        self.profile_b = Profile.objects.create(user=self.user_b)
        self.client = APIClient()
        self.url = "/api/body-shape/measurements/"
        self.payload = {
            "measured_on": "2026-10-04", "shoulder_cm": 90, "bust_cm": 90,
            "waist_cm": 65, "hip_cm": 92, "styling_shape": "hourglass",
        }

    def test_authenticated_user_can_create_read_and_update_measurements(self):
        self.client.force_authenticate(self.user_a)
        created = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(BodyMeasurement.objects.get().profile, self.profile_a)
        retrieved = self.client.get(self.url)
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.data["styling_shape"], "hourglass")
        updated = self.client.patch(self.url, {"styling_shape": "pear"}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["styling_shape"], "pear")
        self.assertEqual(BodyMeasurement.objects.count(), 1)

    def test_measurements_require_authentication(self):
        for response in (
            self.client.get(self.url),
            self.client.post(self.url, self.payload, format="json"),
        ):
            self.assertIn(response.status_code, (401, 403))

    def test_user_cannot_read_or_update_another_users_measurements(self):
        BodyMeasurement.objects.create(profile=self.profile_b, **self.payload)
        self.client.force_authenticate(self.user_a)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(
            self.client.patch(self.url, {"styling_shape": "pear"}, format="json").status_code,
            404,
        )
        self.assertEqual(BodyMeasurement.objects.get().styling_shape, "hourglass")

    def test_new_registration_has_no_demo_measurements(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "new-measurer", "email": "new@example.com",
             "password": "Qv9!mB2#pL7x", "password_confirmation": "Qv9!mB2#pL7x"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        new_user = get_user_model().objects.get(username="new-measurer")
        self.assertEqual(BodyMeasurement.objects.filter(profile__user=new_user).count(), 0)
        self.assertEqual(BodyMeasurement.objects.filter(profile=self.profile_b).count(), 0)


class DemoSeederCommandTests(TestCase):
    def test_seed_command_is_idempotent_and_preserves_existing_demo_records(self):
        user = get_user_model().objects.create_user(username="seed-demo", password="not-a-real-login")
        profile = Profile.objects.create(user=user, display_name="Demo User", currency_code="USD")
        existing_item = WardrobeItem.objects.create(
            profile=profile,
            name="Demo blue cotton shirt",
            category=WardrobeItem.Category.TOP,
            color="blue",
            notes="Keep this existing note",
        )
        personal_item = WardrobeItem.objects.create(
            profile=profile,
            name="Personal jacket",
            category=WardrobeItem.Category.OUTERWEAR,
            color="black",
        )

        first_output = StringIO()
        call_command("seed_demo_data", stdout=first_output)
        counts_after_first_run = self._demo_counts()

        second_output = StringIO()
        call_command("seed_demo_data", stdout=second_output)
        counts_after_second_run = self._demo_counts()

        self.assertEqual(counts_after_first_run, counts_after_second_run)
        self.assertIn("reused", second_output.getvalue())
        profile.refresh_from_db()
        existing_item.refresh_from_db()
        self.assertEqual(profile.currency_code, "USD")
        self.assertEqual(existing_item.notes, "Keep this existing note")
        self.assertTrue(WardrobeItem.objects.filter(pk=personal_item.pk).exists())
        self.assertTrue(Meal.objects.filter(profile=profile, meal_type=Meal.MealType.BREAKFAST).exists())
        self.assertTrue(Meal.objects.filter(profile=profile, meal_type=Meal.MealType.LUNCH).exists())
        self.assertTrue(Meal.objects.filter(profile=profile, meal_type=Meal.MealType.DINNER).exists())
        self.assertTrue(MealPlanItem.objects.filter(meal_plan__profile=profile).exists())
        self.assertTrue(OutfitItem.objects.filter(outfit__profile=profile).exists())
        self.assertTrue(BudgetCategory.objects.filter(profile=profile).exists())
        self.assertTrue(Expense.objects.filter(profile=profile).exists())
        self.assertTrue(Income.objects.filter(profile=profile).exists())
        self.assertTrue(DailyPlan.objects.filter(profile=profile).exists())
        self.assertTrue(DailyTracking.objects.filter(profile=profile).exists())

    def _demo_counts(self):
        return (
            Profile.objects.count(),
            Meal.objects.count(),
            MealPlan.objects.count(),
            MealPlanItem.objects.count(),
            WardrobeItem.objects.count(),
            Outfit.objects.count(),
            OutfitItem.objects.count(),
            BudgetCategory.objects.count(),
            Expense.objects.count(),
            Income.objects.count(),
            DailyPlan.objects.count(),
            DailyTracking.objects.count(),
        )
