from django.contrib import admin

from .models import UploadedFile, ValidationIssue, ValidationRun


admin.site.register(UploadedFile)
admin.site.register(ValidationRun)
admin.site.register(ValidationIssue)
