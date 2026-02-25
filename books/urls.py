from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CategoryViewSet, ContributionViewSet, ReadingListViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'contributions', ContributionViewSet, basename='contributions')
router.register(r'readings', ReadingListViewSet, basename='readings')

router.register(r'favorites', FavoriteViewSet, basename='favorite')


urlpatterns = router.urls