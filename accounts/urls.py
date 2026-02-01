from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, LoginViewSets

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('login', LoginViewSets, basename='login')



urlpatterns = router.urls