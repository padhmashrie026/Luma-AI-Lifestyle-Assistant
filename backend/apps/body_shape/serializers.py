import math

from rest_framework import serializers

from .models import BodyMeasurement


class MeasurementNumberField(serializers.FloatField):
    """Accept JSON numbers only, then ensure values are finite and positive."""

    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, (int, float)):
            raise serializers.ValidationError("Enter a numeric measurement.")
        value = super().to_internal_value(data)
        if not math.isfinite(value):
            raise serializers.ValidationError("Enter a finite measurement.")
        if value <= 0:
            raise serializers.ValidationError("Measurement must be greater than zero.")
        return value


class BodyShapeCalculationSerializer(serializers.Serializer):
    shoulder = MeasurementNumberField()
    bust = MeasurementNumberField()
    waist = MeasurementNumberField()
    hip = MeasurementNumberField()


class BodyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMeasurement
        fields = [
            "id", "measured_on", "height_cm", "shoulder_cm", "bust_cm",
            "waist_cm", "hip_cm", "styling_shape", "approximate_size_notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_internal_value(self, data):
        unknown = set(data) - set(self.fields) if isinstance(data, dict) else set()
        if unknown:
            raise serializers.ValidationError({
                field: ["Unknown field."] for field in sorted(unknown)
            })
        return super().to_internal_value(data)
