import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getBridges, type Bridge } from "../api/bridges";

function Dashboard() {
  const [bridges, setBridges] = useState<Bridge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    async function loadBridges() {
      try {
        const response = await getBridges();
        setBridges(response.items);
      } catch (error) {
        console.error("Failed to load bridges:", error);
        setError("Unable to load bridges.");
      } finally {
        setLoading(false);
      }
    }

    loadBridges();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <p className="text-slate-400">
              Loading Garuda Kavach...
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
          <div className="rounded-2xl border border-red-900 bg-red-950/30 p-6">
            <p className="font-medium text-red-400">
              {error}
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}
        <header className="mb-10">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">

            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                Infrastructure Intelligence
              </p>

              <h1 className="text-4xl font-bold tracking-tight text-white md:text-5xl">
                Garuda Kavach
              </h1>

              <p className="mt-3 max-w-2xl text-slate-400">
                AI-powered bridge inspection and infrastructure
                monitoring platform.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 px-6 py-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Bridges Monitored
              </p>

              <p className="mt-1 text-3xl font-bold text-white">
                {bridges.length}
              </p>
            </div>

          </div>
        </header>

        {/* Bridge Section */}
        <section>
          <div className="mb-5">
            <h2 className="text-2xl font-bold text-white">
              Bridge Infrastructure
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Select a bridge to view inspections and condition intelligence.
            </p>
          </div>

          {bridges.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900 p-10 text-center">
              <p className="font-medium text-slate-300">
                No bridges found.
              </p>

              <p className="mt-1 text-sm text-slate-500">
                Add a bridge to begin infrastructure monitoring.
              </p>
            </div>
          ) : (
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {bridges.map((bridge) => (
                <article
                  key={bridge.id}
                  onClick={() =>
                    navigate(`/bridges/${bridge.id}`)
                  }
                  className="group cursor-pointer rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg transition duration-200 hover:-translate-y-1 hover:border-cyan-800 hover:bg-slate-900/90 hover:shadow-2xl"
                >
                  <div className="flex items-start justify-between gap-4">

                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-cyan-400">
                        Bridge
                      </p>

                      <h3 className="mt-1 text-xl font-bold text-white">
                        {bridge.name}
                      </h3>
                    </div>

                    <span className="rounded-full border border-emerald-900 bg-emerald-950/40 px-3 py-1 text-xs font-semibold uppercase text-emerald-400">
                      Active
                    </span>

                  </div>

                  <div className="mt-6 space-y-4">

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-500">
                        Bridge Type
                      </p>

                      <p className="mt-1 font-medium text-slate-200">
                        {bridge.bridge_type ?? "Unavailable"}
                      </p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-500">
                        Location
                      </p>

                      <p className="mt-1 font-medium text-slate-200">
                        {bridge.location ?? "Unavailable"}
                      </p>
                    </div>

                  </div>

                  <div className="mt-6 border-t border-slate-800 pt-4">
                    <span className="text-sm font-semibold text-cyan-400 transition group-hover:text-cyan-300">
                      View Bridge →
                    </span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Footer */}
        <footer className="mt-12 border-t border-slate-800 py-6">
          <p className="text-xs leading-5 text-slate-500">
            Garuda Kavach provides AI-assisted inspection intelligence.
            Final structural assessment requires qualified human engineering
            review.
          </p>
        </footer>

      </div>
    </main>
  );
}

export default Dashboard;