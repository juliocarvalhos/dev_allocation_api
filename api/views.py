from rest_framework import viewsets

from .models import Allocation, Developer, Project, Technology
from .serializers import (
    AllocationSerializer,
    DeveloperSerializer,
    ProjectSerializer,
    TechnologySerializer,
)


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.order_by('name')
    serializer_class = TechnologySerializer


class DeveloperViewSet(viewsets.ModelViewSet):
    queryset = Developer.objects.prefetch_related('technologies').order_by('id')
    serializer_class = DeveloperSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related('technologies').order_by('id')
    serializer_class = ProjectSerializer


class AllocationViewSet(viewsets.ModelViewSet):
    queryset = Allocation.objects.select_related('project', 'developer').order_by('id')
    serializer_class = AllocationSerializer
