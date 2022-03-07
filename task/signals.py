import json
import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Task, Assignment


@receiver(post_save, sender=Task, dispatch_uid="task_post_save_handler")
def task_post_save_handler(instance, **kwargs):
    with open(instance.annotation_pathname[1:], 'w', encoding='utf-8') as f:
        json.dump(instance.annotation, f)


@receiver(post_delete, sender=Task, dispatch_uid="task_post_delete_handler")
def task_post_delete_handler(instance, **kwargs):
    os.remove(instance.annotation_pathname[1:])


@receiver(post_save, sender=Assignment, dispatch_uid="assignment_post_save_handler")
def submission_post_save_handler(instance, **kwargs):
    with open(instance.annotation_pathname[1:], 'w', encoding='utf-8') as f:
        json.dump(instance.annotation, f)
    with open(instance.final_annotation_pathname[1:], 'w', encoding='utf-8') as f:
        json.dump(instance.final_annotation, f)


@receiver(post_delete, sender=Assignment, dispatch_uid="assignment_post_delete_handler")
def submission_post_delete_handler(instance, **kwargs):
    os.remove(instance.annotation_pathname[1:])
    os.remove(instance.final_annotation_pathname[1:])
