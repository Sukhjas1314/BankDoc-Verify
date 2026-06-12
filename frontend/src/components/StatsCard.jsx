export default function StatsCard({ label, value, tone = "blue" }) {
  const tones = {
    blue: "border-blue-200 bg-blue-50 text-blue-700",
    green: "border-emerald-200 bg-emerald-50 text-emerald-700",
    red: "border-rose-200 bg-rose-50 text-rose-700",
    gray: "border-slate-200 bg-white text-slate-700"
  };
  return (
    <section className={`rounded-lg border p-4 ${tones[tone]}`}>
      <p className="text-sm font-medium">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
    </section>
  );
}
