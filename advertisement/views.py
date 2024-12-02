from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView
)
from .serializers import HeroSlidersSerializer
from .models import HeroSlider
from rest_framework.response import Response
from rest_framework import status,viewsets

# Create your views here.


class HeroSlidersViewSet(viewsets.ModelViewSet):
    serializer_class=HeroSlidersSerializer
    queryset = HeroSlider.objects.all()
    

