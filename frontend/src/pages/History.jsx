import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import ReportDownloadButton from "../components/ReportDownloadButton.jsx";
import { getHistory } from "../services/api.js";

export default function History() {
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory()
      .then((response) => setRuns(response.data))
      .catch(() => setError("Validation history is unavailable."));
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-bank-line pb-5">
        <h1 className="text-3xl font-semibold text-slate-950">History</h1>
        <p className="mt-2 text-sm text-slate-600">Completed validation runs and report downloads.</p>
      </div>
      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{error}</div>}
      <div className="overflow-hidden rounded-lg border border-bank-line bg-white">
        <table className="min-w-full divide-y divide-bank-line text-sm">
          <thead className="bg-slate-100 text-left text-xs font-semibold uppercase text-slate-600">
            <tr>
              <th className="px-4 py-3">File name</th>
              <th className="px-4 py-3">Upload date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Checks</th>
              <th className="px-4 py-3">Report</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-bank-line">
            {runs.map((run) => (
              <tr key={run.id}>
                <td className="px-4 py-3 font-medium text-slate-950">
                  <Link className="text-bank-blue hover:underline" to={`/results/${run.id}`} state={run}>
                    {run.file_name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-slate-600">{new Date(run.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 capitalize">{run.status}</td>
                <td className="px-4 py-3 text-slate-600">{run.passed_checks}/{run.total_checks}</td>
                <td className="px-4 py-3">
                  <ReportDownloadButton runId={run.id} />
                </td>
              </tr>
            ))}
            {!runs.length && (
              <tr>
                <td className="px-4 py-6 text-slate-600" colSpan="5">
                  No validation runs have been completed.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
