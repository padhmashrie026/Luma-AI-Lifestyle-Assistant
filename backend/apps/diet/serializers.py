from rest_framework import serializers

class WeeklyMealPlanRequestSerializer(serializers.Serializer):
    week_start = serializers.DateField()
