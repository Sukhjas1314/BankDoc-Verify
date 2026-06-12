from rest_framework import serializers

from .models import UploadedFile, ValidationIssue, ValidationRun


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["id", "file_name", "file_path", "upload_time", "status"]
        read_only_fields = ["id", "file_name", "upload_time", "status"]


class ValidationIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationIssue
        fields = [
            "id",
            "issue_type",
            "severity",
            "description",
            "expected_value",
            "actual_value",
            "row_number",
            "created_at",
        ]


class ValidationRunSerializer(serializers.ModelSerializer):
    issues = ValidationIssueSerializer(many=True, read_only=True)
    file_name = serializers.CharField(source="uploaded_file.file_name", read_only=True)

    class Meta:
        model = ValidationRun
        fields = [
            "id",
            "uploaded_file",
            "file_name",
            "total_checks",
            "passed_checks",
            "failed_checks",
            "status",
            "report_file",
            "created_at",
            "issues",
        ]
