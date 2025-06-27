from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SucculentViewSet, PotViewSet

router = DefaultRouter()
router.register(r'succulents', SucculentViewSet)
router.register(r'pots', PotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
