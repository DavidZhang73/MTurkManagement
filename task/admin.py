import json
import re

import boto3
import requests
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.utils.html import format_html
from django_monaco_editor.widgets import AdminMonacoEditorWidget
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.formats.base_formats import CSV
from simpleui.admin import AjaxAdmin

from .models import Batch, Task, Settings, Assignment
from .views import _new_batch_from_json

external_reg = re.compile(r'<ExternalURL>(.+?)</ExternalURL>')
html_content_reg = re.compile(r'<HTMLContent>([\s\S]+?)</HTMLContent>')
task_id_reg = re.compile(r'<td>Task ID:</td>\s+?<td>(\d+)</td>')
answer_submission_code_reg = re.compile(r'submissionCode</QuestionIdentifier><FreeText>(.+?)</FreeText>')
answer_people_count_reg = re.compile(r'peopleCount</QuestionIdentifier><FreeText>(.+?)</FreeText>')
answer_person_view_reg = re.compile(r'personView</QuestionIdentifier><FreeText>(.+?)</FreeText>')
answer_is_fixed_reg = re.compile(r'isFixed</QuestionIdentifier><FreeText>(.+?)</FreeText>')
answer_is_indoor_reg = re.compile(r'isIndoor</QuestionIdentifier><FreeText>(.+?)</FreeText>')
answer_feedback_reg = re.compile(r'feedback</QuestionIdentifier><FreeText>(.+?)</FreeText>')


def get_boto3_client():
    return boto3.client(
        service_name='mturk',
        region_name=Settings.objects.get(name='MTURK_REGION_NAME').value,
        endpoint_url=Settings.objects.get(name='MTURK_ENDPOINT').value,
        aws_access_key_id=Settings.objects.get(name='AWS_ACCESS_KEY_ID').value,
        aws_secret_access_key=Settings.objects.get(name='AWS_SECRET_ACCESS_KEY').value
    )


@admin.register(Batch)
class BatchAdmin(AjaxAdmin):
    list_display = (
        'id',
        'review',
        'task_count',
        'submit_approve_reject_count',
        'submission_count',
        'description',
        'created_datetime'
    )
    search_fields = ('id', 'description')
    actions = ('new_batch_from_json', 'new_batch_from_mongodb')

    def has_add_permission(self, request):
        return False

    @admin.display(description='review')
    def review(self, instance):

        if instance.mturk_batch_id:
            return format_html(
                '<a href="{}/{}/results" target="_blank">{}</a>',
                Settings.objects.get(name='MTURK_BATCH_REVIEW').value,
                instance.mturk_batch_id,
                instance.mturk_batch_id,
            )
        else:
            return '-'

    @admin.display(description='#Task')
    def task_count(self, instance):
        return instance.task_set.count()

    @admin.display(description='#Submission')
    def submission_count(self, instance):
        count = 0
        for task in instance.task_set.all():
            for assignment in task.assignment_set.all():
                if assignment.status == Assignment.STATUS.APPROVED or assignment.status == Assignment.STATUS.REJECTED or assignment.status == Assignment.STATUS.SUBMITTED:
                    count += 1
        return count

    @admin.display(description='#Submitted/#Approved/#Rejected')
    def submit_approve_reject_count(self, instance):
        approve_count = 0
        reject_count = 0
        submit_count = 0
        for task in instance.task_set.all():
            for assignment in task.assignment_set.all():
                if assignment.status == Assignment.STATUS.APPROVED:
                    approve_count += 1
                elif assignment.status == Assignment.STATUS.REJECTED:
                    reject_count += 1
                elif assignment.status == Assignment.STATUS.SUBMITTED:
                    submit_count += 1
        return f'{submit_count} / {approve_count} / {reject_count}'

    @admin.action(description="New Batch From JSON")
    def new_batch_from_json(self, request, queryset):
        description = request.POST.get('description')
        count = _new_batch_from_json(description)
        return JsonResponse(data={
            'status': 'success',
            'msg': f'{count} tasks added!'
        })

    layer_desc = {
        'title': 'Please provide a short description for the new batch',
        'confirm_button': 'Confirm',
        'cancel_button': 'Cancel',
        'params': [
            {
                'type': 'textarea',
                'key': 'description',
                'label': 'DESC',
                'value': 'new batch',
                'require': True
            }
        ]
    }
    new_batch_from_json.layer = layer_desc
    new_batch_from_json.type = 'primary'


