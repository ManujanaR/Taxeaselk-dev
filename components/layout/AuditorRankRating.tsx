"use client";

import { useEffect, useRef, useState } from "react";
import { Star, ChevronDown, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api/client";
import { date } from "@/lib/format";

interface ReviewsOut {
  averageRating: number | null;
  totalReviews: number;
  timeliness: number | null;
  communication: number | null;
  technical: number | null;
  completedAudits: number;
  reviews: { id: string; companyName: string; rating: number; comment: string; createdAt: string }[];
}

// Top-bar badge showing the auditor's verified client rating; opens a reputation drawer.
export default function AuditorRankRating() {
  const [data, setData] = useState<ReviewsOut | null>(null);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api<ReviewsOut>("/api/auditor/reviews").then(setData).catch(() => {});
  }, [open]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const rating = data?.averageRating;
  const bars: [string, number | null][] = [
    ["Accuracy", data?.technical ?? null],
    ["Responsiveness", data?.communication ?? null],
    ["Turnaround", data?.timeliness ?? null],
  ];

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-sm font-medium text-amber-800 hover:bg-amber-100"
      >
        <ShieldCheck className="h-4 w-4 text-amber-600" />
        <span>{rating ? "Verified Auditor" : "New Auditor"}</span>
        <span className="flex items-center gap-0.5 font-bold">
          <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-500" />
          {rating ? rating.toFixed(1) : "—"}
        </span>
        <span className="text-xs text-amber-700">({data?.totalReviews ?? 0})</span>
        <ChevronDown className="h-3.5 w-3.5 text-amber-600" />
      </button>

      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 rounded-card border border-gray-100 bg-white p-4 shadow-lg">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Reputation</p>
          <div className="mt-2 flex items-end gap-2">
            <span className="text-3xl font-extrabold text-gray-900">{rating ? rating.toFixed(1) : "—"}</span>
            <span className="pb-1 text-sm text-gray-500">/ 5.0 from {data?.totalReviews ?? 0} client review{data?.totalReviews === 1 ? "" : "s"}</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">{data?.completedAudits ?? 0} audits signed off</p>

          <div className="mt-4 space-y-2">
            {bars.map(([label, v]) => (
              <div key={label}>
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{label}</span>
                  <span className="font-semibold">{v ? `${Math.round((v / 5) * 100)}%` : "—"}</span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-gray-100">
                  <div className="h-1.5 rounded-full bg-amber-400" style={{ width: `${v ? (v / 5) * 100 : 0}%` }} />
                </div>
              </div>
            ))}
          </div>

          {data && data.reviews.length > 0 && (
            <div className="mt-4 max-h-48 space-y-2 overflow-y-auto border-t border-gray-100 pt-3">
              {data.reviews.map((r) => (
                <div key={r.id} className="rounded-lg bg-gray-50 p-2 text-xs">
                  <div className="flex justify-between">
                    <span className="font-semibold text-gray-800">{r.companyName}</span>
                    <span className="text-amber-600">{r.rating} ★</span>
                  </div>
                  {r.comment && <p className="mt-1 text-gray-600">{r.comment}</p>}
                  <p className="mt-1 text-[10px] text-gray-400">{date(r.createdAt)}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
