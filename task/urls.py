from django.urls import path

from .views import new_batch_from_json, submit, audit

urlpatterns = [
    path('new_batch_from_json/', new_batch_from_json),
    path('submit/<int:task_id>/', submit),
    path('audit/<uuid:submission_uuid>/', audit),
]
