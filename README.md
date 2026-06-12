# BankDoc Verify

BankDoc Verify is a local-first banking report validation system. Officers upload PDF or XLSX reports, the backend extracts tabular data, runs reconciliation checks, detects anomalies, and generates a downloadable PDF validation report.

## Stack

- Backend: Python 3.12, Django 5, Django REST Framework, Pandas, NumPy, pdfplumber, openpyxl, scikit-learn, ReportLab
- Frontend: React, Vite, Axios, React Router, Tailwind CSS
- Database: SQLite for development, PostgreSQL through Docker Compose
- Storage: local filesystem under `media/`

## Features

- PDF/XLSX upload with 25 MB size limit and extension validation
- Multi-table PDF extraction and XLSX sheet parsing
- Sum, subtotal, balance, missing value, duplicate, and custom formula validation
- Isolation Forest, z-score, and IQR anomaly detection
- Downloadable PDF validation reports
- Dashboard, upload, validation result, and history pages

## Run With Docker

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`

## Run Locally

Backend:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/upload/`
- `POST /api/extract/`
- `POST /api/validate/`
- `GET /api/history/`
- `GET /api/report/{id}/`
- `GET /api/dashboard/`

## Sample Data

`sample_data/banking_report_sample.csv` contains intentional issues: duplicate transaction ID, missing transaction ID, subtotal mismatch, total mismatch, and a high-value outlier. Convert it to XLSX for upload or use it as a template for generated reports.

## Tests

Backend:

```bash
cd backend
python manage.py test
```

Frontend:

```bash
cd frontend
npm test
```
