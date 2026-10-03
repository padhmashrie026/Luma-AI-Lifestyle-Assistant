from rest_framework.response import Response
from rest_framework.views import APIView

from .calculations import calculate_body_shape
from .serializers import BodyShapeCalculationSerializer


class BodyShapeCalculationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = BodyShapeCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = calculate_body_shape(**serializer.validated_data)
        return Response(result)
