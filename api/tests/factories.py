from datetime import timedelta

from django.utils import timezone

from api.models import Allocation, Developer, Project, Technology


def today():
    return timezone.localdate()


def make_technology(name='Python'):
    return Technology.objects.get_or_create(name=name)[0]


def make_developer(name='Ada Lovelace', technologies=()):
    developer = Developer.objects.create(name=name)
    developer.technologies.set(technologies)
    return developer


def make_project(name='Project', start_offset=-5, end_offset=5, technologies=()):
    """Create a project whose period is relative to today (in days)."""
    project = Project.objects.create(
        name=name,
        start_date=today() + timedelta(days=start_offset),
        end_date=today() + timedelta(days=end_offset),
    )
    project.technologies.set(technologies)
    return project


def make_allocation(project, developer, hours):
    return Allocation.objects.create(project=project, developer=developer, hours=hours)
