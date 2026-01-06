from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, GoalBookViewSet

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goals')
router.register(r'goal-books', GoalBookViewSet, basename='goal-books')

urlpatterns = router.urls
