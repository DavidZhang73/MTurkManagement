import json
import os
import random
import re
import uuid

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from task.models import Task, Settings, Batch, Assignment

reg = re.compile(r"(\d+)")


def get_random_color():
    return f'#{random.randint(0, 0xFFFFFF):06x}'


def save_task(item_category, item_subCategory, item_id, video, DATASET_PATH, batch_id):
    item_path = os.path.join(DATASET_PATH, item_category, item_subCategory, item_id)
    step_path = os.path.join(item_path, 'step')
    manual_path = os.path.join(item_path, 'manual')
    video_url = video['url']
    # config
    annotation_path = os.path.join(item_path, 'annotation')
    os.makedirs(annotation_path, exist_ok=True)
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
                "thumbnail": "/" + "/".join(
                    [DATASET_PATH, item_category, item_subCategory, item_id,
                     [img for img in os.listdir(item_path) if
                      os.path.isfile(os.path.join(item_path, img)) and img.endswith('.jpg')][0]]),
                "objects": [
                    0
                ]
            },
        ],
        "skeletonTypeData": []
    }
    # step
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
    # video
    video_id = video_url.replace("https://www.youtube.com/watch?v=", "")
    video_name = f'{video_id}.mp4'
    # manual
    manual_list = [os.path.join(manual_path, manual) for manual in os.listdir(manual_path) if
                   os.path.isfile(os.path.join(manual_path, manual)) and manual.endswith('.pdf')]

    if Task.objects.count():
        task_id = Task.objects.latest('id').id + 1
    else:
        task_id = 1
    Task(
        id=task_id,
        batch_id=batch_id,
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
            [DATASET_PATH, item_category, item_subCategory, item_id, 'annotation',
             f'task-{task_id}-{item_id}-{video_id}.json']),
        manual_list=manual_list,
        video_title=video.get('title', 'N/A'),
        video_duration=video.get('duration', 'N/A'),
    ).save()


def _new_batch_from_json(description=None):
    DATASET_PATH = Settings.objects.get(name='DATASET_PATH').value
    DATASET_JSON_NAME = Settings.objects.get(name='DATASET_JSON_NAME').value
    batch = Batch()
    batch.description = description
    batch.save()
    count = 0
    with open(os.path.join(DATASET_PATH, DATASET_JSON_NAME), 'r', encoding='utf8') as f:
        dataset = json.load(f)
    for item in dataset:
        for video in item['videoList']:
            save_task(item['category'], item['subCategory'], item['id'], video, DATASET_PATH, batch.pk)
            count += 1
    return count


@csrf_exempt
def new_batch_from_json(request):
    count = _new_batch_from_json()
    return HttpResponse(f'{count} tasks added!')


def is_same(obj1, obj2):
    return json.dumps(obj1, sort_keys=True) == json.dumps(obj2, sort_keys=True)


@csrf_exempt
def submit(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        _uuid = uuid.uuid4()
        task_annotation = task.annotation
        annotation = json.loads(request.body)
        # sanity check
        ## check annotation
        if is_same(task_annotation["annotation"]["actionAnnotationList"],
                   annotation["annotation"]["actionAnnotationList"]):
            return JsonResponse({
                "type": 'negative',
                "message": "There is no annotation detected!"
            })
        ## check video
        if task_annotation["annotation"]["video"]["src"] != annotation["annotation"]["video"]["src"]:
            return JsonResponse({
                "type": 'negative',
                "message": "The video should not be changed!"
            })
        ## check config
        if not is_same(task_annotation["config"], annotation["config"]):
            return JsonResponse({
                "type": 'negative',
                "message": "The config should not be changed!"
            })
        ## check action list length
        for action in annotation["annotation"]["actionAnnotationList"]:
            if action["start"] >= action["end"]:
                return JsonResponse({
                    "type": 'negative',
                    "message": "The duration of an action should be greater than 0! "
                               "Please delete all actions that did not appear in the video!"
                })
        annotation_path = '/'.join([task.annotation_pathname.split('/annotation')[0], 'annotation'])
        assignment = Assignment(
            uuid=_uuid,
            task=task,
            status=Assignment.STATUS.CREATED,
            annotation=annotation,
            annotation_pathname='/'.join([annotation_path, f'submission-{_uuid}.json']),
            final_annotation=annotation,
            final_annotation_pathname='/'.join([annotation_path, f'final-{_uuid}.json'])
        )
        assignment.save()
        checksum = str(sum(int(item[0], 16) for item in str(_uuid).split('-')) % 10)
        return JsonResponse({
            "message": "Thanks for your work! Please copy and paste the uuid back to MTurk.",
            "clipboard": str(_uuid) + checksum
        })
    except Exception as e:
        return JsonResponse({
            "message": str(e)
        })


@csrf_exempt
def audit(request, submission_uuid):
    assignment = Assignment.objects.get(uuid=submission_uuid)
    assignment.final_annotation = json.loads(request.body)
    assignment.save()
    return JsonResponse({
        "message": "Thanks for your work!",
        "clipboard": assignment.uuid
    })
