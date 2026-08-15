interface RiskCardProps {
  riskScore: number;
  riskLevel: string;
  priority: string;
  humanReviewRequired: boolean;
}

function RiskCard({
  riskScore,
  riskLevel,
  priority,
  humanReviewRequired,
}: RiskCardProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
          Risk Engine
        </p>

        <h2 className="mt-1 text-xl font-bold text-white">
          Risk Assessment
        </h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-500">Risk Score</p>

          <p className="mt-2 text-3xl font-bold text-white">
            {riskScore}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-500">Risk Level</p>

          <p className="mt-2 text-xl font-bold uppercase text-cyan-400">
            {riskLevel}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-500">Priority</p>

          <p className="mt-2 text-xl font-bold uppercase text-white">
            {priority.replaceAll("_", " ")}
          </p>
        </div>
      </div>

      {humanReviewRequired && (
        <div className="mt-5 rounded-xl border border-amber-800 bg-amber-950/30 p-4">
          <p className="font-medium text-amber-300">
            ⚠ Human engineering review required
          </p>
        </div>
      )}
    </section>
  );
}

export default RiskCard;