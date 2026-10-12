import os
import subprocess
import sys
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from config.settings import env_bool


class DeploymentConfigurationTests(SimpleTestCase):
    def test_environment_boolean_parsing(self):
        with patch.dict("os.environ", {"TEST_FLAG": "false"}):
            self.assertFalse(env_bool("TEST_FLAG", True))
        with patch.dict("os.environ", {"TEST_FLAG": "yes"}):
            self.assertTrue(env_bool("TEST_FLAG", False))

    def test_render_environment_forces_secure_production_configuration(self):
        environment = os.environ.copy()
        environment.update(
            {
                "RENDER": "true",
                "RENDER_EXTERNAL_HOSTNAME": "luma-example.onrender.com",
                "DEBUG": "true",
                "DJANGO_SECRET_KEY": "test-only-secret-key",
                "DATABASE_URL": "postgres://test:test@ep-example.neon.tech/luma",
            }
        )
        environment.pop("ALLOWED_HOSTS", None)
        check_settings = (
            "from django.conf import settings; "
            "assert settings.DEBUG is False; "
            "assert settings.SECURE_SSL_REDIRECT is True; "
            "assert settings.SESSION_COOKIE_SECURE is True; "
            "assert settings.CSRF_COOKIE_SECURE is True; "
            "assert 'luma-example.onrender.com' in settings.ALLOWED_HOSTS; "
            "assert 'https://luma-example.onrender.com' in settings.CSRF_TRUSTED_ORIGINS; "
            "assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'; "
            "assert settings.DATABASES['default']['OPTIONS']['sslmode'] == 'require'"
        )
        result = subprocess.run(
            [sys.executable, "-c", check_settings],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    @override_settings(DEBUG=False, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
    def test_production_cookie_settings_are_secure(self):
        self.assertFalse(settings.DEBUG)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)

    def test_root_and_client_routes_render_the_react_shell(self):
        for url in ("/", "/dashboard", "/wardrobe/items"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'id="root"')

    def test_backend_routes_do_not_fall_back_to_react(self):
        for url in ("/api/not-a-real-route/", "/static/not-a-real-file.js"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_real_api_and_admin_routes_do_not_fall_back_to_react(self):
        api_response = self.client.get("/api/auth/csrf/")
        self.assertEqual(api_response.status_code, 200)
        self.assertNotContains(api_response, 'id="root"')

        admin_response = self.client.get("/admin/")
        self.assertEqual(admin_response.status_code, 302)
        self.assertEqual(admin_response.headers["Location"], "/admin/login/?next=/admin/")

        admin_login_response = self.client.get("/admin/login/")
        self.assertEqual(admin_login_response.status_code, 200)
        self.assertNotContains(admin_login_response, 'id="root"')
