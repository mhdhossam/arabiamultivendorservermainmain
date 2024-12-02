from django.urls import  path
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include

app_name = "advertisement"

router = DefaultRouter()
router.register(r'hero-sliders', views.HeroSlidersViewSet)

urlpatterns = [
    path('', include(router.urls)),
]