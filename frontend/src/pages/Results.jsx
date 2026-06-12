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
      <ValidationTable issues={run.issues} />
      <Link className="inline-flex h-10 items-center rounded-md border border-bank-line bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50" to="/history">
        View history
      </Link>
    </div>
  );
}
