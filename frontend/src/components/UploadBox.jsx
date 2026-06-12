import { FileCheck2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

export default function UploadBox({ onUpload, busy }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);

  function chooseFile(nextFile) {
    if (nextFile) {
      setFile(nextFile);
    }
  }

  return (
    <div
      className={`rounded-lg border-2 border-dashed bg-white p-8 text-center ${
        dragging ? "border-bank-blue bg-blue-50" : "border-bank-line"
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        chooseFile(event.dataTransfer.files[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.xlsx,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        className="hidden"
        onChange={(event) => chooseFile(event.target.files[0])}
      />
      <UploadCloud className="mx-auto h-12 w-12 text-bank-blue" aria-hidden="true" />
      <h1 className="mt-4 text-2xl font-semibold text-slate-950">Upload banking report</h1>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-600">
        PDF and XLSX reports up to 25 MB are validated locally for totals, balances, duplicates, missing fields, formula mismatches, and anomalies.
      </p>
      {file && (
        <div className="mx-auto mt-5 flex max-w-xl items-center justify-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          <FileCheck2 className="h-4 w-4" aria-hidden="true" />
          {file.name}
        </div>
      )}
      <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
        <button
          type="button"
          className="rounded-md border border-bank-line bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          onClick={() => inputRef.current?.click()}
        >
          Select file
        </button>
        <button
          type="button"
          disabled={!file || busy}
          className="rounded-md bg-bank-blue px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          onClick={() => onUpload(file)}
        >
          {busy ? "Validating" : "Upload and validate"}
        </button>
      </div>
    </div>
  );
}
