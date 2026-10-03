import math

from rest_framework import serializers


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
