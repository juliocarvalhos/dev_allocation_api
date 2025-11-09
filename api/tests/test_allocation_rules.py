"""Business rules enforced by AllocationSerializer and ProjectSerializer."""

from datetime import timedelta

from django.test import TestCase

from api.serializers import AllocationSerializer, ProjectSerializer

from .factories import (
    make_allocation,
    make_developer,
    make_project,
    make_technology,
    today,
)


class AllocationRulesTestCase(TestCase):
    def setUp(self):
        self.python = make_technology('Python')
        self.react = make_technology('React')
        # 11 days * 8h = 88 planned hours
        self.project = make_project('Backend', technologies=[self.python])
        self.developer = make_developer('Ada', technologies=[self.python])

    def assertNonFieldError(self, serializer, message):
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], message)

    def build(self, hours=20, project=None, developer=None, instance=None, partial=False):
        data = {
            'project': (project or self.project).id,
            'developer': (developer or self.developer).id,
            'hours': hours,
        }
        return AllocationSerializer(instance=instance, data=data, partial=partial)

    def test_valid_allocation(self):
        serializer = self.build()
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TechnologyRuleTests(AllocationRulesTestCase):
    def test_developer_without_any_project_technology_is_rejected(self):
        frontend_dev = make_developer('Grace', technologies=[self.react])
        self.assertNonFieldError(
            self.build(developer=frontend_dev),
            "The developer 'Grace' does not have the required technologies "
            "for the project 'Backend'.",
        )

    def test_developer_with_no_technologies_is_rejected(self):
        self.developer.technologies.clear()
        self.assertFalse(self.build().is_valid())

    def test_one_shared_technology_is_enough(self):
        self.project.technologies.add(self.react)
        fullstack = make_developer('Linus', technologies=[self.react, make_technology('Go')])
        serializer = self.build(developer=fullstack)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class PeriodRuleTests(AllocationRulesTestCase):
    def test_project_not_started_yet_is_rejected(self):
        future = make_project('Future', start_offset=10, end_offset=20, technologies=[self.python])
        self.assertNonFieldError(
            self.build(project=future),
            f"The current date ({today()}) is outside the project's start and end dates "
            f"({future.start_date} to {future.end_date}).",
        )

    def test_finished_project_is_rejected(self):
        past = make_project('Past', start_offset=-20, end_offset=-10, technologies=[self.python])
        self.assertFalse(self.build(project=past).is_valid())

    def test_project_starting_today_is_accepted(self):
        project = make_project(
            'Starts today', start_offset=0, end_offset=3, technologies=[self.python]
        )
        serializer = self.build(project=project)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_project_ending_today_is_accepted(self):
        project = make_project(
            'Ends today', start_offset=-3, end_offset=0, technologies=[self.python]
        )
        serializer = self.build(project=project)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class HoursRuleTests(AllocationRulesTestCase):
    def test_single_allocation_above_planned_hours_is_rejected(self):
        self.assertNonFieldError(
            self.build(hours=120),
            "Allocating 120 hours exceeds the planned hours for the project 'Backend'. "
            'Currently allocated: 0 hours, planned: 88 hours.',
        )

    def test_allocation_exactly_at_the_limit_is_accepted(self):
        serializer = self.build(hours=88)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_sum_of_allocations_from_different_developers_is_enforced(self):
        other = make_developer('Grace', technologies=[self.python])
        make_allocation(self.project, other, 80)
        self.assertNonFieldError(
            self.build(hours=10),
            "Allocating 10 hours exceeds the planned hours for the project 'Backend'. "
            'Currently allocated: 80 hours, planned: 88 hours.',
        )

    def test_hours_from_other_projects_are_not_counted(self):
        other_project = make_project('Other', technologies=[self.python])
        make_allocation(other_project, self.developer, 80)
        serializer = self.build(hours=80)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_updating_an_allocation_does_not_count_its_own_hours_twice(self):
        allocation = make_allocation(self.project, self.developer, 80)
        serializer = self.build(hours=88, instance=allocation)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_partial_update_still_enforces_the_hours_limit(self):
        allocation = make_allocation(self.project, self.developer, 10)
        serializer = AllocationSerializer(instance=allocation, data={'hours': 100}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_partial_update_still_enforces_the_technology_rule(self):
        allocation = make_allocation(self.project, self.developer, 10)
        frontend_dev = make_developer('Grace', technologies=[self.react])
        serializer = AllocationSerializer(
            instance=allocation, data={'developer': frontend_dev.id}, partial=True
        )
        self.assertFalse(serializer.is_valid())

    def test_zero_hours_is_rejected(self):
        serializer = self.build(hours=0)
        self.assertFalse(serializer.is_valid())
        self.assertIn('hours', serializer.errors)


class ProjectRulesTests(AllocationRulesTestCase):
    def test_end_date_before_start_date_is_rejected(self):
        serializer = ProjectSerializer(
            data={
                'name': 'Invalid',
                'start_date': today(),
                'end_date': today() - timedelta(days=1),
                'technologies': [self.python.id],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_partial_update_cannot_move_end_date_before_start_date(self):
        serializer = ProjectSerializer(
            instance=self.project,
            data={'end_date': self.project.start_date - timedelta(days=1)},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())

    def test_project_cannot_shrink_below_allocated_hours(self):
        make_allocation(self.project, self.developer, 80)
        serializer = ProjectSerializer(
            instance=self.project,
            data={'end_date': self.project.start_date + timedelta(days=1)},  # 16h
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_planned_hours_is_read_only(self):
        serializer = ProjectSerializer(
            instance=self.project, data={'planned_hours': 9999}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().planned_hours, 88)
