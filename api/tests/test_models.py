from datetime import date

from django.test import TestCase

from api.models import Project


class ProjectPlannedHoursTests(TestCase):
    def test_planned_hours_counts_both_ends_of_the_period(self):
        project = Project.objects.create(
            name='One week', start_date=date(2025, 3, 3), end_date=date(2025, 3, 9)
        )
        self.assertEqual(project.planned_hours, 7 * 8)

    def test_single_day_project_has_one_work_day(self):
        project = Project.objects.create(
            name='One day', start_date=date(2025, 3, 3), end_date=date(2025, 3, 3)
        )
        self.assertEqual(project.planned_hours, 8)

    def test_planned_hours_is_recalculated_when_period_changes(self):
        project = Project.objects.create(
            name='Growing', start_date=date(2025, 3, 3), end_date=date(2025, 3, 4)
        )
        project.end_date = date(2025, 3, 12)
        project.save()
        project.refresh_from_db()
        self.assertEqual(project.planned_hours, 10 * 8)
