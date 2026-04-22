import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function Panel({ title, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-lg font-semibold text-slate-800">{title}</h2>
      {children}
    </section>
  );
}

function DataTable({ title, rows }) {
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-base font-semibold text-slate-800">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-500">No records.</p>
      ) : (
        <div className="overflow-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-100 text-slate-700">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="px-3 py-2 font-medium">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx} className="border-t border-slate-200">
                  {columns.map((col) => (
                    <td key={col} className="px-3 py-2 text-slate-700">
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default function App() {
  const [tab, setTab] = useState("testing");
  const [entityType, setEntityType] = useState("account");
  const [query, setQuery] = useState("Acme");
  const [accountId, setAccountId] = useState("acc_001");
  const [leadId, setLeadId] = useState("lead_001");
  const [output, setOutput] = useState({ message: "Run a test action to see output." });
  const [appData, setAppData] = useState({ accounts: [], leads: [], opportunities: [], activities: [] });
  const [loading, setLoading] = useState(false);

  async function callApi(path) {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}${path}`);
      const payload = await response.json();
      setOutput(payload);
    } catch (error) {
      setOutput({ error: { message: String(error) } });
    } finally {
      setLoading(false);
    }
  }

  async function loadApplicationData() {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/application-data`);
      const payload = await response.json();
      setAppData(payload);
    } catch (error) {
      setOutput({ error: { message: String(error) } });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl space-y-5 p-6">
      <header className="rounded-xl bg-slate-900 p-5 text-white">
        <h1 className="text-2xl font-bold">ABC MCP Testing UI</h1>
        <p className="mt-2 text-sm text-slate-200">
          Test flow: Application data to MCP-like tools via API to user validation.
        </p>
        <p className="mt-1 text-xs text-slate-300">API Base: {API_BASE}</p>
        <nav className="mt-4 flex gap-2">
          <button
            onClick={() => setTab("testing")}
            className={`rounded px-3 py-2 text-sm ${
              tab === "testing" ? "bg-white text-slate-900" : "bg-slate-700 text-slate-100"
            }`}
          >
            Testing UI
          </button>
          <button
            onClick={() => {
              setTab("application");
              loadApplicationData();
            }}
            className={`rounded px-3 py-2 text-sm ${
              tab === "application" ? "bg-white text-slate-900" : "bg-slate-700 text-slate-100"
            }`}
          >
            Main Application Data
          </button>
        </nav>
      </header>

      {tab === "testing" ? (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Panel title="1) Health Check">
              <button
                onClick={() => callApi("/health")}
                className="rounded bg-slate-900 px-3 py-2 text-sm text-white hover:bg-slate-700"
              >
                Run health_check
              </button>
            </Panel>

            <Panel title="2) Search Entities">
              <div className="space-y-2">
                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2 text-sm"
                >
                  <option value="account">account</option>
                  <option value="lead">lead</option>
                </select>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2 text-sm"
                  placeholder="Search query"
                />
                <button
                  onClick={() => callApi(`/search?query=${encodeURIComponent(query)}&entity_type=${entityType}`)}
                  className="rounded bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-500"
                >
                  Run search_entities
                </button>
              </div>
            </Panel>

            <Panel title="3) Account 360">
              <div className="space-y-2">
                <input
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2 text-sm"
                  placeholder="acc_001"
                />
                <button
                  onClick={() => callApi(`/account/${encodeURIComponent(accountId)}/360`)}
                  className="rounded bg-emerald-600 px-3 py-2 text-sm text-white hover:bg-emerald-500"
                >
                  Run get_account_360
                </button>
              </div>
            </Panel>

            <Panel title="4) Lead 360">
              <div className="space-y-2">
                <input
                  value={leadId}
                  onChange={(e) => setLeadId(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2 text-sm"
                  placeholder="lead_001"
                />
                <button
                  onClick={() => callApi(`/lead/${encodeURIComponent(leadId)}/360`)}
                  className="rounded bg-cyan-700 px-3 py-2 text-sm text-white hover:bg-cyan-600"
                >
                  Run get_lead_360
                </button>
              </div>
            </Panel>
          </div>

          <Panel title="Output">
            {loading ? <p className="text-sm text-slate-500">Loading...</p> : null}
            <pre className="max-h-[460px] overflow-auto rounded bg-slate-950 p-4 text-xs text-slate-100">
              {JSON.stringify(output, null, 2)}
            </pre>
          </Panel>
        </>
      ) : (
        <div className="space-y-4">
          <Panel title="Application Data Explorer">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-slate-600">
                View raw seeded records from application tables.
              </p>
              <button
                onClick={loadApplicationData}
                className="rounded bg-slate-900 px-3 py-2 text-sm text-white hover:bg-slate-700"
              >
                Refresh Data
              </button>
            </div>
            {loading ? <p className="mt-3 text-sm text-slate-500">Loading...</p> : null}
          </Panel>
          <DataTable title="Accounts" rows={appData.accounts || []} />
          <DataTable title="Leads" rows={appData.leads || []} />
          <DataTable title="Opportunities" rows={appData.opportunities || []} />
          <DataTable title="Activities" rows={appData.activities || []} />
        </div>
      )}
    </main>
  );
}
