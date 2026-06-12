import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from .validator import ValidationFinding


class AnomalyDetector:
    def detect(self, frames: list[pd.DataFrame]) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for frame in frames:
            numeric = self._amount_series(frame)
            if numeric is None or numeric.dropna().shape[0] < 4:
                continue
            findings.extend(self._z_score(numeric))
            findings.extend(self._iqr(numeric))
            findings.extend(self._isolation_forest(numeric))
        return self._dedupe(findings)

    def _amount_series(self, frame: pd.DataFrame) -> pd.Series | None:
        for column in ("amount", "balance", "closing_balance"):
            if column in frame:
                return pd.to_numeric(frame[column].astype(str).str.replace(",", "", regex=False), errors="coerce")
        return None

    def _severity(self, value: float, median: float) -> str:
        ratio = abs(value) / max(abs(median), 1)
        if ratio >= 5:
            return "high"
        if ratio >= 2:
            return "medium"
        return "low"

    def _z_score(self, values: pd.Series) -> list[ValidationFinding]:
        clean = values.dropna()
        std = float(clean.std())
        if std == 0:
            return []
        mean = float(clean.mean())
        median = float(clean.median())
        findings = []
        for index, value in values.items():
            if pd.isna(value):
                continue
            z_score = abs((float(value) - mean) / std)
            if z_score > 3:
                findings.append(
                    ValidationFinding(
                        "anomaly_z_score",
                        self._severity(float(value), median),
                        "Transaction amount is outside the expected z-score range.",
                        expected_value="z-score <= 3.00",
                        actual_value=f"{z_score:.2f}",
                        row_number=index + 2,
                    )
                )
        return findings

    def _iqr(self, values: pd.Series) -> list[ValidationFinding]:
        clean = values.dropna()
        q1 = float(clean.quantile(0.25))
        q3 = float(clean.quantile(0.75))
        iqr = q3 - q1
        if iqr == 0:
            return []
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        median = float(clean.median())
        return [
            ValidationFinding(
                "anomaly_iqr",
                self._severity(float(value), median),
                "Transaction amount is outside the interquartile range.",
                expected_value=f"{lower:.2f} to {upper:.2f}",
                actual_value=f"{float(value):.2f}",
                row_number=index + 2,
            )
            for index, value in values.items()
            if pd.notna(value) and (float(value) < lower or float(value) > upper)
        ]

    def _isolation_forest(self, values: pd.Series) -> list[ValidationFinding]:
        clean = values.dropna()
        if clean.shape[0] < 10:
            return []
        model = IsolationForest(contamination=0.1, random_state=42)
        predictions = model.fit_predict(clean.to_numpy().reshape(-1, 1))
        median = float(clean.median())
        indexes = clean.index.to_list()
        findings = []
        for position, prediction in enumerate(predictions):
            if prediction == -1:
                value = float(clean.iloc[position])
                findings.append(
                    ValidationFinding(
                        "anomaly_isolation_forest",
                        self._severity(value, median),
                        "Isolation Forest marked this transaction as anomalous.",
                        expected_value="normal transaction cluster",
                        actual_value=f"{value:.2f}",
                        row_number=int(indexes[position]) + 2,
                    )
                )
        return findings

    def _dedupe(self, findings: list[ValidationFinding]) -> list[ValidationFinding]:
        seen = set()
        unique = []
        for finding in findings:
            key = (finding.issue_type, finding.row_number, finding.actual_value)
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        return unique
