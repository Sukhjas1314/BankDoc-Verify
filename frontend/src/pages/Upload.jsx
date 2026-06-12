import { useState } from "react";
import { useNavigate } from "react-router-dom";

import UploadBox from "../components/UploadBox.jsx";
import { uploadReport, extractReport, validateReport } from "../services/api.js";

export default function Upload() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [uploadedFileId, setUploadedFileId] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedColumns, setSelectedColumns] = useState([]);

  async function handleUpload(file) {
    setBusy(true);
    setError("");
    setPreview(null);
    setSelectedColumns([]);
    try {
      const uploadResponse = await uploadReport(file);
      setUploadedFileId(uploadResponse.data.id);
      const previewResponse = await extractReport(uploadResponse.data.id);
      setPreview(previewResponse.data.extraction);
    } catch (exception) {
      setError(exception.response?.data?.detail || exception.message || "The report could not be processed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleValidate() {
    if (!uploadedFileId) {
      setError("Upload a file before validating.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const validationResponse = await validateReport(uploadedFileId, selectedColumns);
      navigate(`/results/${validationResponse.data.id}`, { state: validationResponse.data });
    } catch (exception) {
      setError(exception.response?.data?.detail || exception.message || "The report could not be validated.");
    } finally {
      setBusy(false);
    }
  }

  function toggleColumn(column) {
    setSelectedColumns((current) =>
      current.includes(column) ? current.filter((item) => item !== column) : [...current, column]
    );
  }

  return (
    <div className="space-y-5">
      <UploadBox onUpload={handleUpload} busy={busy} />
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">{error}</div>}
      {preview && (
        <section className="rounded-lg border border-bank-line bg-white p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-slate-950">Preview available columns</h2>
              <p className="mt-1 text-sm text-slate-600">Select one or more columns to generate a summary during validation.</p>
            </div>
            <button
              type="button"
              disabled={busy}
              className="rounded-md bg-bank-blue px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              onClick={handleValidate}
            >
              {busy ? "Validating..." : "Validate and summarize"}
            </button>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {preview.columns.map((column) => (
              <label key={column} className="inline-flex items-center gap-2 rounded-lg border border-bank-line bg-slate-50 px-3 py-2 text-sm text-slate-800">
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(column)}
                  onChange={() => toggleColumn(column)}
                  className="h-4 w-4 rounded border-bank-line text-bank-blue"
                />
                {column}
              </label>
            ))}
          </div>

          {preview.tables?.length > 0 && (
            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm text-slate-700">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    {Object.keys(preview.tables[0]).map((header) => (
                      <th key={header} className="px-3 py-2">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {preview.tables[0].slice(0, 5).map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((value, cellIndex) => (
                        <td key={cellIndex} className="px-3 py-2">
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
