from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from .models import Allocation, Developer, Project, Technology


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name']


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['id', 'name', 'technologies']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'start_date', 'end_date', 'technologies', 'planned_hours']
        read_only_fields = ['planned_hours']

    def validate(self, attrs):
        # On partial updates, fall back to the stored values so the rule still holds.
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {'end_date': 'End date must be greater than or equal to start date.'}
            )

        # Shrinking a project must not leave more hours allocated than planned.
        if self.instance is not None and start_date and end_date:
            new_planned = ((end_date - start_date).days + 1) * Project.HOURS_PER_DAY
            allocated = self.instance.allocations.aggregate(total=Sum('hours'))['total'] or 0
            if allocated > new_planned:
                raise serializers.ValidationError(
                    {
                        'end_date': (
                            f'The new period gives {new_planned} planned hours, but '
                            f'{allocated} hours are already allocated.'
                        )
                    }
                )

        return attrs


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = ['id', 'project', 'developer', 'hours']

    def validate_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError('Hours must be greater than zero.')
        return value

    def validate(self, attrs):
        # On partial updates (PATCH), fall back to the stored values so every
        # business rule is always checked against the final state.
        project = attrs.get('project', getattr(self.instance, 'project', None))
        developer = attrs.get('developer', getattr(self.instance, 'developer', None))
        hours = attrs.get('hours', getattr(self.instance, 'hours', None))

        self._validate_technologies(project, developer)
        self._validate_period(project)
        self._validate_hours(project, hours)

        return attrs

    def _validate_technologies(self, project, developer):
        """The developer must know at least one technology required by the project."""
        shared = project.technologies.filter(id__in=developer.technologies.values('id'))
        if not shared.exists():
            raise serializers.ValidationError(
                f"The developer '{developer.name}' does not have the required "
                f"technologies for the project '{project.name}'."
            )

    def _validate_period(self, project):
        """Hours can only be distributed while the project is running."""
        today = timezone.localdate()
        if not (project.start_date <= today <= project.end_date):
            raise serializers.ValidationError(
                f"The current date ({today}) is outside the project's start and end dates "
                f"({project.start_date} to {project.end_date})."
            )

    def _validate_hours(self, project, hours):
        """The sum of allocated hours can never exceed the project's planned hours."""
        allocations = project.allocations.all()
        if self.instance is not None:
            # When editing, the allocation being changed must not be counted twice.
            allocations = allocations.exclude(pk=self.instance.pk)

        allocated = allocations.aggregate(total=Sum('hours'))['total'] or 0

        if allocated + hours > project.planned_hours:
            raise serializers.ValidationError(
                f"Allocating {hours} hours exceeds the planned hours for the project "
                f"'{project.name}'. Currently allocated: {allocated} hours, "
                f"planned: {project.planned_hours} hours."
            )
