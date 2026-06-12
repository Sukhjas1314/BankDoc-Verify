from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from verifier.models import UploadedFile


class UploadApiTests(TestCase):
    def test_rejects_invalid_file_type(self):
        response = self.client.post(reverse("upload-file"), {"file": SimpleUploadedFile("bad.exe", b"nope")})

        self.assertEqual(response.status_code, 400)

    def test_accepts_xlsx_upload(self):
        response = self.client.post(
            reverse("upload-file"),
            {"file": SimpleUploadedFile("report.xlsx", b"placeholder", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UploadedFile.objects.filter(file_name=Path("report.xlsx").name).exists())

    def test_accepts_txt_upload(self):
        response = self.client.post(
            reverse("upload-file"),
            {"file": SimpleUploadedFile("report.txt", b"transaction_id,account_number,date,amount\n1,A1,2026-01-01,100", content_type="text/plain")},
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(UploadedFile.objects.filter(file_name=Path("report.txt").name).exists())

    def test_text_upload_detects_pipe_delimiter(self):
        content = b"transaction_id|account_number|date|amount\n1|A1|2026-01-01|100\n2|A2|2026-01-02|200"
        response = self.client.post(
            reverse("upload-file"),
            {"file": SimpleUploadedFile("report.txt", content, content_type="text/plain")},
        )

        self.assertEqual(response.status_code, 201)
        uploaded = UploadedFile.objects.get(file_name=Path("report.txt").name)
        from verifier.services.pdf_parser import extract_tables

        frames = extract_tables(uploaded.file_path.path)
        self.assertEqual(len(frames), 1)
        self.assertIn("transaction_id", frames[0].columns)
        self.assertEqual(frames[0].shape, (2, 4))

    def test_validation_summary_rows_include_all_columns(self):
        content = b"cust_id|account|date|amount|description\nC1|A1|2026-01-01|100|deposit\nC1|A2|2026-01-02|200|withdrawal\nC2|A3|2026-01-03|300|transfer"
        upload_response = self.client.post(
            reverse("upload-file"),
            {"file": SimpleUploadedFile("report.txt", content, content_type="text/plain")},
        )
        self.assertEqual(upload_response.status_code, 201)
        uploaded_id = upload_response.json()["id"]

        validate_response = self.client.post(
            reverse("validate-file"),
            {"uploaded_file_id": uploaded_id, "selected_columns": ["cust_id"]},
        )
        self.assertEqual(validate_response.status_code, 201)
        summary = validate_response.json().get("summary", {})

        self.assertIsInstance(summary.get("groups"), list)
        self.assertGreater(len(summary["groups"]), 0)
        first_group = summary["groups"][0]
        self.assertIn("rows", first_group)
        self.assertEqual(first_group["rows"][0]["account"], "A1")
        self.assertEqual(first_group["rows"][1]["description"], "withdrawal")
