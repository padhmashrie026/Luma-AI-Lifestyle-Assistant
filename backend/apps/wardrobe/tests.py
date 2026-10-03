from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.body_shape.models import Profile
from .models import WardrobeItem


class WardrobeItemApiTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="wardrobe-test")
        self.profile = Profile.objects.create(user=user)
        self.client = APIClient()
        self.item = WardrobeItem.objects.create(
            profile=self.profile,
            name="Blue shirt",
            category=WardrobeItem.Category.TOP,
            color="Blue",
        )
        self.collection_url = "/api/wardrobe/items/"

    def test_list_items(self):
        response = self.client.get(self.collection_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Blue shirt")

    def test_create_item(self):
        response = self.client.post(
            self.collection_url,
            {
                "profile": self.profile.id,
                "name": "Black trousers",
                "category": "bottom",
                "color": "Black",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Black trousers")
        self.assertEqual(response.data["status"], "available")

    def test_retrieve_item(self):
        response = self.client.get(f"{self.collection_url}{self.item.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.item.id)

    def test_update_item(self):
        response = self.client.patch(
            f"{self.collection_url}{self.item.id}/",
            {"color": "Navy"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["color"], "Navy")

    def test_delete_item(self):
        response = self.client.delete(f"{self.collection_url}{self.item.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WardrobeItem.objects.filter(id=self.item.id).exists())

    def test_invalid_input_is_rejected(self):
        response = self.client.post(
            self.collection_url,
            {
                "profile": self.profile.id,
                "name": "   ",
                "category": "seasonal",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)
        self.assertIn("category", response.data)

    def test_filter_by_category_and_color(self):
        WardrobeItem.objects.create(
            profile=self.profile,
            name="Green shirt",
            category=WardrobeItem.Category.TOP,
            color="Green",
        )
        response = self.client.get(self.collection_url, {"category": "top", "color": "blue"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Blue shirt")