class TaskResources(resources.ModelResource):
    url = Field()
    video = Field()
    step_count = Field()

    def dehydrate_url(self, task):
        return task.url()

    def dehydrate_video(self, task):
        return task.video_url()

    def dehydrate_video_title(self, task):
        return re.sub(r'[^A-Za-z0-9\s]+', '', task.video_title).strip()

    def dehydrate_manual_list(self, task):
        return task.manual_url_list()

    def dehydrate_step_count(self, task):
        return task.step_list_count()

    class Meta:
        model = Task
        fields = ('id', 'url', 'video', 'video_title', 'video_duration', 'manual_list', 'step_count')
        export_order = ('id', 'url', 'video', 'video_title', 'video_duration', 'manual_list', 'step_count')


@admin.register(Task)
class TaskAdmin(ExportMixin, AjaxAdmin):
    list_display = (
        'id',
        'vidat',
        'audit_pass_fail_unset_count',
        'submission_count',
        'step_count',
        'video_title',
        'video_duration',
        'batch',
        'mturk_hit_id',
        'mturk_hit_status',
        'mturk_hit_expiration',
        'mturk_hit_number_of_assignment_pending',
        'mturk_hit_number_of_assignment_available',
        'mturk_hit_number_of_assignment_completed'
    )
    search_fields = ('id', 'mturk_hit_id', 'annotation_pathname')
    list_filter = ('batch', 'mturk_hit_status')
    actions = ('sync',)
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }
    resource_class = TaskResources

    formats = (CSV,)

    def has_add_permission(self, request):
        return False

    @admin.display(description='#Submission')
    def submission_count(self, instance):
        count = 0
        for assignment in instance.assignment_set.all():
            if assignment.status == Assignment.STATUS.APPROVED or assignment.status == Assignment.STATUS.REJECTED or assignment.status == Assignment.STATUS.SUBMITTED:
                count += 1
        return count

    @admin.display(description='#Step')
    def step_count(self, instance):
        return instance.step_list_count()

    @admin.display(description='View in Vidat')
    def vidat(self, instance):
        return format_html(
            '<a href="{}" target="_blank">View</a>',
            instance.url(),
        )

    @admin.display(description='#Submitted/#Approved/#Rejected')
    def audit_pass_fail_unset_count(self, instance):
        approve_count = 0
        reject_count = 0
        submit_count = 0
        for assignment in instance.assignment_set.all():
            if assignment.status == Assignment.STATUS.APPROVED:
                approve_count += 1
            elif assignment.status == Assignment.STATUS.REJECTED:
                reject_count += 1
            elif assignment.status == Assignment.STATUS.SUBMITTED:
                submit_count += 1
        return f'{submit_count} / {approve_count} / {reject_count}'

    @staticmethod
    def sync_with_mturk(client):
        paginator = client.get_paginator('list_hits')
        count = 0
        for page in paginator.paginate():
            for hit in page.get('HITs', []):
                question = hit['Question']
                external_result = external_reg.findall(question)
                if external_result:
                    html = requests.get(external_result[0]).text
                else:
                    html = html_content_reg.findall(question)[0]
                if not html:
                    break
                task_id_result = task_id_reg.findall(html)
                if not task_id_result:
                    break
                task_id = task_id_result[0]
                try:
                    task = Task.objects.get(id=task_id)
                    task.mturk_hit_id = hit.get('HITId')
                    task.mturk_hit_status = hit.get('HITStatus')
                    task.mturk_hit_title = hit.get('Title')
                    task.mturk_hit_expiration = hit.get('Expiration')
                    task.mturk_hit_number_of_assignment_pending = hit.get('NumberOfAssignmentsPending')
                    task.mturk_hit_number_of_assignment_available = hit.get('NumberOfAssignmentsAvailable')
                    task.mturk_hit_number_of_assignment_completed = hit.get('NumberOfAssignmentsCompleted')
                    requester_annotation = hit.get('RequesterAnnotation')
                    batch = task.batch
                    batch.mturk_batch_id = requester_annotation.split(';')[0].split(':')[1]
                    batch.save()
                    task.save()
                except Task.DoesNotExist:
                    break
                count += 1
        return count

    @admin.display(description='Sync With MTurk')
    def sync(self, request, queryset):
        try:
            count = self.sync_with_mturk(get_boto3_client())
            return JsonResponse(data={
                'status': 'success',
                'msg': f'{count} tasks are synchronized.'
            })
        except Exception as e:
            return JsonResponse(data={
                'status': 'error',
                'msg': str(e)
            })

    sync.icon = 'fas fa-sync'
    sync.type = 'primary'
    sync.layer = {
        'title': 'Are you sure to sync with MTurk',
        'confirm_button': 'Sync',
        'cancel_button': 'Cancel',
    }


