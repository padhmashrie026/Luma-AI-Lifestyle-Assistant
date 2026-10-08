from rest_framework import serializers
from apps.body_shape.models import Profile

from .models import WardrobeItem


class CurrentUserProfileDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return Profile.objects.get(user=serializer_field.context["request"].user)


class WardrobeItemSerializer(serializers.ModelSerializer):
    # Supply the current profile to model uniqueness validation while keeping
    # the field read-only so clients cannot choose the item's owner.
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserProfileDefault()
    )

    class Meta:
        model = WardrobeItem
        fields = [
            "id",
            "profile",
            "name",
            "category",
            "color",
            "brand",
            "size_label",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        # Ownership is assigned by the view from request.user, never from input.
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_category(self, value):
        if value not in WardrobeItem.Category.values:
            raise serializers.ValidationError("Choose a valid wardrobe category.")
        return value

    def validate_status(self, value):
        if value not in WardrobeItem.Status.values:
            raise serializers.ValidationError("Choose a valid wardrobe status.")
        return value

    def validate_color(self, value):
        return value.strip()

    def validate_brand(self, value):
        return value.strip()

    def validate_size_label(self, value):
        return value.strip()
