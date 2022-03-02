import json
import os
import random
import re
import uuid

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from item.models import Item
from task.models import Task, Settings, Submission, Audit

reg = re.compile(r"(\d+)")


def get_random_color():
    return f'#{str(hex(000000 + int(random.random() * 16777216)))[-6:]}'


def save_task(item_category, item_subCategory, item_id, video_url, DATASET_PATH):
    config = {
        "objectLabelData": [
            {
                "id": 0,
                "name": "default",
                "color": "#00ff00"
            }
        ],
        "actionLabelData": [
            {
                "id": 0,
                "name": "default",
                "color": "#0000FF",
                "thumbnail": '',
                "objects": [
                    0
                ]
            },
        ],
        "skeletonTypeData": []
    }
    item_path = os.path.join(DATASET_PATH, item_category, item_subCategory, item_id)
    step_path = os.path.join(item_path, 'step')
    annotation_path = os.path.join(item_path, 'annotation')
    os.makedirs(annotation_path, exist_ok=True)
    action_annotation_list = []
    for index, step_file in enumerate(sorted(os.listdir(step_path), key=lambda name: int(reg.findall(name)[0]))):
        random_color = get_random_color()
        config["actionLabelData"].append({
            "id": index + 1,
            "name": f"Step {index + 1}",
            "color": random_color,
            "thumbnail": "/" + "/".join(
                [DATASET_PATH, item_category, item_subCategory, item_id, 'step', step_file]),
            "objects": [
                0
            ]
        })
        action_annotation_list.append({
            "start": 0,
            "end": 0,
            "action": index + 1,
            "object": 0,
            "color": random_color,
            "description": ""
        })
    video_id = video_url.replace("https://www.youtube.com/watch?v=", "")
    video_name = f'{video_id}.mp4'
    Task(
        annotation={
            "version": Settings.objects.get(name='VIDAT_VERSION').value,
            "annotation": {
                "video": {
                    "src": "/" + "/".join(
                        [DATASET_PATH, item_category, item_subCategory, item_id, 'video', video_name])
                },
                "keyframeList": [],
                "objectAnnotationListMap": {},
                "regionAnnotationListMap": {},
                "skeletonAnnotationListMap": {},
                "actionAnnotationList": action_annotation_list
            },
            "config": config
        },
        annotation_pathname="/" + "/".join(
            [DATASET_PATH, item_category, item_subCategory, item_id, 'annotation', f'task-{item_id}-{video_id}.json'])
    ).save()


@csrf_exempt
def load_task_from_mongodb(request):
    DATASET_PATH = Settings.objects.get(name='DATASET_PATH').value
    count = 0
    for item in Item.objects.filter(progressStatus__in=[[True, True, True]]):
        for video in item.videoList:
            save_task(item.category, item.subCategory, item.id, video.url, DATASET_PATH)
            count += 1
    return HttpResponse(f'{count} tasks added!')


@csrf_exempt
def load_task_from_json(request):
    DATASET_PATH = Settings.objects.get(name='DATASET_PATH').value
    DATASET_JSON_NAME = Settings.objects.get(name='DATASET_JSON_NAME').value
    count = 0
    with open(os.path.join(DATASET_PATH, DATASET_JSON_NAME), 'r', encoding='utf8') as f:
        dataset = json.load(f)
    for item in dataset:
        for video in item['videoList']:
            save_task(item['category'], item['subCategory'], item['id'], video['url'], DATASET_PATH)
            count += 1
    return HttpResponse(f'{count} tasks added!')


@csrf_exempt
def submit(request, task_id):
    task = Task.objects.get(id=task_id)
    _id = uuid.uuid4()
    annotation = json.loads(request.body)
    annotation_path = '/'.join([task.annotation_pathname.split('/annotation')[0], 'annotation'])
    submission = Submission(
        uuid=_id,
        task=task,
        annotation=annotation,
        annotation_pathname='/'.join([annotation_path, f'submission-{_id}.json'])
    )
    submission.save()
    if Audit.objects.count():
        _audit_id = Audit.objects.latest('id').id + 1
    else:
        _audit_id = 1
    _audit = Audit(
        id=_audit_id,
        submission=submission,
        annotation=annotation
    )
    _audit.annotation_pathname = '/'.join([annotation_path, f'audit-{_audit_id}.json'])
    _audit.save()
    return JsonResponse({
        "message": "Thanks for your work! Please copy and paste the uuid back to MTurk.",
        "clipboard": _id
    })


@csrf_exempt
def audit(request, submission_uuid):
    submission = Submission.objects.get(uuid=submission_uuid)
    _audit = submission.audit
    _audit.annotation = json.loads(request.body)
    _audit.result = 'UNSET'
    _audit.save()
    return JsonResponse({
        "message": "Thanks for your work!",
        "clipboard": _audit.id
    })
