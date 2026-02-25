from rest_framework.routers import DefaultRouter
from .views import ReadingGoalViewSet

router = DefaultRouter()
router.register(r'goals', ReadingGoalViewSet, basename='goals')

urlpatterns = router.urls
