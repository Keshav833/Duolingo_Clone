"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Course, User } from "@/lib/types";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [userData, courseData] = await Promise.all([
          apiFetch<User>("/api/me"),
          apiFetch<Course>("/api/course"),
        ]);

        setUser(userData);
        setCourse(courseData);
      } catch (err) {
        console.error(err);
        setError("Could not connect to the API.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  if (error || !user || !course) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>{error ?? "Something went wrong."}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center justify-between gap-6 sm:justify-start">
            <h1 className="text-2xl font-bold text-green-600">
              Duolingo Clone
            </h1>

            <nav className="flex items-center gap-4 text-sm font-semibold text-slate-500 sm:ml-6">
              <Link href="/profile" className="hover:text-green-600">
                Profile
              </Link>
              <Link href="/leaderboard" className="hover:text-green-600">
                Leaderboard
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-6 text-sm font-semibold">
            <span>🔥 {user.stats.streak_count}</span>
            <span>💎 500</span>
            <span>
              ❤️ {user.stats.hearts}/{user.stats.hearts_max}
            </span>
            <span>⭐ {user.stats.xp_total} XP</span>
          </div>
        </div>
      </header>

      {/* Course */}
      <section className="mx-auto max-w-3xl px-6 py-10">
        <div className="mb-10">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            {course.language}
          </p>

          <h2 className="mt-1 text-3xl font-bold text-slate-900">
            {course.name}
          </h2>

          <p className="mt-2 text-slate-500">
            Continue your Spanish learning journey.
          </p>
        </div>

        {/* Units */}
        <div className="space-y-12">
          {course.units.map((unit) => (
            <section key={unit.id}>
              <div className="mb-5">
                <h3 className="text-xl font-bold text-slate-800">
                  Unit {unit.order}: {unit.title}
                </h3>
              </div>

              <div className="space-y-4">
                {unit.skills.map((skill) => {
                  const locked = skill.status === "locked";
                  const completed = skill.status === "completed";

                  const cardContent = (
                    <div
                      className={`rounded-2xl border bg-white p-5 shadow-sm ${
                        locked ? "opacity-60" : "border-green-200"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-3xl">
                            {skill.icon}
                          </div>

                          <div>
                            <h4 className="text-lg font-bold text-slate-900">
                              {skill.title}
                            </h4>

                            <p className="text-sm text-slate-500">
                              {skill.lessons_completed} lessons completed
                            </p>
                          </div>
                        </div>

                        <div className="text-right">
                          {completed && (
                            <p className="font-semibold text-green-600">
                              Completed
                            </p>
                          )}

                          {locked && (
                            <p className="text-sm font-semibold text-slate-500">
                              🔒 Locked
                            </p>
                          )}

                          {!locked && (
                            <p className="mt-1 text-sm">
                              {"👑".repeat(skill.crowns)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );

                  if (locked) {
                    return <div key={skill.id}>{cardContent}</div>;
                  }

                  return (
                    <Link key={skill.id} href={`/skill/${skill.id}`} className="block">
                      {cardContent}
                    </Link>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </section>
    </main>
  );
}