@admin.register(Assignment)
class AssignmentAdmin(AjaxAdmin):
    list_display = (
        'short_uuid',
        'audit_in_vidat',
        'view_final_in_vidat',
        'batch',
        'status',
        'step_count',
        'annotated_step_count',
        'work_time',
        'mturk_worker_id',
        'mturk_worker_feedback',
        'description',
        'people_count',
        'person_view',
        'is_fixed',
        'is_indoor',
        'mturk_assignment_status',
        'mturk_worker_accept_time',
        'mturk_worker_submit_time',
        'mturk_assignment_id',
        'created_datetime',
        'last_modified_datetime',
    )
    list_filter = ('task__batch', 'status')
    search_fields = ('id', 'uuid', 'description', 'mturk_worker_id', 'mturk_assignment_id')
    formfield_overrides = {
        models.JSONField: {'widget': AdminMonacoEditorWidget}
    }
    actions = (
        'sync', 'approve', 'reject',
        'export_approved_worker_list', 'export_rejected_worker_list',
        'export_approved_annotation_list', 'export_final_annotation_list'
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Short UUID')
    def short_uuid(self, instance):
        return str(instance.uuid).split('-')[-1]

    @admin.display(description='Audit')
    def audit_in_vidat(self, instance):
        return format_html(
            '<a href="{}" target="_blank">Audit</a>',
            instance.url(instance.annotation_pathname),
        )

    @admin.display(description='Final')
    def view_final_in_vidat(self, instance):
        return format_html(
            '<a href="{}" target="_blank">Final</a>',
            instance.url(instance.final_annotation_pathname),
        )

    @admin.display(description='Batch')
    def batch(self, instance):
        return instance.task.batch

    @admin.display(description='#Step')
    def step_count(self, instance):
        return instance.step_list_count()

    @admin.display(description='#Annotated Step')
    def annotated_step_count(self, instance):
        return instance.action_annotation_list_count()

    @admin.display(description='work time')
    def work_time(self, instance):
        if instance.mturk_worker_accept_time and instance.mturk_worker_submit_time:
            return instance.mturk_worker_submit_time - instance.mturk_worker_accept_time
        else:
            return '0'

    def sync_with_mturk(self, client):
        count = 0
        for hit_id in Task.objects.all().values_list('mturk_hit_id', flat=True).distinct():
            paginator = client.get_paginator('list_assignments_for_hit')
            for page in paginator.paginate(HITId=hit_id):
                for assignment2 in page.get('Assignments', []):
                    answer = assignment2.get('Answer')
                    submission_code_result = answer_submission_code_reg.findall(answer)
                    if not submission_code_result:
                        break
                    submission_code = submission_code_result[0]
                    try:
                        if submission_code[-1] != str(
                                sum(int(item[0], 16) for item in submission_code[0:-1].split('-')) % 10):
                            raise ValidationError(f'{submission_code} checksum failed.')
                        assignment = Assignment.objects.get(uuid=submission_code[0:-1], task__mturk_hit_id=hit_id)
                        assignment.mturk_assignment_id = assignment2.get('AssignmentId')
                        assignment.mturk_assignment_status = assignment2.get('AssignmentStatus')
                        assignment.mturk_worker_id = assignment2.get('WorkerId')
                        assignment.mturk_worker_accept_time = assignment2.get('AcceptTime')
                        assignment.mturk_worker_submit_time = assignment2.get('SubmitTime')

                        people_count_result = answer_people_count_reg.findall(answer)
                        if people_count_result:
                            assignment.people_count = people_count_result[0]

                        person_view_result = answer_person_view_reg.findall(answer)
                        if person_view_result:
                            assignment.person_view = person_view_result[0]

                        is_fixed_result = answer_is_fixed_reg.findall(answer)
                        if is_fixed_result:
                            assignment.is_fixed = is_fixed_result[0]

                        is_indoor_result = answer_is_indoor_reg.findall(answer)
                        if is_indoor_result:
                            assignment.is_indoor = is_indoor_result[0]

                        feedback_result = answer_feedback_reg.findall(answer)
                        if feedback_result:
                            assignment.mturk_worker_feedback = feedback_result[0]

                        if assignment2.get('AssignmentStatus') == 'Submitted':
                            assignment.status = Assignment.STATUS.SUBMITTED
                        elif assignment2.get('AssignmentStatus') == 'Rejected':
                            assignment.status = Assignment.STATUS.REJECTED
                        elif assignment2.get('AssignmentStatus') == 'Approved':
                            assignment.status = Assignment.STATUS.APPROVED
                        assignment.save()
                        count += 1
                    except (Assignment.DoesNotExist, ValidationError):
                        try:
                            client.reject_assignment(
                                AssignmentId=assignment2.get('AssignmentId'),
                                RequesterFeedback=f"Submission code {submission_code}\
                                 could not be found in our database, \
                                 if you believe this is an error, \
                                 please contact us <jiahao.zhang@anu.edu.au>."
                            )
                        except:
                            continue
                        raise Exception(
                            f'Assignment {submission_code} could not be found! So we reject it automatically!'
                        )
        return count

    @admin.display(description='Sync With MTurk')
    def sync(self, request, queryset):
        try:
            client = get_boto3_client()
            count = self.sync_with_mturk(client)
            return JsonResponse(data={
                'status': 'success',
                'msg': f'{count} assignments are synchronized.'
            })
        except Exception as e:
            return JsonResponse(data={
                'status': 'error',
                'msg': str(e)
            })

    sync.icon = 'fas fa-sync'
    sync.type = 'primary'
    sync.layer = {
        'title': 'Are you sure to sync with MTurk',
        'confirm_button': 'Sync',
        'cancel_button': 'Cancel',
    }

    @admin.action(description='Approve')
    def approve(self, request, queryset):
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.APPROVED:
                messages.add_message(request, messages.WARNING,
                                     f'Assignment {assignment.uuid} has already been approved!')
                return
            if assignment.status == Assignment.STATUS.REJECTED:
                messages.add_message(request, messages.WARNING,
                                     f'Could not approve the rejected Assignment {assignment.uuid}!')
                return
            if assignment.status == Assignment.STATUS.CREATED:
                messages.add_message(request, messages.WARNING, 'Please sync with MTurk first!')
                return
            if assignment.status == Assignment.STATUS.UNKNOWN:
                messages.add_message(request, messages.ERROR,
                                     f'The status of  Assignment {assignment.uuid} should not be UNKNOWN!')
                return
            try:
                client = get_boto3_client()
                client.approve_assignment(
                    AssignmentId=assignment.mturk_assignment_id,
                    RequesterFeedback='Thanks for your great work!'
                )
                assignment.status = Assignment.STATUS.APPROVED
                assignment.mturk_assignment_status = 'Approved'
                assignment.save()
                messages.add_message(request, messages.SUCCESS,
                                     f'Assignment {assignment.uuid} has been approved!')
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))

    approve.icon = 'fas fa-check-circle'
    approve.type = 'primary'
    approve.confirm = 'Are you sure to approve this submission, this action is invertible!'

    @admin.action(description='Reject')
    def reject(self, request, queryset):
        reason = request.POST.get('reason')
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.APPROVED:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': f'Could not reject approved Assignment {assignment.uuid}!'
                })
            if assignment.status == Assignment.STATUS.REJECTED:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': f'Assignment {assignment.uuid} has already been rejected!'
                })
            if assignment.status == Assignment.STATUS.CREATED:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': 'Please sync with MTurk first!'
                })
            if assignment.status == Assignment.STATUS.UNKNOWN:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': f'The status of  Assignment {assignment.uuid} should not be UNKNOWN!'
                })
            try:
                client = get_boto3_client()
                client.reject_assignment(
                    AssignmentId=assignment.mturk_assignment_id,
                    RequesterFeedback=reason
                )
                assignment.status = Assignment.STATUS.REJECTED
                assignment.mturk_assignment_status = 'Rejected'
                if assignment.description:
                    assignment.description += "\nRejection reason: " + reason
                else:
                    assignment.description = "Rejection reason: " + reason
                assignment.save()
                messages.add_message(request, messages.SUCCESS,
                                     f'Assignment {assignment.uuid} has been rejected!')
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))

        return JsonResponse(data={
            'status': 'success',
            'msg': f"{queryset.count()} Assignment(s) have been rejected'"
        })

    reject.icon = 'fas fa-times-circle'
    reject.type = 'danger'
    reject.layer = {
        'title': 'Please provide a rejection reason',
        'confirm_button': 'Confirm Rejection',
        'cancel_button': 'Cancel',
        'params': [
            {
                'type': 'textarea',
                'key': 'reason',
                'label': 'Reason',
                'require': True,
                'value': 'The submission does not meet our criteria. Because'
            }
        ]
    }

    @admin.action(description='Export Approved Workers')
    def export_approved_worker_list(self, request, queryset):
        response = HttpResponse(content_type='text/txt')
        response['Content-Disposition'] = 'attachment; filename="approved_worker_list.txt"'
        worker_id_set = set()
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.APPROVED and assignment.mturk_worker_id:
                worker_id_set.add(assignment.mturk_worker_id)
        response.write('\n'.join(worker_id_set))
        return response

    export_approved_worker_list.icon = 'fas fa-file-export'

    @admin.action(description='Export Rejected Workers')
    def export_rejected_worker_list(self, request, queryset):
        response = HttpResponse(content_type='text/txt')
        response['Content-Disposition'] = 'attachment; filename="rejected_worker_list.txt"'
        worker_id_set = set()
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.REJECTED and assignment.mturk_worker_id:
                worker_id_set.add(assignment.mturk_worker_id)
        response.write('\n'.join(worker_id_set))
        return response

    export_rejected_worker_list.icon = 'fas fa-file-export'

    @admin.action(description='Export Approved Annotations')
    def export_approved_annotation_list(self, request, queryset):
        response = HttpResponse(content_type='text/json')
        response['Content-Disposition'] = 'attachment; filename="approved_annotations.json"'
        annotation_map = {}
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.APPROVED:
                video_src = assignment.annotation['annotation']['video']['src']
                video_name = video_src.split('/')[-1]
                video_id = video_name.split('.')[0]
                item = dict(
                    batch=assignment.task.batch.id,
                    video_src=video_src,
                    annotation=assignment.final_annotation['annotation']['actionAnnotationList'],
                    action_label_list=assignment.final_annotation['config']['actionLabelData'],
                    people_count=assignment.people_count,
                    person_view=assignment.person_view,
                    is_fixed=assignment.is_fixed,
                    is_indoor=assignment.is_indoor,
                    description=assignment.description
                )
                if video_id in annotation_map:
                    annotation_map[video_id].append(item)
                else:
                    annotation_map[video_id] = [item]
        json.dump(annotation_map, response)
        return response

    export_approved_annotation_list.icon = 'fas fa-file-export'

    @admin.action(description='Export Final Annotations')
    def export_final_annotation_list(self, request, queryset):
        response = HttpResponse(content_type='text/json')
        response['Content-Disposition'] = 'attachment; filename="final_annotations.json"'
        annotation_map = {}
        for assignment in queryset:
            if assignment.status == Assignment.STATUS.APPROVED and assignment.final_annotation:
                video_src = assignment.final_annotation['annotation']['video']['src']
                video_name = video_src.split('/')[-1]
                video_id = video_name.split('.')[0]
                item = dict(
                    batch=assignment.task.batch.id,
                    video_src=video_src,
                    annotation=assignment.final_annotation['annotation']['actionAnnotationList'],
                    action_label_list=assignment.final_annotation['config']['actionLabelData'],
                    people_count=assignment.people_count,
                    person_view=assignment.person_view,
                    is_fixed=assignment.is_fixed,
                    is_indoor=assignment.is_indoor,
                    description=assignment.description
                )
                if video_id in annotation_map:
                    annotation_map[video_id].append(item)
                else:
                    annotation_map[video_id] = [item]
        json.dump(annotation_map, response)
        return response

    export_final_annotation_list.icon = 'fas fa-file-export'


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'description')
    search_fields = ('id', 'name', 'value', 'description')
