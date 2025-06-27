from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Succulent, Pot
from .serializers import SucculentSerializer, PotSerializer

class SucculentViewSet(viewsets.ModelViewSet):
    queryset = Succulent.objects.all()
    serializer_class = SucculentSerializer
    permission_classes = [AllowAny]

class PotViewSet(viewsets.ModelViewSet):
    queryset = Pot.objects.all()
    serializer_class = PotSerializer
    permission_classes = [AllowAny]

