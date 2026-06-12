from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import UploadedFile, ValidationIssue, ValidationRun
from .serializers import UploadedFileSerializer, ValidationRunSerializer
from .services.anomaly_detector import AnomalyDetector
from .services.pdf_parser import extract_preview, extract_tables
from .services.report_generator import generate_validation_report
from .services.validator import BankingValidator

MAX_UPLOAD_SIZE = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".xlsx"}


def _validate_upload(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return "Only PDF and XLSX files are accepted."
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        return "File exceeds the 25 MB upload limit."
    return None


@api_view(["GET"])
@ensure_csrf_cookie
def csrf(request):
    return Response({"detail": "CSRF cookie set."})


@api_view(["POST"])
@parser_classes([MultiPartParser])
@csrf_protect
def upload_file(request):
    uploaded = request.FILES.get("file")
    if not uploaded:
        return Response({"detail": "A file field named 'file' is required."}, status=status.HTTP_400_BAD_REQUEST)
    error = _validate_upload(uploaded)
    if error:
        return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)
    record = UploadedFile.objects.create(file_name=Path(uploaded.name).name, file_path=uploaded)
    return Response(UploadedFileSerializer(record).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@csrf_protect
def extract_file(request):
    uploaded = get_object_or_404(UploadedFile, pk=request.data.get("uploaded_file_id"))
    try:
        preview = extract_preview(uploaded.file_path.path)
    except Exception as exc:
        uploaded.status = UploadedFile.Status.FAILED
        uploaded.save(update_fields=["status"])
        return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    uploaded.status = UploadedFile.Status.EXTRACTED
    uploaded.save(update_fields=["status"])
    return Response({"uploaded_file": UploadedFileSerializer(uploaded).data, "extraction": preview})


@api_view(["POST"])
@csrf_protect
def validate_file(request):
    uploaded = get_object_or_404(UploadedFile, pk=request.data.get("uploaded_file_id"))
    try:
        frames = extract_tables(uploaded.file_path.path)
        validator = BankingValidator()
        findings, total_checks = validator.validate(frames)
        findings.extend(AnomalyDetector().detect(frames))
    except Exception as exc:
        uploaded.status = UploadedFile.Status.FAILED
        uploaded.save(update_fields=["status"])
        return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    failed_checks = len(findings)
    total_checks = max(total_checks, failed_checks)
    passed_checks = total_checks - failed_checks
    run_status = ValidationRun.Status.FAILED if failed_checks else ValidationRun.Status.PASSED
    run = ValidationRun.objects.create(
        uploaded_file=uploaded,
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        status=run_status,
    )
    issue_records = [
        ValidationIssue(
            validation_run=run,
            issue_type=finding.issue_type,
            severity=finding.severity,
            description=finding.description,
            expected_value=finding.expected_value,
            actual_value=finding.actual_value,
            row_number=finding.row_number,
        )
        for finding in findings
    ]
    ValidationIssue.objects.bulk_create(issue_records)
    report_path = settings.MEDIA_ROOT / "reports" / f"validation-run-{run.id}.pdf"
    generate_validation_report(run, issue_records, report_path)
    with report_path.open("rb") as handle:
        run.report_file.save(report_path.name, File(handle), save=True)
    uploaded.status = UploadedFile.Status.VALIDATED
    uploaded.save(update_fields=["status"])
    return Response(ValidationRunSerializer(run).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def history(request):
    runs = ValidationRun.objects.select_related("uploaded_file").prefetch_related("issues").order_by("-created_at")
    return Response(ValidationRunSerializer(runs, many=True).data)


@api_view(["GET"])
def dashboard(request):
    total_files = UploadedFile.objects.count()
    total_validations = ValidationRun.objects.count()
    failed_validations = ValidationRun.objects.filter(status=ValidationRun.Status.FAILED).count()
    passed_validations = ValidationRun.objects.filter(status=ValidationRun.Status.PASSED).count()
    return Response(
        {
            "total_files_processed": total_files,
            "total_validations": total_validations,
            "failed_validations": failed_validations,
            "passed_validations": passed_validations,
        }
    )


@api_view(["GET"])
def download_report(request, run_id):
    run = get_object_or_404(ValidationRun, pk=run_id)
    if not run.report_file:
        return Response({"detail": "Report is not available."}, status=status.HTTP_404_NOT_FOUND)
    return FileResponse(run.report_file.open("rb"), as_attachment=True, filename=Path(run.report_file.name).name)
