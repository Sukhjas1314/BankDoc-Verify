from django.db import models


class UploadedFile(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        EXTRACTED = "extracted", "Extracted"
        VALIDATED = "validated", "Validated"
        FAILED = "failed", "Failed"

    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to="uploads/")
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)

    def __str__(self):
        return self.file_name


class ValidationRun(models.Model):
    class Status(models.TextChoices):
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        WARNING = "warning", "Warning"

    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name="validation_runs")
    total_checks = models.PositiveIntegerField(default=0)
    passed_checks = models.PositiveIntegerField(default=0)
    failed_checks = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PASSED)
    report_file = models.FileField(upload_to="reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_file.file_name} - {self.status}"


class ValidationIssue(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    validation_run = models.ForeignKey(ValidationRun, on_delete=models.CASCADE, related_name="issues")
    issue_type = models.CharField(max_length=80)
    severity = models.CharField(max_length=20, choices=Severity.choices)
    description = models.TextField()
    expected_value = models.CharField(max_length=255, blank=True)
    actual_value = models.CharField(max_length=255, blank=True)
    row_number = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue_type}: {self.severity}"
