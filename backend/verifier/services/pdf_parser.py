from pathlib import Path

import pandas as pd


def normalize_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.dropna(how="all").dropna(axis=1, how="all")
    frame = frame.rename(columns=lambda value: str(value).strip().lower().replace(" ", "_"))
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return frame.reset_index(drop=True)


def extract_tables(file_path: str | Path) -> list[pd.DataFrame]:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        sheets = pd.read_excel(path, sheet_name=None)
        return [normalize_dataframe(sheet) for sheet in sheets.values() if not sheet.empty]
    if suffix != ".pdf":
        raise ValueError("Only PDF and XLSX files can be extracted.")

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
