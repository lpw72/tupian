from django.urls import path, include
from .views import CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
