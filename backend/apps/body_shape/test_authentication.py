from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Profile


class AuthenticationApiTests(TestCase):
    password = "G7!vQm2#rPx9"
    registration_url = "/api/auth/register/"
    login_url = "/api/auth/login/"
    current_url = "/api/auth/me/"
    logout_url = "/api/auth/logout/"

    def setUp(self):
        self.client = APIClient()

    def registration_data(self, **overrides):
        return {
            "username": "riley",
            "email": "riley@example.com",
            "password": self.password,
            "password_confirmation": self.password,
            **overrides,
        }

    def test_successful_registration_returns_safe_account_and_one_profile(self):
        response = self.client.post(
            self.registration_url, self.registration_data(), format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "riley")
        self.assertEqual(response.data["email"], "riley@example.com")
        self.assertEqual(response.data["profile"]["currency_code"], "INR")
        self.assertNotIn("password", response.data)
        self.assertNotIn("user_id", response.data)
        self.assertNotIn("profile_id", response.data)
        user = get_user_model().objects.get(username="riley")
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

    def test_registration_rejects_invalid_data_and_client_identity_fields(self):
        weak_password = self.client.post(
            self.registration_url,
            self.registration_data(password="password", password_confirmation="password"),
            format="json",
        )
        mismatch = self.client.post(
            self.registration_url,
            self.registration_data(password_confirmation="Different!Password47"),
            format="json",
        )
        forged_id = self.client.post(
            self.registration_url,
            self.registration_data(profile_id=1),
            format="json",
        )

        self.assertEqual(weak_password.status_code, 400)
        self.assertIn("password", weak_password.data)
        self.assertEqual(mismatch.status_code, 400)
        self.assertIn("password_confirmation", mismatch.data)
        self.assertEqual(forged_id.status_code, 400)
        self.assertIn("profile_id", forged_id.data)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

    def test_registration_rejects_duplicate_username_and_email(self):
        User = get_user_model()
        User.objects.create_user(
            username="riley", email="other@example.com", password=self.password
        )
        duplicate_username = self.client.post(
            self.registration_url, self.registration_data(), format="json"
        )
        duplicate_email = self.client.post(
            self.registration_url,
            self.registration_data(username="another", email="OTHER@example.com"),
            format="json",
        )

        self.assertEqual(duplicate_username.status_code, 400)
        self.assertIn("username", duplicate_username.data)
        self.assertEqual(duplicate_email.status_code, 400)
        self.assertIn("email", duplicate_email.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 0)

    def test_registration_requires_a_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        rejected = client.post(
            self.registration_url, self.registration_data(), format="json"
        )
        self.assertEqual(rejected.status_code, 403)

        token_response = client.get("/api/auth/csrf/")
        self.assertEqual(token_response.status_code, 200)
        token = token_response.data["csrfToken"]
        accepted = client.post(
            self.registration_url,
            self.registration_data(),
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(accepted.status_code, 201)

    def test_login_success_returns_current_account_and_session(self):
        user = get_user_model().objects.create_user(
            username="riley", email="riley@example.com", password=self.password
        )
        Profile.objects.create(user=user, display_name="Riley")

        response = self.client.post(
            self.login_url,
            {"username": "riley", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "riley")
        self.assertEqual(response.data["profile"]["display_name"], "Riley")
        self.assertIn("sessionid", self.client.cookies)
        current = self.client.get(self.current_url)
        self.assertEqual(current.status_code, 200)
        self.assertEqual(current.data["username"], "riley")

    def test_login_failure_does_not_create_a_session(self):
        get_user_model().objects.create_user(
            username="riley", password=self.password
        )

        response = self.client.post(
            self.login_url,
            {"username": "riley", "password": "incorrect"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("sessionid", self.client.cookies)

    def test_current_account_requires_authentication(self):
        response = self.client.get(self.current_url)
        self.assertIn(response.status_code, (401, 403))

    def test_logout_ends_the_authenticated_session(self):
        get_user_model().objects.create_user(
            username="riley", password=self.password
        )
        self.client.post(
            self.login_url,
            {"username": "riley", "password": self.password},
            format="json",
        )

        response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, 204)
        self.assertNotIn("_auth_user_id", self.client.session)
        current = self.client.get(self.current_url)
        self.assertIn(current.status_code, (401, 403))
