from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import BodyMeasurement, Profile
from apps.wardrobe.models import WardrobeItem
from .models import Outfit, OutfitItem


class OutfitRecommendationTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="outfit-test")
        self.profile = Profile.objects.create(user=user)
        self.top = WardrobeItem.objects.create(
            profile=self.profile, name="Linen top", category=WardrobeItem.Category.TOP
        )
        self.bottom = WardrobeItem.objects.create(
            profile=self.profile, name="Cotton trousers", category=WardrobeItem.Category.BOTTOM
        )
        self.url = "/api/outfits/recommend/"
        self.client = APIClient()

    def payload(self, **overrides):
        return {"profile_id": self.profile.id, "occasion": "everyday", **overrides}

    def test_recommends_stored_available_items(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["recommendation_available"])
        recommendation = response.data["recommendation"]
        self.assertEqual(recommendation["selected_top"]["id"], self.top.id)
        self.assertEqual(recommendation["selected_bottom"]["id"], self.bottom.id)

    def test_uses_requested_body_shape_for_guidance(self):
        response = self.client.post(self.url, self.payload(body_shape="Pear"), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["body_shape"], "pear")
        self.assertIn("pear", response.data["explanation"])

    def test_uses_latest_saved_body_shape_when_not_supplied(self):
        BodyMeasurement.objects.create(
            profile=self.profile, measured_on=date(2026, 10, 1),
            styling_shape=BodyMeasurement.StylingShape.RECTANGLE,
        )
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.data["body_shape"], "rectangle")

    def test_prefers_a_saved_look_matching_the_occasion(self):
        other_top = WardrobeItem.objects.create(
            profile=self.profile, name="Silk blouse", category=WardrobeItem.Category.TOP
        )
        formal_look = Outfit.objects.create(
            profile=self.profile, name="Office pairing", occasion=Outfit.Occasion.WORK
        )
        OutfitItem.objects.create(outfit=formal_look, item=other_top)
        OutfitItem.objects.create(outfit=formal_look, item=self.bottom)
        response = self.client.post(self.url, self.payload(occasion="work"), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["recommendation"]["selected_top"]["id"], other_top.id)
        self.assertIn("saved work outfit", response.data["explanation"])

    def test_items_not_marked_available_are_not_recommended(self):
        self.bottom.status = WardrobeItem.Status.LAUNDRY
        self.bottom.save()
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertFalse(response.data["recommendation_available"])
        self.assertEqual(response.data["missing_items"], ["bottom"])
        self.assertIsNone(response.data["recommendation"])

    def test_season_is_rejected_because_model_has_no_season_field(self):
        response = self.client.post(self.url, self.payload(season="summer"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("season", response.data)

    def test_invalid_input_is_rejected(self):
        for payload in (
            {"profile_id": self.profile.id},
            self.payload(occasion="casual"),
            self.payload(body_shape="not_set"),
            self.payload(profile_id=99999),
        ):
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, 400)

    def test_response_contains_expected_structure(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        for key in (
            "recommendation_available", "profile_id", "occasion", "body_shape",
            "season_applied", "missing_items", "recommendation", "message", "explanation",
        ):
            self.assertIn(key, response.data)

    def test_one_piece_can_complete_a_recommendation(self):
        self.top.delete()
        self.bottom.delete()
        dress = WardrobeItem.objects.create(
            profile=self.profile, name="Everyday dress", category=WardrobeItem.Category.DRESS
        )
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.data["recommendation"]["selected_one_piece"]["id"], dress.id)
