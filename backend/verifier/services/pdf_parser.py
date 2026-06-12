from io import StringIO
from pathlib import Path
import csv

import pandas as pd


def normalize_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.dropna(how="all").dropna(axis=1, how="all")
    frame = frame.rename(columns=lambda value: str(value).strip().lower().replace(" ", "_"))
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return frame.reset_index(drop=True)


def _find_best_delimiter(sample: str) -> str:
    candidates = [",", "\t", ";", "|"]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(candidates))
        if dialect.delimiter in candidates:
            return dialect.delimiter
    except csv.Error:
        pass

    lines = [line for line in sample.splitlines() if line.strip()]
    best = ","
    best_score = None
    for delim in candidates:
        counts = []
        for line in lines[:20]:
            try:
                counts.append(len(list(csv.reader([line], delimiter=delim))[0]))
            except Exception:
                counts.append(0)
        if not counts:
            continue
        score = (max(counts) - min(counts), len(set(counts)))
        if best_score is None or score < best_score:
            best_score = score
            best = delim
    return best


def extract_text_table(file_path: str | Path) -> list[pd.DataFrame]:
    path = Path(file_path)
    raw_text = path.read_text(encoding="utf-8", errors="replace")
    delimiter = _find_best_delimiter("\n".join(raw_text.splitlines()[:20]))
    try:
        frame = pd.read_csv(StringIO(raw_text), delimiter=delimiter, engine="python", dtype=str, on_bad_lines="skip")
    except pd.errors.ParserError:
        frame = pd.read_csv(StringIO(raw_text), delimiter=delimiter, engine="python", dtype=str, quoting=csv.QUOTE_NONE, on_bad_lines="skip")
    if frame.empty:
        return []
    return [normalize_dataframe(frame)]


def extract_tables(file_path: str | Path) -> list[pd.DataFrame]:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        sheets = pd.read_excel(path, sheet_name=None)
        return [normalize_dataframe(sheet) for sheet in sheets.values() if not sheet.empty]
    if suffix in {".txt", ".csv"}:
        return extract_text_table(path)
    if suffix != ".pdf":
        raise ValueError("Only PDF, XLSX, TXT, and CSV files can be extracted.")

    import pdfplumber

    frames: list[pd.DataFrame] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue
                header, rows = table[0], table[1:]
                frame = pd.DataFrame(rows, columns=header)
                normalized = normalize_dataframe(frame)
                if not normalized.empty:
                    frames.append(normalized)
    return frames


def extract_preview(file_path: str | Path) -> dict:
    frames = extract_tables(file_path)
    return {
        "table_count": len(frames),
        "row_count": sum(len(frame) for frame in frames),
        "columns": sorted({column for frame in frames for column in frame.columns}),
        "tables": [frame.head(10).fillna("").to_dict(orient="records") for frame in frames],
    }
