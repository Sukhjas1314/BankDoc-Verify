import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

const icons = {
  passed: CheckCircle2,
  failed: XCircle,
  warning: AlertTriangle
};

export default function ValidationTable({ issues = [] }) {
  if (!issues.length) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-emerald-800">
        <CheckCircle2 className="mb-2 h-5 w-5" aria-hidden="true" />
        All validation checks passed.
      </div>
    );
  }
  return (
    <div className="overflow-hidden rounded-lg border border-bank-line bg-white">
      <table className="min-w-full divide-y divide-bank-line text-sm">
        <thead className="bg-slate-100 text-left text-xs font-semibold uppercase text-slate-600">
          <tr>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Severity</th>
            <th className="px-4 py-3">Description</th>
            <th className="px-4 py-3">Expected</th>
            <th className="px-4 py-3">Actual</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-bank-line">
          {issues.map((issue) => {
            const Icon = icons[issue.severity === "low" ? "warning" : "failed"];
            return (
              <tr key={issue.id}>
                <td className="px-4 py-3">
                  <Icon className="h-4 w-4 text-rose-600" aria-hidden="true" />
                </td>
                <td className="px-4 py-3 font-medium text-slate-900">{issue.issue_type}</td>
                <td className="px-4 py-3 capitalize">{issue.severity}</td>
                <td className="px-4 py-3 text-slate-700">{issue.description}</td>
                <td className="px-4 py-3 text-slate-600">{issue.expected_value || "-"}</td>
                <td className="px-4 py-3 text-slate-600">{issue.actual_value || "-"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
