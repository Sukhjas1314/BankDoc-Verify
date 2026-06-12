import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import StatsCard from "../components/StatsCard.jsx";
import { getDashboard } from "../services/api.js";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then((response) => setStats(response.data))
      .catch(() => setError("Dashboard metrics are unavailable."));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 border-b border-bank-line pb-5 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-3xl font-semibold text-slate-950">Dashboard</h1>
          <p className="mt-2 text-sm text-slate-600">Operational view of local report validations.</p>
        </div>
        <Link to="/upload" className="inline-flex h-10 items-center rounded-md bg-bank-blue px-4 text-sm font-semibold text-white hover:bg-blue-700">
          New validation
        </Link>
      </div>
      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          {error}
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard label="Files processed" value={stats?.total_files_processed ?? "0"} />
        <StatsCard label="Validations" value={stats?.total_validations ?? "0"} tone="gray" />
        <StatsCard label="Passed" value={stats?.passed_validations ?? "0"} tone="green" />
        <StatsCard label="Failed" value={stats?.failed_validations ?? "0"} tone="red" />
      </div>
      <section className="rounded-lg border border-bank-line bg-white p-5">
        <div className="flex items-center gap-3">
          <RefreshCw className="h-5 w-5 text-bank-blue" aria-hidden="true" />
          <h2 className="text-lg font-semibold">Validation coverage</h2>
        </div>
        <div className="mt-4 grid gap-3 text-sm text-slate-700 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-md bg-slate-50 p-3">Totals and subtotals</div>
          <div className="rounded-md bg-slate-50 p-3">Opening and closing balances</div>
          <div className="rounded-md bg-slate-50 p-3">Duplicate transactions</div>
          <div className="rounded-md bg-slate-50 p-3">Missing required values</div>
          <div className="rounded-md bg-slate-50 p-3">Formula checks</div>
          <div className="rounded-md bg-slate-50 p-3">Outlier detection</div>
        </div>
      </section>
    </div>
  );
}
