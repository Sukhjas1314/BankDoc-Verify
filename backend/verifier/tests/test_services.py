import pandas as pd
from django.test import SimpleTestCase

from verifier.services.anomaly_detector import AnomalyDetector
from verifier.services.validator import BankingValidator


class ValidationServiceTests(SimpleTestCase):
    def test_validator_detects_duplicate_and_total_mismatch(self):
        frame = pd.DataFrame(
            [
                {"transaction_id": "T1", "account_number": "A1", "date": "2026-01-01", "amount": 100, "reported_total": 250},
                {"transaction_id": "T1", "account_number": "A1", "date": "2026-01-01", "amount": 100, "reported_total": 250},
            ]
        )

        findings, checks = BankingValidator().validate([frame])

        self.assertEqual(checks, 5)
        self.assertTrue(any(finding.issue_type == "duplicate_transaction" for finding in findings))
        self.assertTrue(any(finding.issue_type == "sum_validation" for finding in findings))

    def test_anomaly_detector_marks_outlier(self):
        frame = pd.DataFrame({"amount": [10, 12, 11, 9, 10, 12, 11, 10, 9, 900]})

        findings = AnomalyDetector().detect([frame])

        self.assertTrue(findings)
        self.assertTrue(any(finding.row_number == 11 for finding in findings))
