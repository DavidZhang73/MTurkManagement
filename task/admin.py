from django.contrib import admin
from django.db import models
from django_monaco_editor.widgets import AdminMonacoEditorWidget
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.formats.base_formats import CSV

from .models import Batch, Task, Submission, Settings, Audit


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'task_count',
        'audit_pass_fail_unset_count',
        'submission_count',
        'progress',
        'description',
        'created_datetime'
    )
    search_fields = ('id', 'description')

    def has_add_permission(self, request):
        return False


class TaskResources(resources.ModelResource):
    url = Field()

    def dehydrate_url(self, task):
        return task.url()

    class Meta:
        model = Task
        fields = ('id', 'url')


@admin.register(Task)
class TaskAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'vidat',
        'audit_pass_fail_unset_count',
        'submission_count',
        'progress',
        'step_list_count',
        'batch',
        'annotation_pathname'
    )
    search_fields = ('id', 'batch', 'annotation_pathname')
    list_filter = ('batch',)
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }
    resource_class = TaskResources

    formats = [CSV]

    def has_add_permission(self, request):
        return False


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

    def has_add_permission(self, request):
        return False


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
    list_filter = ('submission__uuid', 'result')
    search_fields = ('id', 'submission__uuid')
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }
    actions = ['mark_pass', 'mark_fail', 'mark_unset']

    def has_add_permission(self, request):
        return False

    @admin.action(description='Mark as PASS')
    def mark_pass(self, request, queryset):
        queryset.update(result='PASS')

    @admin.action(description='Mark as FAIL')
    def mark_fail(self, request, queryset):
        queryset.update(result='FAIL')

    @admin.action(description='Mark as UNSET')
    def mark_unset(self, request, queryset):
        queryset.update(result='UNSET')


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'description')
    search_fields = ('id', 'name', 'value', 'description')
