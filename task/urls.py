from django.urls import path

from .views import load_task_from_mongodb, load_task_from_json, submit, audit

urlpatterns = [
    path('load_task_from_mongodb/', load_task_from_mongodb),
    path('load_task_from_json/', load_task_from_json),
    path('submit/<int:task_id>/', submit),
    path('audit/<uuid:submission_uuid>/', audit),
]
