from rest_framework import routers
from django.urls import path, include
from .views import TechnologyViewSet, DeveloperViewSet, ProjectViewSet, AllocationViewSet

router = routers.DefaultRouter()
router.register(r'technologies', TechnologyViewSet, basename='technology')
router.register(r'developers', DeveloperViewSet, basename='developer')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'allocations', AllocationViewSet, basename='allocation')

urlpatterns = [
    path('', include(router.urls)),
]
