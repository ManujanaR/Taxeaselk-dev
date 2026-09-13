"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, X } from "lucide-react";

type Toast = { id: number; kind: "success" | "error"; text: string };
const listeners = new Set<(t: Toast) => void>();
let seq = 0;

function emit(kind: Toast["kind"], text: string) {
  const t = { id: ++seq, kind, text };
  listeners.forEach((l) => l(t));
}

// toast.success("Saved") / toast.error(err.message) from any client component.
export const toast = { success: (text: string) => emit("success", text), error: (text: string) => emit("error", text) };

export function errorMessage(e: unknown): string {
  return e instanceof Error ? e.message : "Something went wrong";
}

export function Toaster() {
  const [items, setItems] = useState<Toast[]>([]);
  useEffect(() => {
    const add = (t: Toast) => {
      setItems((xs) => [...xs, t]);
      setTimeout(() => setItems((xs) => xs.filter((x) => x.id !== t.id)), t.kind === "error" ? 6000 : 3500);
    };
    listeners.add(add);
    return () => void listeners.delete(add);
  }, []);
  if (!items.length) return null;
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-80 flex-col gap-2">
      {items.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`pointer-events-auto flex items-start gap-2 rounded-lg border px-3 py-2.5 text-sm shadow-lg ${
            t.kind === "success" ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-red-200 bg-red-50 text-red-700"
          }`}
        >
          {t.kind === "success" ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" /> : <XCircle className="mt-0.5 h-4 w-4 shrink-0" />}
          <span className="flex-1">{t.text}</span>
          <button onClick={() => setItems((xs) => xs.filter((x) => x.id !== t.id))} aria-label="Dismiss" className="opacity-60 hover:opacity-100">
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
