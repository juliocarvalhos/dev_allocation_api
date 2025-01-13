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

        # validate technologies
        if project and developer:
            project_technologies = set(project.technologies.all())
            developer_technologies = set(developer.technologies.all())

            if not developer_technologies.intersection(project_technologies):
                raise serializers.ValidationError(
                    f"The developer '{developer.name}' does not have the required technologies for the project '{project.name}'."
                )