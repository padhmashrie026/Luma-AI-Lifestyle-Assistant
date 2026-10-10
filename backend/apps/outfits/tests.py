from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import BodyMeasurement, Profile
from apps.wardrobe.models import WardrobeItem
from .models import Outfit, OutfitItem


class OutfitRecommendationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="outfit-test")
        self.profile = Profile.objects.create(user=self.user)
        self.top = WardrobeItem.objects.create(
            profile=self.profile, name="Linen top", category=WardrobeItem.Category.TOP
        )
        self.bottom = WardrobeItem.objects.create(
            profile=self.profile, name="Cotton trousers", category=WardrobeItem.Category.BOTTOM
        )
        self.url = "/api/outfits/recommend/"
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def payload(self, **overrides):
        return {"occasion": "everyday", **overrides}

    def test_anonymous_access_is_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {"occasion": "everyday"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_recommends_stored_available_items(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["recommendation_available"])
        recommendation = response.data["recommendation"]
        self.assertEqual(recommendation["selected_top"]["id"], self.top.id)
        self.assertEqual(recommendation["selected_bottom"]["id"], self.bottom.id)

    def test_returns_varied_combinations_without_duplicates(self):
        second_top = WardrobeItem.objects.create(
            profile=self.profile, name="Silk blouse", category=WardrobeItem.Category.TOP
        )
        second_bottom = WardrobeItem.objects.create(
            profile=self.profile, name="Denim skirt", category=WardrobeItem.Category.BOTTOM
        )
        dress = WardrobeItem.objects.create(
            profile=self.profile, name="Summer dress", category=WardrobeItem.Category.DRESS
        )

        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        suggestions = response.data["recommendations"]
        self.assertGreaterEqual(len(suggestions), 5)
        combination_keys = [tuple(
            suggestion[field]["id"] if suggestion[field] else None
            for field in ("selected_one_piece", "selected_top", "selected_bottom", "selected_outerwear", "selected_accessory")
        ) for suggestion in suggestions]
        self.assertEqual(len(combination_keys), len(set(combination_keys)))
        self.assertTrue(any(
            suggestion["selected_top"] and suggestion["selected_top"]["id"] == second_top.id
            for suggestion in suggestions
        ))
        self.assertTrue(any(
            suggestion["selected_bottom"] and suggestion["selected_bottom"]["id"] == second_bottom.id
            for suggestion in suggestions
        ))
        self.assertTrue(any(suggestion["selected_one_piece"]["id"] == dress.id for suggestion in suggestions))
        saved_ids = set(WardrobeItem.objects.filter(profile=self.profile).values_list("id", flat=True))
        recommended_ids = {
            suggestion[field]["id"]
            for suggestion in suggestions
            for field in ("selected_one_piece", "selected_top", "selected_bottom", "selected_outerwear", "selected_accessory")
            if suggestion[field]
        }
        self.assertTrue(recommended_ids.issubset(saved_ids))

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
        self.assertEqual(response.data["recommendations"], [])
        self.assertIn("Not enough available items", response.data["message"])

    def test_season_is_rejected_because_model_has_no_season_field(self):
        response = self.client.post(self.url, self.payload(season="summer"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("season", response.data)

    def test_invalid_input_is_rejected(self):
        for payload in (
            {},
            self.payload(occasion="casual"),
            self.payload(body_shape="not_set"),
        ):
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, 400)

    def test_response_contains_expected_structure(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        for key in (
            "recommendation_available", "profile_id", "wardrobe_empty", "occasion", "body_shape",
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

    def test_forged_profile_id_is_ignored_and_other_users_data_is_isolated(self):
        other_user = get_user_model().objects.create_user(username="other-outfit-user")
        other_profile = Profile.objects.create(user=other_user)
        other_top = WardrobeItem.objects.create(
            profile=other_profile, name="Other top", category=WardrobeItem.Category.TOP
        )
        WardrobeItem.objects.create(
            profile=other_profile, name="Other bottom", category=WardrobeItem.Category.BOTTOM
        )

        response = self.client.post(
            self.url, self.payload(profile_id=other_profile.id), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile_id"], self.profile.id)
        self.assertEqual(response.data["recommendation"]["selected_top"]["id"], self.top.id)
        self.assertNotEqual(response.data["recommendation"]["selected_top"]["id"], other_top.id)

    def test_empty_wardrobe_is_reported_clearly(self):
        self.top.delete()
        self.bottom.delete()
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["wardrobe_empty"])
        self.assertFalse(response.data["recommendation_available"])
