import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function Panel({ title, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">{title}</h2>
      {children}
    </section>
  );
}

function DataTable({ title, rows }) {
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-3 text-base font-semibold text-slate-800">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-500">No records.</p>
      ) : (
        <div className="overflow-auto rounded-lg border border-slate-200">
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
  const [unitTestResult, setUnitTestResult] = useState(null);
  const [smokeTestResult, setSmokeTestResult] = useState(null);
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

  async function runUnitTests() {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/qa/run-unit-tests`, { method: "POST" });
      const payload = await response.json();
      setUnitTestResult(payload);
    } catch (error) {
      setUnitTestResult({
        status: "fail",
        passed: false,
        test_count: 0,
        duration_ms: 0,
        output: String(error),
      });
    } finally {
      setLoading(false);
    }
  }

  async function runSmokeTest() {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/qa/run-smoke-test`, { method: "POST" });
      const payload = await response.json();
      setSmokeTestResult(payload);
    } catch (error) {
      setSmokeTestResult({
        status: "fail",
        passed: false,
        duration_ms: 0,
        output: String(error),
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl space-y-5 p-6">
      <header className="rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 p-5 text-white shadow-lg">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold">ABC MCP Testing UI</h1>
            <p className="mt-1 text-xs text-slate-300">API Base: {API_BASE}</p>
          </div>
          <span className="inline-flex w-fit rounded-full border border-slate-600 bg-slate-700/70 px-3 py-1 text-xs text-slate-200">
            {tab === "testing" ? "Testing Mode" : "Application Data Mode"}
          </span>
        </div>
        <nav className="mt-4 flex gap-2">
          <button
            onClick={() => setTab("testing")}
            className={`rounded-lg px-3 py-2 text-sm transition ${
              tab === "testing" ? "bg-white text-slate-900 shadow" : "bg-slate-700 text-slate-100 hover:bg-slate-600"
            }`}
          >
            Testing UI
          </button>
          <button
            onClick={() => {
              setTab("application");
              loadApplicationData();
            }}
            className={`rounded-lg px-3 py-2 text-sm transition ${
              tab === "application" ? "bg-white text-slate-900 shadow" : "bg-slate-700 text-slate-100 hover:bg-slate-600"
            }`}
          >
            Main Application Data
          </button>
          <button
            onClick={() => setTab("quality")}
            className={`rounded-lg px-3 py-2 text-sm transition ${
              tab === "quality" ? "bg-white text-slate-900 shadow" : "bg-slate-700 text-slate-100 hover:bg-slate-600"
            }`}
          >
            Test Status
          </button>
        </nav>
      </header>

      {tab === "testing" ? (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Panel title="1) Health Check">
              <button
                onClick={() => callApi("/health")}
                className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white transition hover:bg-slate-700"
              >
                Run health_check
              </button>
            </Panel>

            <Panel title="2) Search Entities">
              <div className="space-y-2">
                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="account">account</option>
                  <option value="lead">lead</option>
                </select>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  placeholder="Search query"
                />
                <button
                  onClick={() => callApi(`/search?query=${encodeURIComponent(query)}&entity_type=${entityType}`)}
                  className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white transition hover:bg-indigo-500"
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
                  className="w-full rounded-lg border border-slate-300 p-2 text-sm focus:border-emerald-500 focus:outline-none"
                  placeholder="acc_001"
                />
                <button
                  onClick={() => callApi(`/account/${encodeURIComponent(accountId)}/360`)}
                  className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white transition hover:bg-emerald-500"
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
                  className="w-full rounded-lg border border-slate-300 p-2 text-sm focus:border-cyan-600 focus:outline-none"
                  placeholder="lead_001"
                />
                <button
                  onClick={() => callApi(`/lead/${encodeURIComponent(leadId)}/360`)}
                  className="rounded-lg bg-cyan-700 px-3 py-2 text-sm text-white transition hover:bg-cyan-600"
                >
                  Run get_lead_360
                </button>
              </div>
            </Panel>
          </div>

          <Panel title="Output">
            {loading ? <p className="text-sm text-slate-500">Loading...</p> : null}
            <pre className="max-h-[460px] overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
              {JSON.stringify(output, null, 2)}
            </pre>
          </Panel>
        </>
      ) : tab === "application" ? (
        <div className="space-y-4">
          <Panel title="Application Data Explorer">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-slate-600">
                View raw seeded records from application tables.
              </p>
              <button
                onClick={loadApplicationData}
                className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white transition hover:bg-slate-700"
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
      ) : (
        <div className="space-y-4">
          <Panel title="Unit Test Runner">
            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={runUnitTests}
                className="rounded-lg bg-violet-700 px-3 py-2 text-sm text-white transition hover:bg-violet-600"
              >
                Run Unit Tests
              </button>
              <button
                onClick={runSmokeTest}
                className="rounded-lg bg-indigo-700 px-3 py-2 text-sm text-white transition hover:bg-indigo-600"
              >
                Run Smoke Test
              </button>
              {unitTestResult ? (
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    unitTestResult.passed ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                  }`}
                >
                  {unitTestResult.passed ? "PASS" : "FAIL"}
                </span>
              ) : null}
              {smokeTestResult ? (
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    smokeTestResult.passed ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                  }`}
                >
                  {smokeTestResult.passed ? "SMOKE PASS" : "SMOKE FAIL"}
                </span>
              ) : null}
            </div>
            {loading ? <p className="mt-3 text-sm text-slate-500">Running tests...</p> : null}
            <div className="mt-4 grid gap-4 text-sm text-slate-700 md:grid-cols-2">
              {unitTestResult ? (
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p>
                    <span className="font-semibold">Unit Status:</span> {unitTestResult.status}
                  </p>
                  <p>
                    <span className="font-semibold">Unit Tests:</span> {unitTestResult.test_count}
                  </p>
                  <p>
                    <span className="font-semibold">Unit Duration:</span> {unitTestResult.duration_ms} ms
                  </p>
                </div>
              ) : null}
              {smokeTestResult ? (
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p>
                    <span className="font-semibold">Smoke Status:</span> {smokeTestResult.status}
                  </p>
                  <p>
                    <span className="font-semibold">Smoke Duration:</span> {smokeTestResult.duration_ms} ms
                  </p>
                </div>
              ) : null}
            </div>
          </Panel>

          <Panel title="Unit Test Output">
            <pre className="max-h-[460px] overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
              {unitTestResult?.output || "No test run yet."}
            </pre>
          </Panel>
          <Panel title="Smoke Test Output">
            <pre className="max-h-[460px] overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
              {smokeTestResult?.output || "No smoke test run yet."}
            </pre>
          </Panel>
        </div>
      )}
    </main>
  );
}
