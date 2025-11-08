from django.contrib import admin

from .models import Allocation, Developer, Project, Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    search_fields = ['name']
    filter_horizontal = ['technologies']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'planned_hours']
    readonly_fields = ['planned_hours']
    filter_horizontal = ['technologies']


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ['developer', 'project', 'hours']
    list_filter = ['project']
