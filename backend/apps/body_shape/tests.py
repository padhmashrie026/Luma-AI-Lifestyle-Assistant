from django.test import SimpleTestCase
from rest_framework.test import APIClient

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
