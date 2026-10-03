from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Profile
from .calculations import calculate_body_shape


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
        self.profile_url = f"/api/profile/?profile_id={self.profile.id}"
        self.settings_url = f"/api/settings/?profile_id={self.profile.id}"

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

    def test_profile_requires_existing_profile_id(self):
        missing = self.client.get("/api/profile/")
        self.assertEqual(missing.status_code, 400)
        self.assertIn("profile_id", missing.data)
        invalid = self.client.get("/api/profile/?profile_id=0")
        self.assertEqual(invalid.status_code, 400)
        unknown = self.client.get("/api/profile/?profile_id=999999")
        self.assertEqual(unknown.status_code, 404)

    def test_retrieve_and_update_settings_use_existing_currency_preference(self):
        retrieved = self.client.get(self.settings_url)
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.data, {"profile_id": self.profile.id, "currency_code": "INR"})
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
