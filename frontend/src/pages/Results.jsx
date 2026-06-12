import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import ReportDownloadButton from "../components/ReportDownloadButton.jsx";
import ValidationTable from "../components/ValidationTable.jsx";
import { getHistory } from "../services/api.js";

export default function Results() {
  const { runId } = useParams();
  const location = useLocation();
  const [run, setRun] = useState(location.state || null);
  const [activeGroup, setActiveGroup] = useState(null);

  useEffect(() => {
    if (run) return;
    getHistory().then((response) => {
      setRun(response.data.find((item) => String(item.id) === String(runId)));
    });
  }, [run, runId]);

  if (!run) {
    return <div className="rounded-lg border border-bank-line bg-white p-5">Loading validation result.</div>;
  }

  const passed = run.status === "passed";
  const summary = run.summary;
  const groupColumns = summary?.columns || [];
  const activeRows = activeGroup?.rows || [];
  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 border-b border-bank-line pb-5 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-3xl font-semibold text-slate-950">Validation results</h1>
          <p className="mt-2 text-sm text-slate-600">{run.file_name}</p>
        </div>
        <ReportDownloadButton runId={run.id} />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <section className={`rounded-lg border p-4 ${passed ? "border-emerald-200 bg-emerald-50" : "border-rose-200 bg-rose-50"}`}>
          {passed ? <CheckCircle2 className="h-5 w-5 text-emerald-700" /> : <XCircle className="h-5 w-5 text-rose-700" />}
          <p className="mt-2 text-sm font-medium capitalize">{run.status}</p>
          <p className="text-2xl font-semibold">{run.failed_checks} failed checks</p>
        </section>
        <section className="rounded-lg border border-bank-line bg-white p-4">
          <CheckCircle2 className="h-5 w-5 text-emerald-700" />
          <p className="mt-2 text-sm font-medium">Passed checks</p>
          <p className="text-2xl font-semibold">{run.passed_checks}</p>
        </section>
        <section className="rounded-lg border border-bank-line bg-white p-4">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <p className="mt-2 text-sm font-medium">Total checks</p>
          <p className="text-2xl font-semibold">{run.total_checks}</p>
        </section>
      </div>
      {summary?.columns?.length > 0 && (
        <section className="rounded-lg border border-bank-line bg-white p-4">
          <h2 className="text-lg font-semibold text-slate-950">Summary</h2>
          <p className="mt-2 text-sm text-slate-600">Grouped by {groupColumns.join(", ")}.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {Object.entries(summary.distinct_values || {}).map(([column, count]) => (
              <div key={column} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">{column}</p>
                <p className="mt-1 text-2xl font-semibold text-slate-900">{count}</p>
                <p className="text-xs text-slate-500">Distinct values</p>
              </div>
            ))}
          </div>
          {summary.groups?.length > 0 && (
            <div className="mt-5 overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm text-slate-700">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    {groupColumns.map((column) => (
                      <th key={column} className="px-3 py-2">
                        {column}
                      </th>
                    ))}
                    <th className="px-3 py-2">Count</th>
                    <th className="px-3 py-2">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {summary.groups.slice(0, 10).map((row, index) => (
                    <tr key={index} className="hover:bg-slate-50">
                      {groupColumns.map((column) => (
                        <td key={column} className="px-3 py-2">
                          {row.group[column] ?? "—"}
                        </td>
                      ))}
                      <td className="px-3 py-2">{row.count}</td>
                      <td className="px-3 py-2">
                        <button
                          type="button"
                          className="rounded-md bg-bank-blue px-3 py-1 text-xs font-semibold text-white hover:bg-bank-blue/90"
                          onClick={() => setActiveGroup(row)}
                        >
                          View rows
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-3 text-sm text-slate-500">Click a group row to see all corresponding columns for that customer ID.</p>
            </div>
          )}
          {activeGroup && (
            <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-base font-semibold text-slate-950">Data for selected summary group</h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {groupColumns.map((column) => `${column}: ${activeGroup.group[column] ?? "(empty)"}`).join(", ")}
                  </p>
                </div>
                <button
                  type="button"
                  className="rounded-md border border-bank-line bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-100"
                  onClick={() => setActiveGroup(null)}
                >
                  Close
                </button>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-sm text-slate-700">
                  <thead className="bg-white text-left text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      {activeRows.length > 0 && Object.keys(activeRows[0]).map((column) => (
                        <th key={column} className="px-3 py-2">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {activeRows.map((rowData, rowIndex) => (
                      <tr key={rowIndex}>
                        {Object.values(rowData).map((value, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2">
                            {value ?? ""}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}
      <ValidationTable issues={run.issues} />
      <Link className="inline-flex h-10 items-center rounded-md border border-bank-line bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50" to="/history">
        View history
      </Link>
    </div>
  );
}
