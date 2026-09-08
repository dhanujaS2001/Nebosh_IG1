from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path("add_record/", views.add_record, name="add_record"),
    path("update_record/<int:record_id>/", views.update_record, name="update_record"),
    path("delete_record/<int:record_id>/", views.delete_record, name="delete_record"),
    path("inline-update/<int:record_id>/", views.inline_update, name="inline_update"),
]