from django.urls import include, path
from rest_framework import routers

from .views import AllocationViewSet, DeveloperViewSet, ProjectViewSet, TechnologyViewSet

router = routers.DefaultRouter()
router.register(r'technologies', TechnologyViewSet, basename='technology')
router.register(r'developers', DeveloperViewSet, basename='developer')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'allocations', AllocationViewSet, basename='allocation')

urlpatterns = [
    path('', include(router.urls)),
]
