from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register('users', MyUserViewSet)

urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
