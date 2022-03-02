from django.contrib import admin
from django.db import models
from django_monaco_editor.widgets import AdminMonacoEditorWidget
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from .models import Task, Submission, Settings, Audit


class TaskResources(resources.ModelResource):
    url = Field()

    def dehydrate_url(self, task):
        return task.url()

    class Meta:
        model = Task
        fields = ('id', 'url')


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = (
        'id',
        'vidat',
        'audit_result',
        'step_list_count',
        'annotation_pathname'
    )
    search_fields = ('id',)
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }
    resource_class = TaskResources


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vidat',
        'uuid',
        'task',
        'audit_result',
        'step_list_count',
        'action_annotation_list_count',
        'created_datetime'
    )
    list_filter = ('task__id', 'audit__result')
    search_fields = ('id', 'uuid')
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vidat',
        'result',
        'submission',
        'step_list_count',
        'action_annotation_list_count',
        'created_datetime'
    )
    list_filter = ('submission__uuid',)
    search_fields = ('id',)
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'description')
    search_fields = ('id', 'name', 'value', 'description')
