from django.urls import path

from .views import BodyShapeCalculationView


urlpatterns = [
    path("body-shape/calculate/", BodyShapeCalculationView.as_view(), name="body-shape-calculate"),
]
