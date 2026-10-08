import re

from django.db import transaction
from rest_framework import serializers

from .models import Profile


class StrictInputModelSerializer(serializers.ModelSerializer):
    """Reject fields that this API does not expose instead of silently ignoring them."""

    def to_internal_value(self, data):
        if isinstance(data, dict):
            errors = {}
            for name in data:
                field = self.fields.get(name)
                if field is None:
                    errors[name] = ["Unknown field."]
                elif field.read_only:
                    errors[name] = ["This field is read-only."]
            if errors:
                raise serializers.ValidationError(errors)
        return super().to_internal_value(data)


class ProfileSerializer(StrictInputModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", max_length=150, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", max_length=150, required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source="user.email", required=False, allow_blank=True
    )

    class Meta:
        model = Profile
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "display_name", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "username", "created_at", "updated_at"]

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip()

    def validate_display_name(self, value):
        return value.strip()

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        if user_data:
            instance.user.save()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if validated_data:
            instance.save()
        return instance


class SettingsSerializer(StrictInputModelSerializer):
    class Meta:
        model = Profile
        fields = ["currency_code"]

    def validate_currency_code(self, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", value):
            raise serializers.ValidationError("Enter a three-letter currency code.")
        return value
