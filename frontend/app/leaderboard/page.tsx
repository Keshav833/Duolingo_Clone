"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Leaderboard } from "@/lib/types";

function Trophy({ color }: { color: string }) { return <svg viewBox="0 0 24 24" aria-hidden="true" className="h-8 w-8"><path d="M7 3h10v5a5 5 0 0 1-10 0V3Z" fill={color}/><path d="M7 5H3v2a4 4 0 0 0 4 4m10-6h4v2a4 4 0 0 1-4 4M12 13v5m-4 3h8" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round"/></svg>; }

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { async function load() { try { setLeaderboard(await apiFetch<Leaderboard>("/api/leaderboard")); } catch (err) { console.error(err); setError("Could not load the leaderboard."); } finally { setLoading(false); } } load(); }, []);
  if (loading) return <main className="grid min-h-screen place-items-center bg-[#f7f7f7] font-bold text-slate-500">Loading leaderboard...</main>;
  if (error || !leaderboard) return <main className="grid min-h-screen place-items-center bg-[#f7f7f7] font-bold text-slate-500"><div className="text-center"><p>{error ?? "Something went wrong."}</p><Link href="/" className="mt-4 inline-block font-extrabold text-[#58cc02]">Back to dashboard</Link></div></main>;
  const { entries, current_user_rank } = leaderboard;
  const rankColor = (rank: number) => rank === 1 ? "#ffbf00" : rank === 2 ? "#aeb7bf" : rank === 3 ? "#ff9600" : "#1cb0f6";
  return <main className="min-h-screen bg-[#f7f7f7]"><header className="border-b-2 border-slate-100 bg-white"><div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-5"><Link href="/" className="text-3xl font-black tracking-tight text-[#58cc02]">lingua</Link><Link href="/" className="rounded-xl px-4 py-2 text-sm font-extrabold uppercase text-slate-500 hover:bg-slate-50">Back to learn</Link></div></header><section className="mx-auto max-w-2xl px-6 py-12"><div className="mb-8 rounded-3xl bg-[#ffbf00] p-7 text-white shadow-[0_6px_0_#e2a500]"><div className="flex items-center gap-5"><div className="grid h-16 w-16 place-items-center rounded-2xl bg-white/20"><Trophy color="#fff" /></div><div><p className="text-sm font-extrabold uppercase tracking-wide text-[#fff1b3]">Weekly league</p><h1 className="text-3xl font-black">Leaderboard</h1><p className="mt-1 font-bold text-white/90">You&apos;re ranked #{current_user_rank} this week.</p></div></div></div><div className="overflow-hidden rounded-3xl border-2 border-slate-200 bg-white">{entries.map((entry, index) => { const current = entry.rank === current_user_rank; return <div key={entry.rank} className={`flex items-center justify-between px-6 py-5 ${index !== entries.length - 1 ? "border-b-2 border-slate-100" : ""} ${current ? "bg-[#efffdc]" : ""}`}><div className="flex items-center gap-4"><div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-50"><Trophy color={rankColor(entry.rank)} /></div><div><p className={`font-black ${current ? "text-[#46a302]" : "text-slate-700"}`}>{entry.username}{current && <span className="ml-2 rounded-lg bg-[#58cc02] px-2 py-1 text-xs uppercase text-white">You</span>}</p><p className="mt-1 text-sm font-bold text-slate-400">Rank #{entry.rank}</p></div></div><span className="rounded-xl bg-[#ddf4ff] px-4 py-2 font-extrabold text-[#168ac2]">{entry.xp} XP</span></div>; })}</div></section></main>;
}
