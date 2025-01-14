from rest_framework import serializers
from .models import Technology, Developer, Project, Allocation

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
        
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be greater than start date."
            })

        return data
    
class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = ['id', 'project', 'developer', 'hours']

def validate(self, attrs):
        project = attrs.get('project')
        developer = attrs.get('developer')
        hours = attrs.get('hours')

        # validate technologies
        if project and developer:
            project_technologies = set(project.technologies.all())
            developer_technologies = set(developer.technologies.all())

            if not developer_technologies.intersection(project_technologies):
                raise serializers.ValidationError(
                    f"The developer '{developer.name}' does not have the required technologies for the project '{project.name}'."
                )
            
        # Validate hours
        if project and hours:
            current_allocations = project.allocations.all()
            total_hours_allocated = sum(allocation.hours for allocation in current_allocations)
            total_hours_with_new_allocation = total_hours_allocated + hours

            if total_hours_with_new_allocation > project.planned_hours:
                raise serializers.ValidationError(
                    f"Allocating {hours} hours exceeds the planned hours for the project '{project.name}'. "
                    f"Currently allocated: {total_hours_allocated} hours, planned: {project.planned_hours} hours."
                )
            
        # Validate Period
        if project:
            today = date.today()
            if not (project.start_date <= today <= project.end_date):
                raise serializers.ValidationError(
                    f"The current date ({today}) is outside the project's start and end dates "
                    f"({project.start_date} to {project.end_date})."
                ) 

        return attrs