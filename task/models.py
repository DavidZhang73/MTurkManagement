import urllib.parse
import uuid

from django.contrib import admin
from django.db import models
from django.utils.html import format_html


class AnnotationModel(models.Model):
    annotation = models.JSONField()
    annotation_pathname = models.CharField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)

    def video_pathname(self):
        return self.annotation['annotation']['video']['src']

    def video_fps(self):
        return self.annotation['annotation']['video']['fps']

    def video_duration(self):
        return self.annotation['annotation']['video']['duration']

    def video_frames(self):
        return self.annotation['annotation']['video']['frames']

    def video_width(self):
        return self.annotation['annotation']['video']['width']

    def video_height(self):
        return self.annotation['annotation']['video']['height']

    def action_annotation_list(self):
        return self.annotation['annotation']['actionAnnotationList']

    def action_annotation_list_count(self):
        return len(self.annotation['annotation']['actionAnnotationList'])

    def step_list(self):
        return self.annotation['config']['actionLabelData']

    def step_list_count(self):
        return len(self.annotation['config']['actionLabelData'])

    class Meta:
        abstract = True


class Task(AnnotationModel):
    def url(self):
        VIDAT_URL = Settings.objects.get(name='VIDAT_URL').value
        VIDAT_SUMIT_URL = Settings.objects.get(name='VIDAT_SUMIT_URL').value
        VIDAT_DEFAULT_FPS = Settings.objects.get(name='VIDAT_DEFAULT_FPS').value
        VIDAT_DEFAULT_FPK = Settings.objects.get(name='VIDAT_DEFAULT_FPK').value
        return f'{VIDAT_URL}' \
               f'?annotation={self.annotation_pathname}' \
               f'&showObjects=false&showRegions=false&showSkeletons=false&showActions=true' \
               f'&showPopup=false&grayscale=false&decoder=auto&muted=false&zoom=false' \
               f'&defaultFps={VIDAT_DEFAULT_FPS}&defaultFpk={VIDAT_DEFAULT_FPK}' \
               f'&submitURL={urllib.parse.quote_plus(VIDAT_SUMIT_URL + "/" + str(self.id) + "/")}'

    @admin.display
    def vidat(self):
        return format_html(
            '<a href="{}" target="_blank">Open in Vidat</a>',
            self.url(),
        )

    @admin.display
    def audit_result(self):
        submission_set = self.submission_set.all()
        submission_count = len(submission_set)
        if submission_count:
            audit_pass_count = 0
            for submission in submission_set:
                if submission.audit.result == 'PASS':
                    audit_pass_count += 1
            return f'{audit_pass_count} / {submission_count}'
        else:
            return '0 / 0'

    def __str__(self):
        return f'Task {self.pk}'


class Submission(AnnotationModel):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE)

    def url(self):
        VIDAT_URL = Settings.objects.get(name='VIDAT_URL').value
        VIDAT_AUDIT_URL = Settings.objects.get(name='VIDAT_AUDIT_URL').value
        VIDAT_DEFAULT_FPS = Settings.objects.get(name='VIDAT_DEFAULT_FPS').value
        VIDAT_DEFAULT_FPK = Settings.objects.get(name='VIDAT_DEFAULT_FPK').value
        return f'{VIDAT_URL}' \
               f'?annotation={self.annotation_pathname}' \
               f'&showObjects=false&showRegions=false&showSkeletons=false&showActions=true' \
               f'&showPopup=false&grayscale=false&decoder=auto&muted=false&zoom=false' \
               f'&defaultFps={VIDAT_DEFAULT_FPS}&defaultFpk={VIDAT_DEFAULT_FPK}' \
               f'&submitURL={urllib.parse.quote_plus(VIDAT_AUDIT_URL + "/" + str(self.uuid) + "/")}'

    @admin.display
    def vidat(self):
        return format_html(
            '<a href="{}" target="_blank">Audit in Vidat</a>',
            self.url(),
        )

    @admin.display
    def audit_result(self):
        return self.audit.result

    def __str__(self):
        return f'Submission {self.uuid}'


class Audit(AnnotationModel):
    AUDIT_RESULT = (
        ('PASS', 'PASS'),
        ('FAIL', 'FAIL'),
        ('UNSET', 'UNSET')
    )
    submission = models.OneToOneField(to=Submission, on_delete=models.CASCADE)
    result = models.CharField(max_length=5, choices=AUDIT_RESULT, default='UNSET')

    def url(self):
        VIDAT_URL = Settings.objects.get(name='VIDAT_URL').value
        VIDAT_AUDIT_URL = Settings.objects.get(name='VIDAT_AUDIT_URL').value
        VIDAT_DEFAULT_FPS = Settings.objects.get(name='VIDAT_DEFAULT_FPS').value
        VIDAT_DEFAULT_FPK = Settings.objects.get(name='VIDAT_DEFAULT_FPK').value
        return f'{VIDAT_URL}?annotation={self.annotation_pathname}' \
               f'&showObjects=false&showRegions=false&showSkeletons=false&showActions=true' \
               f'&showPopup=false&grayscale=false&decoder=auto&muted=false&zoom=false' \
               f'&defaultFps={VIDAT_DEFAULT_FPS}&defaultFpk={VIDAT_DEFAULT_FPK}' \
               f'&submitURL={urllib.parse.quote_plus(VIDAT_AUDIT_URL + "/" + str(self.submission.uuid) + "/")}'

    @admin.display
    def vidat(self):
        return format_html(
            '<a href="{}" target="_blank">Audit in Vidat</a>',
            self.url(),
        )

    def __str__(self):
        return f'Audit {self.pk}'


class Settings(models.Model):
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
