from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from verifier.models import UploadedFile


class UploadApiTests(TestCase):
    def test_rejects_invalid_file_type(self):
        response = self.client.post(reverse("upload-file"), {"file": SimpleUploadedFile("bad.txt", b"nope")})

        self.assertEqual(response.status_code, 400)

    def test_accepts_xlsx_upload(self):
        response = self.client.post(
            reverse("upload-file"),
            {"file": SimpleUploadedFile("report.xlsx", b"placeholder", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UploadedFile.objects.filter(file_name=Path("report.xlsx").name).exists())
