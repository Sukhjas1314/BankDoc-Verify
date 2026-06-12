from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass
class ValidationFinding:
    issue_type: str
    severity: str
    description: str
    expected_value: str = ""
    actual_value: str = ""
    row_number: int | None = None


class BankingValidator:
    def __init__(self):
        self.formulas: dict[str, Callable[[pd.Series], float]] = {}

    def register_formula(self, name: str, formula: Callable[[pd.Series], float]) -> None:
        self.formulas[name] = formula

    def validate(self, frames: list[pd.DataFrame]) -> tuple[list[ValidationFinding], int]:
        findings: list[ValidationFinding] = []
        checks = 0
        for frame in frames:
            checks += 5
            findings.extend(self._missing_values(frame))
            findings.extend(self._duplicate_transactions(frame))
            findings.extend(self._sum_validation(frame))
            findings.extend(self._subtotal_validation(frame))
            findings.extend(self._balance_validation(frame))
            findings.extend(self._formula_validation(frame))
        return findings, checks

    def _numeric_column(self, frame: pd.DataFrame, names: tuple[str, ...]) -> pd.Series | None:
        for name in names:
            if name in frame.columns:
                return pd.to_numeric(frame[name].astype(str).str.replace(",", "", regex=False), errors="coerce")
        return None

    def _missing_values(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        findings = []
        key_columns = [column for column in ("transaction_id", "account_number", "date", "amount") if column in frame]
        for index, row in frame.iterrows():
            missing = [column for column in key_columns if pd.isna(row[column]) or str(row[column]).strip() == ""]
            if missing:
                findings.append(
                    ValidationFinding(
                        "missing_value",
                        "high" if "transaction_id" in missing else "medium",
                        f"Missing required field(s): {', '.join(missing)}.",
                        row_number=index + 2,
                    )
                )
        return findings

    def _duplicate_transactions(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        columns = [column for column in ("transaction_id", "account_number", "date", "amount") if column in frame]
        if not columns:
            return []
        duplicates = frame[frame.duplicated(subset=columns, keep=False)]
        return [
            ValidationFinding(
                "duplicate_transaction",
                "high",
                "Duplicate transaction detected using transaction ID, account, date, and amount.",
                actual_value=str(row[columns].to_dict()),
                row_number=index + 2,
            )
            for index, row in duplicates.iterrows()
        ]

    def _sum_validation(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        amount = self._numeric_column(frame, ("amount", "transaction_amount"))
        reported_total = self._numeric_column(frame, ("reported_total", "total"))
        if amount is None or reported_total is None or reported_total.dropna().empty:
            return []
        expected = float(amount.dropna().sum())
        actual = float(reported_total.dropna().iloc[-1])
        difference = round(expected - actual, 2)
        if abs(difference) <= 0.01:
            return []
        return [
            ValidationFinding(
                "sum_validation",
                "high",
                "Column total does not match reported total.",
                expected_value=f"{expected:.2f}",
                actual_value=f"{actual:.2f} (difference {difference:.2f})",
            )
        ]

    def _subtotal_validation(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        if "group" not in frame or "subtotal" not in frame:
            return []
        amount = self._numeric_column(frame, ("amount", "transaction_amount"))
        if amount is None:
            return []
        working = frame.copy()
        working["_amount"] = amount
        findings = []
        for group, rows in working.groupby("group"):
            reported = pd.to_numeric(rows["subtotal"].astype(str).str.replace(",", "", regex=False), errors="coerce").dropna()
            if reported.empty:
                continue
            expected = float(rows["_amount"].dropna().sum())
            actual = float(reported.iloc[-1])
            if abs(expected - actual) > 0.01:
                findings.append(
                    ValidationFinding(
                        "subtotal_validation",
                        "medium",
                        f"Subtotal mismatch for group {group}.",
                        expected_value=f"{expected:.2f}",
                        actual_value=f"{actual:.2f}",
                    )
                )
        return findings

    def _balance_validation(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        opening = self._numeric_column(frame, ("opening_balance",))
        credits = self._numeric_column(frame, ("credits", "credit"))
        debits = self._numeric_column(frame, ("debits", "debit"))
        closing = self._numeric_column(frame, ("closing_balance",))
        if any(series is None or series.dropna().empty for series in (opening, credits, debits, closing)):
            return []
        expected = float(opening.dropna().iloc[0] + credits.dropna().sum() - debits.dropna().sum())
        actual = float(closing.dropna().iloc[-1])
        if abs(expected - actual) <= 0.01:
            return []
        return [
            ValidationFinding(
                "balance_validation",
                "high",
                "Opening balance plus credits minus debits does not equal closing balance.",
                expected_value=f"{expected:.2f}",
                actual_value=f"{actual:.2f}",
            )
        ]

    def _formula_validation(self, frame: pd.DataFrame) -> list[ValidationFinding]:
        findings = []
        for name, formula in self.formulas.items():
            result_column = f"{name}_result"
            if result_column not in frame:
                continue
            actual = pd.to_numeric(frame[result_column], errors="coerce")
            for index, row in frame.iterrows():
                expected = formula(row)
                if pd.notna(actual.iloc[index]) and abs(float(actual.iloc[index]) - expected) > 0.01:
                    findings.append(
                        ValidationFinding(
                            "formula_validation",
                            "medium",
                            f"Formula mismatch for {name}.",
                            expected_value=f"{expected:.2f}",
                            actual_value=f"{float(actual.iloc[index]):.2f}",
                            row_number=index + 2,
                        )
                    )
        return findings
