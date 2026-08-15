import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import RiskCard from "../components/RiskCard";
import SeveritySummary from "../components/SeveritySummary";
import ComponentConditionCard from "../components/ComponentConditionCard";
import {
  getInspection,
  getInspectionSummary,
  getInspectionIntelligence,
  type Inspection,
  type InspectionSummary,
  type InspectionIntelligence,
} from "../api/inspections";
import FindingCard from "../components/FindingCard";
import {
  getInspectionFindings,
  type Finding,
} from "../api/findings";
function InspectionDetails() {
  const { inspectionId } = useParams<{ inspectionId: string }>();
  const navigate = useNavigate();
const [findings, setFindings] = useState<Finding[]>([]);
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [summary, setSummary] = useState<InspectionSummary | null>(null);
  const [intelligence, setIntelligence] =
    useState<InspectionIntelligence | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInspection() {
      if (!inspectionId) {
        setError("Inspection ID is missing.");
        setLoading(false);
        return;
      }

      try {
        const [
  inspectionData,
  summaryData,
  intelligenceData,
  findingsData,
] = await Promise.all([
  getInspection(inspectionId),
  getInspectionSummary(inspectionId),
  getInspectionIntelligence(inspectionId),
  getInspectionFindings(inspectionId),
]);

setInspection(inspectionData);
setSummary(summaryData);
setIntelligence(intelligenceData);
setFindings(findingsData);
      } catch (error) {
        console.error("Failed to load inspection:", error);
        setError("Unable to load inspection.");
      } finally {
        setLoading(false);
      }
    }

    loadInspection();
  }, [inspectionId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <p className="text-slate-400">
              Loading inspection...
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-2xl border border-red-900 bg-red-950/40 p-6">
            <p className="font-medium text-red-400">{error}</p>
          </div>
        </div>
      </main>
    );
  }

  if (!inspection || !summary || !intelligence) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <p className="text-slate-400">
            Inspection data unavailable.
          </p>
        </div>
      </main>
    );
  }

  const risk = intelligence.intelligence;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-white"
        >
          ← Back
        </button>

        {/* Header */}
        <header className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-7 shadow-xl">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-start">

            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Inspection
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                {inspection.name}
              </h1>

              {inspection.notes && (
                <p className="mt-3 max-w-2xl text-slate-400">
                  {inspection.notes}
                </p>
              )}
            </div>

            <span className="inline-flex w-fit items-center rounded-full border border-cyan-800 bg-cyan-950/50 px-4 py-2 text-xs font-bold uppercase tracking-wide text-cyan-300">
              {inspection.status}
            </span>
          </div>
        </header>

        {/* Overview */}
        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-white">
              Inspection Overview
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Inspection data and recorded observations
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-500">
                Components
              </p>

              <p className="mt-2 text-3xl font-bold text-white">
                {summary.statistics.component_count}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-500">
                Media Assets
              </p>

              <p className="mt-2 text-3xl font-bold text-white">
                {summary.statistics.media_count}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-sm text-slate-500">
                Findings
              </p>

              <p className="mt-2 text-3xl font-bold text-white">
                {summary.statistics.finding_count ?? 0}
              </p>
            </div>

          </div>
        </section>

        {/* Risk */}
        <section className="mb-8">
          <RiskCard
            riskScore={risk.risk_score}
            riskLevel={risk.risk_level}
            priority={risk.priority}
            humanReviewRequired={risk.human_review_required}
          />
        </section>

        {/* Severity */}
        <section className="mb-8">
          <SeveritySummary
            critical={intelligence.severity_summary.critical}
            high={intelligence.severity_summary.high}
            medium={intelligence.severity_summary.medium}
            low={intelligence.severity_summary.low}
          />
        </section>
        <section className="mb-8">
  <div className="mb-5">
    <h2 className="text-xl font-bold text-white">
      Inspection Findings
    </h2>

    <p className="mt-1 text-sm text-slate-500">
      Detected defects and inspection observations
    </p>
  </div>

  {findings.length === 0 ? (
    <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-8 text-center">
      <p className="font-medium text-slate-300">
        No findings recorded.
      </p>

      <p className="mt-1 text-sm text-slate-500">
        No defects have been associated with this inspection.
      </p>
    </div>
  ) : (
    <div className="grid gap-4 md:grid-cols-2">
      {findings.map((finding) => (
        <FindingCard
          key={finding.id}
          defectType={finding.defect_type}
          description={finding.description}
          severity={finding.severity}
          confidence={finding.confidence}
        />
      ))}
    </div>
  )}
</section>
        {/* Component Conditions */}
        <section className="mb-8">
          <div className="mb-5">
            <h2 className="text-xl font-bold text-white">
              Component Condition
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Condition assessment across inspected bridge components
            </p>
          </div>

          {intelligence.components.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-8 text-center">
              <p className="font-medium text-slate-300">
                No component condition data available.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {intelligence.components.map((component) => (
                <ComponentConditionCard
                  key={component.component_id}
                  componentName={component.component_name}
                  componentType={component.component_type}
                  findingCount={component.finding_count}
                  riskScore={component.risk_score}
                  condition={component.condition}
                />
              ))}
            </div>
          )}
        </section>

        {/* Recommendation */}
        <section className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-sm">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-white">
              Engineering Recommendation
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Generated inspection intelligence
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
            <p className="leading-7 text-slate-300">
              {intelligence.recommendation}
            </p>
          </div>
        </section>

        {/* Footer note */}
        <div className="border-t border-slate-800 py-6">
          <p className="text-xs leading-5 text-slate-500">
            AI-generated inspection intelligence is decision support only.
            Final structural assessment requires qualified human engineering
            review.
          </p>
        </div>

      </div>
    </main>
  );
}

export default InspectionDetails;