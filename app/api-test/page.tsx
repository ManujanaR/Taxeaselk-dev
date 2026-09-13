"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  Server,
  Database,
  ArrowRight,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { supabase } from "@/lib/supabase";

interface TestResult {
  id: string;
  name: string;
  endpoint: string;
  method: string;
  category: "Core" | "Business" | "Auditor" | "Supabase";
  status: "idle" | "running" | "passed" | "failed";
  latencyMs?: number;
  httpStatus?: number;
  details?: any;
  error?: string;
}

const TESTS: Omit<TestResult, "status">[] = [
  {
    id: "t_root",
    name: "FastAPI Health & Root Endpoint",
    endpoint: "/",
    method: "GET",
    category: "Core",
  },
  {
    id: "t_supabase",
    name: "Supabase Cloud Connection",
    endpoint: "Supabase Client",
    method: "SDK",
    category: "Supabase",
  },
  {
    id: "t_dashboard",
    name: "Business Dashboard (5 Stages & CIT Metrics)",
    endpoint: "/api/dashboard?company_name=ABC+(Pvt)+Ltd",
    method: "GET",
    category: "Business",
  },
  {
    id: "t_docs",
    name: "Documents Repository API",
    endpoint: "/api/documents?company_name=ABC+(Pvt)+Ltd",
    method: "GET",
    category: "Business",
  },
  {
    id: "t_financials",
    name: "Financials & Sri Lanka CIT Engine (5 Tabs)",
    endpoint: "/api/financials?company_name=ABC+(Pvt)+Ltd",
    method: "GET",
    category: "Business",
  },
  {
    id: "t_engagement",
    name: "Auditor Engagement & Appointment Check",
    endpoint: "/api/auditor-engagement/ABC+(Pvt)+Ltd",
    method: "GET",
    category: "Business",
  },
  {
    id: "t_checklists",
    name: "Statutory & Industry Checklist Presets",
    endpoint: "/api/checklists/presets",
    method: "GET",
    category: "Business",
  },
  {
    id: "t_auditor_dash",
    name: "Auditor Dashboard (Workload & Priority Queue)",
    endpoint: "/api/auditor/dashboard",
    method: "GET",
    category: "Auditor",
  },
  {
    id: "t_auditor_companies",
    name: "Auditor Client Companies Portfolio",
    endpoint: "/api/auditor/companies",
    method: "GET",
    category: "Auditor",
  },
  {
    id: "t_notifications",
    name: "Real-time Notification Service",
    endpoint: "/api/notifications?role=business",
    method: "GET",
    category: "Core",
  },
];

