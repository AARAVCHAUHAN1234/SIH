interface FindingCardProps {
  defectType: string;
  description: string | null;
  severity: string;
  confidence: number | null;
}

function FindingCard({
  defectType,
  description,
  severity,
  confidence,
}: FindingCardProps) {
  const severityStyles: Record<string, string> = {
    critical: "border-red-200 bg-red-50 text-red-700",
    high: "border-orange-200 bg-orange-50 text-orange-700",
    medium: "border-yellow-200 bg-yellow-50 text-yellow-700",
    low: "border-green-200 bg-green-50 text-green-700",
  };

  const normalizedSeverity = severity.toLowerCase();

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Defect
          </p>

          <h3 className="mt-1 text-lg font-bold text-slate-900">
            {defectType}
          </h3>
        </div>

        <span
          className={`rounded-full border px-3 py-1 text-xs font-bold uppercase ${
            severityStyles[normalizedSeverity] ??
            "border-slate-200 bg-slate-50 text-slate-700"
          }`}
        >
          {severity}
        </span>
      </div>

      {description && (
        <p className="mt-4 leading-6 text-slate-600">
          {description}
        </p>
      )}

      {confidence !== null && (
        <div className="mt-5 border-t border-slate-100 pt-4">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-slate-500">
              AI Confidence
            </span>

            <strong className="text-slate-900">
              {(confidence * 100).toFixed(1)}%
            </strong>
          </div>

          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-cyan-500"
              style={{
                width: `${Math.min(Math.max(confidence * 100, 0), 100)}%`,
              }}
            />
          </div>
        </div>
      )}
    </article>
  );
}

export default FindingCard;