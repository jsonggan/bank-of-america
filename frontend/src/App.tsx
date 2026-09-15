import { useState } from "react";
import { api } from "./api";
import { examples, pretty } from "./examples";

const steps = [
  { key: "schema", title: "1. Register Schema", endpoint: "POST /schema", label: "Schema JSON", action: "Register schema", description: "Define field names, types, and required fields.", initial: pretty(examples.trade.schema) },
  { key: "ingest", title: "2. Ingest Data", endpoint: "POST /ingest", label: "Data JSON", action: "Ingest data", description: "Validate required fields and types; reject unknown fields. Invalid batches are not stored.", initial: pretty(examples.trade.rows) },
  { key: "dashboard", title: "3. Register Dashboard Configuration", endpoint: "POST /dashboard", label: "Dashboard JSON", action: "Register dashboard", description: "Choose a schema and configure summary or table views.", initial: pretty(examples.trade.dashboard) },
  { key: "generate", title: "4. Generate Dashboard Data", endpoint: "GET /dashboard/{name}", label: "Dashboard name", action: "Generate dashboard data", description: "Return dashboard data using the registered schema, ingested rows, and configuration.", initial: examples.trade.dashboard.name },
] as const;
type Step = (typeof steps)[number]["key"];
type Result = { data?: Record<string, unknown>; error?: string };

export default function App() {
  const [inputs, setInputs] = useState<Record<Step, string>>({ schema: steps[0].initial, ingest: steps[1].initial, dashboard: steps[2].initial, generate: steps[3].initial });
  const [results, setResults] = useState<Partial<Record<Step, Result>>>({});
  const [busy, setBusy] = useState<Step | null>(null);
  async function submit(step: Step) {
    if (busy) return; setBusy(step); setResults((p) => ({ ...p, [step]: {} }));
    try {
      if (step !== "generate") { try { JSON.parse(inputs[step]); } catch { throw new Error("Enter valid JSON before submitting."); } }
      const data = await api<Record<string, unknown>>(step === "generate" ? `/dashboard/${encodeURIComponent(inputs.generate)}` : `/${step}`, step === "generate" ? undefined : inputs[step]);
      setResults((p) => ({ ...p, [step]: { data } }));
      if (step === "dashboard" && typeof data.name === "string") { setInputs((p) => ({ ...p, generate: data.name as string })); setResults((p) => ({ ...p, generate: {} })); }
    } catch (error) { setResults((p) => ({ ...p, [step]: { error: (error as Error).message } })); } finally { setBusy(null); }
  }
  return <main className="mx-auto max-w-6xl px-4 py-8 sm:px-8"><header className="mb-8"><h1 className="text-2xl font-semibold">Schema-Driven Dashboard Platform</h1><p className="mt-2 text-sm text-slate-600">Follow the four assignment requirements in order. Trade examples are prefilled and editable.</p><p className="mt-1 text-sm text-slate-600">All data is stored in memory and resets when the backend restarts.</p></header><div className="grid items-start gap-6 lg:grid-cols-2">{steps.map((step) => { const result = results[step.key]; const message = step.key === "schema" ? "Schema registered successfully." : step.key === "dashboard" ? "Dashboard registered successfully." : step.key === "ingest" ? `${result?.data?.accepted} ${result?.data?.accepted === 1 ? "row" : "rows"} accepted.` : "Dashboard data generated."; return <section key={step.key} aria-labelledby={`${step.key}-heading`} className="min-w-0 rounded-lg border border-slate-200 bg-white p-5"><h2 id={`${step.key}-heading`} className="text-lg font-semibold">{step.title}</h2><code className="mt-2 inline-block rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">{step.endpoint}</code><p className="my-3 text-sm text-slate-600">{step.description}</p><form onSubmit={(e) => { e.preventDefault(); void submit(step.key); }}><label htmlFor={step.key} className="mb-2 block text-sm font-medium">{step.label}</label>{step.key === "generate" ? <input id={step.key} required disabled={busy !== null} value={inputs.generate} onChange={(e) => { setInputs({ ...inputs, generate: e.target.value }); setResults({ ...results, generate: {} }); }} /> : <textarea id={step.key} rows={12} spellCheck={false} disabled={busy !== null} value={inputs[step.key]} onChange={(e) => { setInputs({ ...inputs, [step.key]: e.target.value }); setResults({ ...results, [step.key]: {} }); }} />}<button className="mt-3" disabled={busy !== null}>{busy === step.key ? "Submitting..." : step.action}</button></form>{result?.error && <p role="alert" className="mt-3 break-words text-sm text-red-700">{result.error}</p>}{result?.data && <div className="mt-3"><p role="status" className="text-sm text-emerald-700">{message}</p><details open={step.key === "generate"} className="mt-2 text-sm"><summary className="cursor-pointer text-slate-600">Response JSON</summary><pre aria-label={step.key === "generate" ? "Generated dashboard data" : `${step.label} response`} className="mt-2 max-h-96 overflow-auto rounded bg-slate-50 p-3 text-xs">{pretty(result.data)}</pre></details></div>}</section>; })}</div></main>;
}
