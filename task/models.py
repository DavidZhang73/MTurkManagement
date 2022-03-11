import urllib.parse
import uuid

from django.db import models


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
        return len(self.annotation['config']['actionLabelData']) - 1  # remove default

    class Meta:
        abstract = True


class Batch(models.Model):
    description = models.TextField(blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)

    mturk_batch_id = models.CharField(max_length=32, null=True, editable=False)

    def __str__(self):
        return f'Batch {self.pk}'


class Task(AnnotationModel):
    batch = models.ForeignKey(to=Batch, on_delete=models.CASCADE, null=True)

    mturk_hit_id = models.CharField(max_length=128, null=True, editable=False)
    mturk_hit_status = models.CharField(max_length=32, null=True, editable=False)
    mturk_hit_title = models.CharField(max_length=128, null=True, editable=False)
    mturk_hit_expiration = models.DateTimeField(null=True, editable=False)

    def url(self):
        VIDAT_URL = Settings.objects.get(name='VIDAT_URL').value
        VIDAT_SUMIT_URL = Settings.objects.get(name='VIDAT_SUMIT_URL').value
        VIDAT_DEFAULT_FPS = Settings.objects.get(name='VIDAT_DEFAULT_FPS').value
        VIDAT_DEFAULT_FPK = Settings.objects.get(name='VIDAT_DEFAULT_FPK').value
        return f'{VIDAT_URL}' \
               f'?annotation={urllib.parse.quote(self.annotation_pathname)}' \
               f'&showObjects=false&showRegions=false&showSkeletons=false&showActions=true' \
               f'&showPopup=false&grayscale=false&decoder=auto&muted=false&zoom=false' \
               f'&defaultFps={VIDAT_DEFAULT_FPS}&defaultFpk={VIDAT_DEFAULT_FPK}' \
               f'&submitURL={urllib.parse.quote(VIDAT_SUMIT_URL + "/" + str(self.id) + "/")}'

    def __str__(self):
        return f'Task {self.pk}'


class Assignment(AnnotationModel):
    class STATUS(models.TextChoices):
        CREATED = ('CREATE', 'Created')
        SUBMITTED = ('SUBMIT', 'Submitted')
        APPROVED = ('APPROVE', 'Approved')
        REJECTED = ('REJECT', 'Rejected')
        UNKNOWN = ('UNKNOWN', 'Unknown')

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=7, choices=STATUS.choices, default=STATUS.UNKNOWN)
    final_annotation = models.JSONField()
    final_annotation_pathname = models.CharField(max_length=1024, blank=True, null=True)
    last_modified_datetime = models.DateTimeField(auto_now=True)

    mturk_assignment_id = models.CharField(max_length=128, null=True, editable=False)
    mturk_assignment_status = models.CharField(max_length=32, null=True, editable=False)
    mturk_worker_id = models.CharField(max_length=128, null=True, editable=False)
    mturk_worker_feedback = models.TextField(null=True, editable=False)
    mturk_worker_accept_time = models.DateTimeField(null=True, editable=False)
    mturk_worker_submit_time = models.DateTimeField(null=True, editable=False)

    def url(self, annotation_pathname):
        VIDAT_URL = Settings.objects.get(name='VIDAT_URL').value
        VIDAT_AUDIT_URL = Settings.objects.get(name='VIDAT_AUDIT_URL').value
        VIDAT_DEFAULT_FPS = Settings.objects.get(name='VIDAT_DEFAULT_FPS').value
        VIDAT_DEFAULT_FPK = Settings.objects.get(name='VIDAT_DEFAULT_FPK').value
        return f'{VIDAT_URL}?annotation={urllib.parse.quote(annotation_pathname)}' \
               f'&showObjects=false&showRegions=false&showSkeletons=false&showActions=true' \
               f'&showPopup=false&grayscale=false&decoder=auto&muted=false&zoom=false' \
               f'&defaultFps={VIDAT_DEFAULT_FPS}&defaultFpk={VIDAT_DEFAULT_FPK}' \
               f'&submitURL={urllib.parse.quote(VIDAT_AUDIT_URL + "/" + str(self.uuid) + "/")}'

    def __str__(self):
        return f'Assignment {self.uuid}'


class Settings(models.Model):
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
