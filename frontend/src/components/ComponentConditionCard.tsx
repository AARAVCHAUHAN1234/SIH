interface ComponentConditionCardProps {
  componentName: string;
  componentType: string;
  findingCount: number;
  riskScore: number;
  condition: string;
}

function ComponentConditionCard({
  componentName,
  componentType,
  findingCount,
  riskScore,
  condition,
}: ComponentConditionCardProps) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl transition hover:border-slate-700 hover:shadow-2xl">
      <div className="mb-5">
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-cyan-400">
          Bridge Component
        </p>

        <h3 className="mt-1 text-lg font-bold text-white">
          {componentName}
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          {componentType}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Findings
          </span>

          <strong className="mt-1 block text-2xl font-bold text-white">
            {findingCount}
          </strong>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Risk Score
          </span>

          <strong className="mt-1 block text-2xl font-bold text-white">
            {riskScore.toFixed(2)}
          </strong>
        </div>
      </div>

      <div className="mt-5 border-t border-slate-800 pt-4">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
          Condition
        </span>

        <p className="mt-1 font-semibold text-slate-200">
          {condition}
        </p>
      </div>
    </article>
  );
}

export default ComponentConditionCard;