import { useState } from "react";
import { useNavigate } from "react-router-dom";

import UploadBox from "../components/UploadBox.jsx";
import { uploadReport, validateReport } from "../services/api.js";

export default function Upload() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(file) {
    setBusy(true);
    setError("");
    try {
      const uploadResponse = await uploadReport(file);
      const validationResponse = await validateReport(uploadResponse.data.id);
      navigate(`/results/${validationResponse.data.id}`, { state: validationResponse.data });
    } catch (exception) {
      setError(exception.response?.data?.detail || exception.message || "The report could not be validated.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <UploadBox onUpload={handleUpload} busy={busy} />
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">{error}</div>}
    </div>
  );
}
