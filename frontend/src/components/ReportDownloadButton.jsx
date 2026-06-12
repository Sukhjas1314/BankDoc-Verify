import { Download } from "lucide-react";

import { reportUrl } from "../services/api.js";

export default function ReportDownloadButton({ runId }) {
  return (
    <a
      href={reportUrl(runId)}
      className="inline-flex h-10 items-center gap-2 rounded-md bg-bank-blue px-4 text-sm font-semibold text-white hover:bg-blue-700"
    >
      <Download className="h-4 w-4" aria-hidden="true" />
      Download report
    </a>
  );
}
