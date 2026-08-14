"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await apiFetch<Profile>("/api/profile");
        setProfile(data);
      } catch (err) {
        console.error(err);
        setError("Could not load your profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p>{error ?? "Something went wrong."}</p>
        <Link href="/" className="font-semibold text-green-600">
          Back to Dashboard
        </Link>
      </main>
    );
  }

  const { stats, progress } = profile;
  const dailyXpPct =
    stats.daily_xp_goal > 0
      ? Math.min(100, (stats.daily_xp_earned / stats.daily_xp_goal) * 100)
      : 0;

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

      <section className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="mb-8 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-3xl font-bold text-green-700">
            {profile.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">
              {profile.username}
            </h2>
            <p className="text-sm text-slate-500">Learner profile</p>
          </div>
        </div>

        {/* Stat cards */}
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
            <p className="text-2xl font-bold text-slate-900">
              {stats.xp_total}
            </p>
            <p className="mt-1 text-sm text-slate-500">Total XP</p>
          </div>

          <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
            <p className="text-2xl font-bold text-slate-900">
              🔥 {stats.streak_count}
            </p>
            <p className="mt-1 text-sm text-slate-500">Day streak</p>
          </div>

          <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
            <p className="text-2xl font-bold text-slate-900">
              ❤️ {stats.hearts}/{stats.hearts_max}
            </p>
            <p className="mt-1 text-sm text-slate-500">Hearts</p>
          </div>

          <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
            <p className="text-2xl font-bold text-slate-900">
              {progress.skills_completed}
            </p>
            <p className="mt-1 text-sm text-slate-500">Skills completed</p>
          </div>
        </div>

        {/* Daily XP progress */}
        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-bold text-slate-900">Daily XP goal</h3>
            <p className="text-sm font-semibold text-slate-500">
              {stats.daily_xp_earned} / {stats.daily_xp_goal} XP
            </p>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-green-500 transition-all"
              style={{ width: `${dailyXpPct}%` }}
            />
          </div>
        </div>

        {/* Progress summary */}
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-bold text-slate-900">Progress</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xl font-bold text-slate-900">
                {progress.skills_completed}
              </p>
              <p className="text-sm text-slate-500">Skills completed</p>
            </div>
            <div>
              <p className="text-xl font-bold text-slate-900">
                {progress.lessons_completed}
              </p>
              <p className="text-sm text-slate-500">Lessons completed</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}