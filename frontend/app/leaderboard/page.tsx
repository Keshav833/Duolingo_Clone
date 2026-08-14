"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Leaderboard } from "@/lib/types";

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadLeaderboard() {
      try {
        const data = await apiFetch<Leaderboard>("/api/leaderboard");
        setLeaderboard(data);
      } catch (err) {
        console.error(err);
        setError("Could not load the leaderboard.");
      } finally {
        setLoading(false);
      }
    }

    loadLeaderboard();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  if (error || !leaderboard) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p>{error ?? "Something went wrong."}</p>
        <Link href="/" className="font-semibold text-green-600">
          Back to Dashboard
        </Link>
      </main>
    );
  }

  const { entries, current_user_rank } = leaderboard;

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="text-2xl font-bold text-green-600">
            Duolingo Clone
          </Link>
          <Link
            href="/"
            className="text-sm font-semibold text-slate-500 hover:text-slate-700"
          >
            ← Dashboard
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">
            Leaderboard
          </h2>
          <p className="mt-1 text-slate-500">
            Ranked by total XP.{" "}
            {entries.length === 1
              ? "You're the only learner here so far — invite friends to compete!"
              : `You're ranked #${current_user_rank}.`}
          </p>
        </div>

        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          {entries.map((entry, i) => {
            const isCurrentUser = entry.rank === current_user_rank;

            return (
              <div
                key={entry.rank}
                className={`flex items-center justify-between px-5 py-4 ${
                  i !== entries.length - 1 ? "border-b" : ""
                } ${isCurrentUser ? "bg-green-50" : "bg-white"}`}
              >
                <div className="flex items-center gap-4">
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${
                      entry.rank === 1
                        ? "bg-yellow-100 text-yellow-700"
                        : entry.rank === 2
                        ? "bg-slate-200 text-slate-700"
                        : entry.rank === 3
                        ? "bg-orange-100 text-orange-700"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {entry.rank}
                  </span>

                  <span
                    className={`font-semibold ${
                      isCurrentUser ? "text-green-700" : "text-slate-900"
                    }`}
                  >
                    {entry.username}
                    {isCurrentUser && (
                      <span className="ml-2 rounded-full bg-green-600 px-2 py-0.5 text-xs font-bold text-white">
                        You
                      </span>
                    )}
                  </span>
                </div>

                <span className="font-bold text-slate-900">
                  {entry.xp} XP
                </span>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}