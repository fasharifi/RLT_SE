from rest_framework.routers import DefaultRouter
from .views import ReadingSessionViewSet

router = DefaultRouter()
router.register(r'sessions', ReadingSessionViewSet, basename='sessions')
urlpatterns = router.urls
