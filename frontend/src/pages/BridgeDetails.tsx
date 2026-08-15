import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getBridge, type Bridge } from "../api/bridges";
import {
  getInspections,
  type Inspection,
} from "../api/inspections";

function BridgeDetails() {
  const { bridgeId } = useParams<{ bridgeId: string }>();
  const navigate = useNavigate();

  const [bridge, setBridge] = useState<Bridge | null>(null);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      if (!bridgeId) {
        setError("Bridge ID is missing.");
        setLoading(false);
        return;
      }

      try {
        const [bridgeData, inspectionResponse] = await Promise.all([
          getBridge(bridgeId),
          getInspections(),
        ]);

        setBridge(bridgeData);

        setInspections(
          inspectionResponse.items.filter(
            (inspection) => inspection.bridge_id === bridgeId,
          ),
        );
      } catch (error) {
        console.error("Failed to load bridge:", error);
        setError("Unable to load bridge.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [bridgeId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-slate-100">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <p className="text-slate-400">Loading bridge...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 text-slate-100">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="rounded-2xl border border-red-900 bg-red-950/40 p-6">
            <p className="font-medium text-red-400">{error}</p>
          </div>
        </div>
      </main>
    );
  }

  if (!bridge) {
    return (
      <main className="min-h-screen bg-slate-950 text-slate-100">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <p className="text-slate-400">Bridge not found.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Back */}
        <button
          onClick={() => navigate("/")}
          className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-cyan-400"
        >
          ← Back to Dashboard
        </button>

        {/* Bridge Header */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-7 shadow-xl">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-start">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                Bridge Asset
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                {bridge.name}
              </h1>

              <p className="mt-3 text-slate-400">
                Infrastructure inspection and condition overview
              </p>
            </div>

            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-950 text-2xl">
              🌉
            </div>
          </div>

          {/* Bridge metadata */}
          <div className="mt-8 grid gap-4 sm:grid-cols-3">

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-600">
                Bridge Type
              </p>

              <p className="mt-2 font-semibold text-white">
                {bridge.bridge_type ?? "Unavailable"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-600">
                Location
              </p>

              <p className="mt-2 font-semibold text-white">
                {bridge.location ?? "Unavailable"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-600">
                Coordinates
              </p>

              <p className="mt-2 font-mono text-sm text-slate-300">
                {bridge.latitude !== null &&
                bridge.longitude !== null
                  ? `${bridge.latitude}, ${bridge.longitude}`
                  : "Unavailable"}
              </p>
            </div>

          </div>
        </section>

        {/* Inspection History */}
        <section className="mt-10">

          <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
                Inspection History
              </p>

              <h2 className="mt-1 text-2xl font-bold text-white">
                Inspections
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Historical inspections recorded for this bridge
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2">
              <span className="text-sm text-slate-500">
                Total
              </span>

              <span className="ml-2 font-bold text-white">
                {inspections.length}
              </span>
            </div>
          </div>

          {inspections.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-10 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-xl">
                📋
              </div>

              <p className="mt-4 font-medium text-slate-300">
                No inspections found
              </p>

              <p className="mt-2 text-sm text-slate-500">
                This bridge does not have any recorded inspections yet.
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {inspections.map((inspection) => (
                <article
                  key={inspection.id}
                  className="group rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg transition duration-200 hover:border-cyan-900 hover:shadow-cyan-950/20"
                >
                  <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">

                    <div className="flex gap-4">

                      <div className="hidden h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-lg sm:flex">
                        🔍
                      </div>

                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <h3 className="text-lg font-bold text-white">
                            {inspection.name}
                          </h3>

                          <span className="rounded-full border border-cyan-900 bg-cyan-950/50 px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-cyan-400">
                            {inspection.status}
                          </span>
                        </div>

                        <p className="mt-2 text-sm text-slate-500">
                          {inspection.notes ??
                            "No inspection notes available."}
                        </p>

                        <p className="mt-3 font-mono text-xs text-slate-700">
                          ID: {inspection.id}
                        </p>
                      </div>

                    </div>

                    <button
                      onClick={() =>
                        navigate(`/inspections/${inspection.id}`)
                      }
                      className="shrink-0 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400"
                    >
                      View Inspection →
                    </button>

                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Footer */}
        <footer className="mt-12 border-t border-slate-800 pt-6">
          <p className="text-xs text-slate-600">
            Garuda Kavach • Bridge inspection intelligence
          </p>
        </footer>

      </div>
    </main>
  );
}

export default BridgeDetails;