export default function ApiTestPage() {
  const [results, setResults] = useState<TestResult[]>(
    TESTS.map((t) => ({ ...t, status: "idle" }))
  );
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "Not configured";

  async function runSingleTest(testId: string) {
    setResults((prev) =>
      prev.map((r) => (r.id === testId ? { ...r, status: "running", error: undefined } : r))
    );

    const testDef = TESTS.find((t) => t.id === testId);
    if (!testDef) return;

    const start = performance.now();

    try {
      if (testDef.category === "Supabase") {
        // Test Supabase connection
        const { data, error } = await supabase.from("users").select("count").limit(1);
        const duration = Math.round(performance.now() - start);

        if (error && !error.message.includes("relation") && !error.message.includes("does not exist")) {
          throw new Error(error.message);
        }

        setResults((prev) =>
          prev.map((r) =>
            r.id === testId
              ? {
                  ...r,
                  status: "passed",
                  latencyMs: duration,
                  httpStatus: 200,
                  details: {
                    supabase_url: supabaseUrl,
                    status: "Connected successfully to Supabase cloud project.",
                    note: error?.message || "Ready for queries",
                  },
                }
              : r
          )
        );
        return;
      }

      // Test FastAPI backend endpoint
      const fullUrl = `${apiUrl}${testDef.endpoint}`;
      const res = await fetch(fullUrl, { cache: "no-store" });
      const duration = Math.round(performance.now() - start);

      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status}: ${errText || res.statusText}`);
      }

      const json = await res.json().catch(() => ({ status: "OK" }));

      setResults((prev) =>
        prev.map((r) =>
          r.id === testId
            ? {
                ...r,
                status: "passed",
                latencyMs: duration,
                httpStatus: res.status,
                details: json,
              }
            : r
        )
      );
    } catch (err: any) {
      const duration = Math.round(performance.now() - start);
      setResults((prev) =>
        prev.map((r) =>
          r.id === testId
            ? {
                ...r,
                status: "failed",
                latencyMs: duration,
                error: err.message || "Failed to fetch from backend",
              }
            : r
        )
      );
    }
  }

  async function runAllTests() {
    setIsRunningAll(true);
    for (const test of TESTS) {
      await runSingleTest(test.id);
    }
    setIsRunningAll(false);
  }

  useEffect(() => {
    runAllTests();
  }, []);

  const passedCount = results.filter((r) => r.status === "passed").length;
  const failedCount = results.filter((r) => r.status === "failed").length;
  const totalCount = results.length;

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-gray-200">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-navy text-white">
                <Server className="h-5 w-5 text-brand-blue-light" />
              </div>
              <h1 className="text-2xl font-black text-brand-navy">
                TaxEaseLK — Frontend & Backend Verification Suite
              </h1>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Live diagnostics validating API routes, database connections, and latency between Next.js and FastAPI.
            </p>
          </div>

          <Button
            icon={isRunningAll ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            onClick={runAllTests}
            disabled={isRunningAll}
            className="bg-brand-blue hover:bg-brand-blue-dark text-white font-semibold"
          >
            {isRunningAll ? "Testing..." : "Re-Run All Tests"}
          </Button>
        </div>

        {/* Configuration Overview Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
          <Card className="p-4 bg-white border border-gray-200 shadow-xs flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-brand-blue">
              <Server className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">FastAPI Backend URL</span>
              <p className="text-sm font-mono font-bold text-gray-900 truncate">{apiUrl}</p>
            </div>
          </Card>

          <Card className="p-4 bg-white border border-gray-200 shadow-xs flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
              <Database className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Supabase Cloud URL</span>
              <p className="text-sm font-mono font-bold text-gray-900 truncate">{supabaseUrl}</p>
            </div>
          </Card>
        </div>

        {/* Overall Status Banner */}
        <div className="mt-6">
          {passedCount === totalCount ? (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-600 shrink-0" />
                <div>
                  <h3 className="text-sm font-bold text-emerald-900">
                    All {totalCount} Endpoints & Database Connections Verified!
                  </h3>
                  <p className="text-xs text-emerald-700 mt-0.5">
                    Your Next.js frontend is 100% connected to the FastAPI backend and ready for production workflows.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Link href="/dashboard">
                  <Button size="sm" variant="outline" className="bg-white hover:bg-emerald-100 text-emerald-800 border-emerald-300">
                    Business Portal <ArrowRight className="h-3.5 w-3.5 ml-1" />
                  </Button>
                </Link>
                <Link href="/auditor-dashboard">
                  <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white">
                    Auditor Portal <ArrowRight className="h-3.5 w-3.5 ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          ) : failedCount > 0 ? (
            <div className="rounded-xl bg-amber-50 border border-amber-200 p-4 flex items-start gap-3">
              <XCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-bold text-amber-900">
                  {failedCount} of {totalCount} tests failed or backend is not running
                </h3>
                <p className="text-xs text-amber-700 mt-1">
                  Make sure your backend server is running on <strong>{apiUrl}</strong> by typing:{" "}
                  <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">python run.py</code> in the backend folder.
                </p>
              </div>
            </div>
          ) : (
            <div className="rounded-xl bg-blue-50 border border-blue-200 p-4 flex items-center gap-3 text-blue-800 text-sm">
              <Loader2 className="h-5 w-5 animate-spin shrink-0 text-blue-600" />
              <span>Running automated health checks across all modules...</span>
            </div>
          )}
        </div>

        {/* Test Results Table */}
        <Card className="mt-6 p-0 overflow-hidden border-gray-200 shadow-xs">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-600">
              Module & Endpoint
            </span>
            <div className="flex items-center gap-4 text-xs font-medium text-gray-500">
              <span>Passed: <strong className="text-emerald-600">{passedCount}</strong></span>
              <span>Failed: <strong className="text-red-600">{failedCount}</strong></span>
              <span>Total: <strong>{totalCount}</strong></span>
            </div>
          </div>

          <div className="divide-y divide-gray-100 bg-white">
            {results.map((r) => {
              const isExpanded = expandedId === r.id;
              return (
                <div key={r.id} className="transition-colors hover:bg-gray-50/50">
                  <div
                    className="flex items-center justify-between p-4 cursor-pointer select-none"
                    onClick={() => setExpandedId(isExpanded ? null : r.id)}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {r.status === "passed" && <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />}
                      {r.status === "failed" && <XCircle className="h-5 w-5 text-red-500 shrink-0" />}
                      {r.status === "running" && <Loader2 className="h-5 w-5 text-brand-blue animate-spin shrink-0" />}
                      {r.status === "idle" && <div className="h-5 w-5 rounded-full border border-gray-300 shrink-0" />}

                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-gray-900 truncate">{r.name}</p>
                          <span className="text-[10px] uppercase font-bold tracking-wider rounded px-1.5 py-0.5 bg-gray-100 text-gray-600">
                            {r.category}
                          </span>
                        </div>
                        <p className="text-xs font-mono text-gray-400 mt-0.5">
                          <span className="font-bold text-gray-600">{r.method}</span> {r.endpoint}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      {r.latencyMs !== undefined && (
                        <span className="text-xs font-mono text-gray-400">{r.latencyMs}ms</span>
                      )}

                      {r.status === "passed" && (
                        <span className="inline-flex items-center rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                          {r.httpStatus || 200} OK
                        </span>
                      )}

                      {r.status === "failed" && (
                        <span className="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20">
                          FAILED
                        </span>
                      )}

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          runSingleTest(r.id);
                        }}
                        className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600"
                        title="Re-test"
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                      </button>

                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded JSON Inspector */}
                  {isExpanded && (
                    <div className="bg-gray-900 text-emerald-400 p-4 font-mono text-xs overflow-x-auto border-t border-gray-800">
                      {r.error ? (
                        <div className="text-red-400 font-bold">Error: {r.error}</div>
                      ) : (
                        <pre>{JSON.stringify(r.details, null, 2)}</pre>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>

        {/* Direct Links Footer */}
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 text-xs text-gray-500 pt-4 border-t border-gray-200">
          <p>TaxEaseLK CIT & Auditing Platform • Local Diagnostic Page</p>
          <div className="flex items-center gap-4">
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-semibold text-brand-blue hover:underline"
            >
              Open FastAPI Swagger Docs <ExternalLink className="h-3 w-3" />
            </a>
            <Link href="/sign-in" className="font-semibold text-brand-blue hover:underline">
              Go to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
