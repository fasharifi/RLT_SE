from rest_framework.routers import DefaultRouter
from .views import StudySessionViewSet

router = DefaultRouter()
router.register(r'study-sessions', StudySessionViewSet, basename='study-sessions')

urlpatterns = router.urls
