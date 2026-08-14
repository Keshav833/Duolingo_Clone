"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { SkillLessonsResponse, User } from "@/lib/types";

export default function SkillPage() {
  const params = useParams<{ skillId: string }>();
  const router = useRouter();
  const skillId = params.skillId;

  const [data, setData] = useState<SkillLessonsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Which lesson's Start button is currently checking hearts (per-button
  // loading state, not a global "am I busy" flag).
  const [checkingLessonId, setCheckingLessonId] = useState<number | null>(null);
  const [heartsCheckError, setHeartsCheckError] = useState<string | null>(null);
  const [outOfHearts, setOutOfHearts] = useState(false);

  useEffect(() => {
    async function loadSkill() {
      try {
        const result = await apiFetch<SkillLessonsResponse>(
          `/api/skills/${skillId}/lessons`
        );
        setData(result);
      } catch (err) {
        console.error(err);
        setError("Could not load this skill.");
      } finally {
        setLoading(false);
      }
    }

    loadSkill();
  }, [skillId]);

  async function handleStartClick(lessonId: number) {
    setCheckingLessonId(lessonId);
    setHeartsCheckError(null);

    try {
      // Always fetch fresh here rather than trusting any hearts value
      // held in component state from an earlier point in time.
      const user = await apiFetch<User>("/api/me");

      if (user.stats.hearts > 0) {
        router.push(`/lesson/${lessonId}`);
        return; // keep checkingLessonId set through navigation
      }

      setOutOfHearts(true);
    } catch (err) {
      console.error(err);
      setHeartsCheckError("Could not check your hearts. Try again.");
    } finally {
      setCheckingLessonId(null);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>{error ?? "Something went wrong."}</p>
      </main>
    );
  }

  const { skill, lessons } = data;

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-2xl font-bold text-green-600">
            Duolingo Clone
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-3xl px-6 py-10">
        <div className="mb-10 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-4xl">
            {skill.icon}
          </div>

          <div>
            <h2 className="text-3xl font-bold text-slate-900">
              {skill.title}
            </h2>

            <div className="mt-1 flex items-center gap-4 text-sm text-slate-500">
              <span className="capitalize">{skill.status}</span>
              <span>{"👑".repeat(skill.crowns)}</span>
              <span>{skill.lessons_completed} lessons completed</span>
            </div>
          </div>
        </div>

        {heartsCheckError && (
          <p className="mb-4 text-sm font-semibold text-red-600">
            {heartsCheckError}
          </p>
        )}

        <div className="space-y-4">
          {lessons.map((lesson) => (
            <div
              key={lesson.id}
              className="flex items-center justify-between rounded-2xl border border-green-200 bg-white p-5 shadow-sm"
            >
              <div>
                <p className="font-bold text-slate-900">
                  Lesson {lesson.order}
                </p>
                <p className="text-sm text-slate-500">
                  {lesson.xp_reward} XP
                </p>
              </div>

              <button
                onClick={() => handleStartClick(lesson.id)}
                disabled={checkingLessonId === lesson.id}
                className="rounded-xl bg-green-600 px-5 py-2 font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {checkingLessonId === lesson.id ? "Checking..." : "Start"}
              </button>
            </div>
          ))}
        </div>
      </section>

      {outOfHearts && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 px-6">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-lg">
            <p className="mb-2 text-3xl">💔</p>
            <h3 className="mb-2 text-xl font-bold text-slate-900">
              You're out of hearts
            </h3>
            <p className="mb-6 text-sm text-slate-500">
              You need at least 1 heart to start a lesson.
            </p>

            <div className="flex flex-col gap-3">
              <Link
                href="/"
                className="rounded-xl bg-green-600 px-5 py-2 font-semibold text-white hover:bg-green-700"
              >
                Back to Dashboard
              </Link>
              <button
                onClick={() => setOutOfHearts(false)}
                className="rounded-xl px-5 py-2 font-semibold text-slate-500 hover:text-slate-700"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}