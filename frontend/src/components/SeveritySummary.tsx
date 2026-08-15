interface SeveritySummaryProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

function SeveritySummary({
  critical,
  high,
  medium,
  low,
}: SeveritySummaryProps) {
  const severities = [
    {
      label: "Critical",
      value: critical,
      className: "border-red-900 bg-red-950/30 text-red-400",
    },
    {
      label: "High",
      value: high,
      className: "border-orange-900 bg-orange-950/30 text-orange-400",
    },
    {
      label: "Medium",
      value: medium,
      className: "border-yellow-900 bg-yellow-950/30 text-yellow-400",
    },
    {
      label: "Low",
      value: low,
      className: "border-green-900 bg-green-950/30 text-green-400",
    },
  ];

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div className="mb-5">
        <h2 className="text-xl font-bold text-white">
          Findings by Severity
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Distribution of detected inspection findings
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {severities.map((severity) => (
          <div
            key={severity.label}
            className={`rounded-xl border p-5 ${severity.className}`}
          >
            <span className="text-sm font-medium">
              {severity.label}
            </span>

            <strong className="mt-2 block text-3xl font-bold">
              {severity.value}
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}

export default SeveritySummary;