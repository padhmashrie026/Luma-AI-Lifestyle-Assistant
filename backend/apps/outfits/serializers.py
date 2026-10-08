from rest_framework import serializers

from apps.body_shape.models import BodyMeasurement
from .models import Outfit


class BodyShapeChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().lower().replace(" ", "_")
        return super().to_internal_value(data)


BODY_SHAPE_CHOICES = [
    choice for choice in BodyMeasurement.StylingShape.choices
    if choice[0] != BodyMeasurement.StylingShape.NOT_SET
]


class OutfitRecommendationRequestSerializer(serializers.Serializer):
    body_shape = BodyShapeChoiceField(choices=BODY_SHAPE_CHOICES, required=False)
    occasion = serializers.ChoiceField(choices=Outfit.Occasion.choices)

    def validate(self, attrs):
        if "season" in self.initial_data:
            raise serializers.ValidationError({
                "season": "Season cannot be used because wardrobe items do not store season information."
            })
        return attrs
