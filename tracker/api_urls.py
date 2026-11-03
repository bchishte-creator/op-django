from rest_framework.routers import DefaultRouter

from .api import CategoryViewSet, FoodEventViewSet, FoodViewSet, TeamMemberViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('people', TeamMemberViewSet, basename='team-member')
router.register('foods', FoodViewSet, basename='food')
router.register('events', FoodEventViewSet, basename='food-event')

urlpatterns = router.urls
