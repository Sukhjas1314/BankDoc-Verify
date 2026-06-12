from django.urls import path

from . import views


urlpatterns = [
    path("csrf/", views.csrf, name="csrf"),
    path("upload/", views.upload_file, name="upload-file"),
    path("extract/", views.extract_file, name="extract-file"),
    path("validate/", views.validate_file, name="validate-file"),
    path("history/", views.history, name="history"),
    path("report/<int:run_id>/", views.download_report, name="download-report"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
