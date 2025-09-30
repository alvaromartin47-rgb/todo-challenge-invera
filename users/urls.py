from django.urls import path, include
from rest_framework import routers
from .views import MeViewSet, UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)

urlpatterns = [
    path('me/', MeViewSet.as_view({'get': 'get'}), name='me'),
    path('', include(router.urls)),
]