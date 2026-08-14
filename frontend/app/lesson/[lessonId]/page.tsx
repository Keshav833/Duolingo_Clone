"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type {
  Lesson,
  User,
  SubmittedAnswer,
  AnswerSubmitResponse,
  CompleteLessonResponse,
  Exercise,
} from "@/lib/types";
import ExerciseRenderer from "./ExerciseRenderer";

function isAnswerValid(exercise: Exercise, answer: SubmittedAnswer | null): boolean {
  if (answer === null) return false;

  switch (exercise.type) {
    case "multiple_choice":
      return typeof answer === "string" && answer.length > 0;
    case "translate":
      return Array.isArray(answer) && answer.length > 0;
    case "match_pairs": {
      if (typeof answer !== "object" || Array.isArray(answer)) return false;
      const pairCount = exercise.options?.pairs.length ?? 0;
      return pairCount > 0 && Object.keys(answer).length === pairCount;
    }
    case "fill_blank":
    case "type_answer":
      return typeof answer === "string" && answer.trim().length > 0;
    default:
      return false;
  }
}

function formatCorrectAnswer(value: SubmittedAnswer): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.join(" ");
  return Object.entries(value)
    .map(([k, v]) => `${k} → ${v}`)
    .join(", ");
}

export default function LessonPage() {
  const params = useParams<{ lessonId: string }>();
  const lessonId = params.lessonId;

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState<SubmittedAnswer | null>(null);
  const [feedback, setFeedback] = useState<AnswerSubmitResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [hearts, setHearts] = useState<number | null>(null);

  const [completing, setCompleting] = useState(false);
  const [completionResult, setCompletionResult] =
    useState<CompleteLessonResponse | null>(null);
  const [completionError, setCompletionError] = useState<string | null>(null);

  useEffect(() => {
    async function loadLesson() {
      try {
        const [lessonData, userData] = await Promise.all([
          apiFetch<Lesson>(`/api/lessons/${lessonId}`),
          apiFetch<User>("/api/me"),
        ]);
        setLesson(lessonData);
        setUser(userData);
        setHearts(userData.stats.hearts);
      } catch (err) {
        console.error(err);
        setLoadError("Could not load this lesson.");
      } finally {
        setLoading(false);
      }
    }

    loadLesson();
  }, [lessonId]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  if (loadError || !lesson || !user || hearts === null) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p>{loadError ?? "Something went wrong."}</p>
        <Link href="/" className="font-semibold text-green-600">
          Back to Dashboard
        </Link>
      </main>
    );
  }

  const total = lesson.exercises.length;
  const currentExercise = lesson.exercises[currentIndex];
  const isLastExercise = currentIndex >= total - 1;

  // Authoritative failure condition: backend said this answer was wrong
  // AND the backend's own returned hearts value is 0. Nothing else can
  // derive "out of hearts" — never computed client-side from a counter.
  const outOfHearts = feedback !== null && !feedback.correct && hearts === 0;

  async function handleCheck() {
    if (!currentExercise || answer === null || submitting) return;

    setSubmitting(true);
    setSubmitError(null);

    try {
      const result = await apiFetch<AnswerSubmitResponse>(
        `/api/lessons/${lessonId}/answer`,
        {
          method: "POST",
          body: JSON.stringify({
            exercise_id: currentExercise.id,
            submitted_answer: answer,
          }),
        }
      );
      setFeedback(result);
      setHearts(result.hearts);
    } catch (err) {
      console.error(err);
      setSubmitError("Could not submit your answer. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCompleteLesson() {
    if (completing || completionResult) return; // guards duplicate completion calls

    setCompleting(true);
    setCompletionError(null);

    try {
      const result = await apiFetch<CompleteLessonResponse>(
        `/api/lessons/${lessonId}/complete`,
        { method: "POST" }
      );
      setCompletionResult(result);
    } catch (err) {
      console.error(err);
      setCompletionError("Could not complete this lesson. Try again.");
    } finally {
      setCompleting(false);
    }
  }

  function handleContinue() {
    // Correct-only path. Wrong answers never reach this handler — the
    // button that calls it renders "Try Again" and calls handleRetry
    // instead whenever feedback.correct is false (see render below).
    if (!feedback || !feedback.correct) return;

    if (isLastExercise) {
      handleCompleteLesson();
      return;
    }

    setCurrentIndex((i) => i + 1);
    setAnswer(null);
    setFeedback(null);
    setSubmitError(null);
  }

  function handleRetry() {
    // Resets the CURRENT exercise only. Never advances currentIndex.
    setAnswer(null);
    setFeedback(null);
    setSubmitError(null);
  }

  // --- Out-of-hearts failure screen: no Continue, no Try Again, no path
  // to /complete. Only way out is back to the dashboard. ---
  if (outOfHearts) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-5 bg-[#f7f7f7] px-6 py-10">
        <p className="text-3xl">💔</p>
        <h2 className="text-2xl font-bold text-slate-900">Out of hearts</h2>
        <p className="text-center text-slate-500">
          You&apos;ve run out of hearts for this lesson. Come back later to try again.
        </p>
        <Link
          href="/"
          className="mt-2 rounded-xl bg-green-600 px-6 py-2 font-semibold text-white hover:bg-green-700"
        >
          Back to Dashboard
        </Link>
      </main>
    );
  }

  // --- Completion screen (only reachable after a real /complete call,
  // which only ever fires from handleContinue on a correct final answer) ---
  if (completing || completionResult || completionError) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-6">
        {completing && <div className="rounded-3xl border-2 border-slate-200 bg-white px-8 py-6 text-center shadow-sm"><div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-[#d7ffb8] border-t-[#58cc02]" /><p className="font-extrabold text-slate-600">Saving your progress...</p></div>}

        {completionError && !completing && (
          <>
            <p className="font-semibold text-red-600">{completionError}</p>
            <button
              onClick={handleCompleteLesson}
              className="rounded-xl bg-green-600 px-6 py-2 font-semibold text-white hover:bg-green-700"
            >
              Retry
            </button>
            <Link href="/" className="font-semibold text-slate-500">
              Back to Dashboard
            </Link>
          </>
        )}

        {completionResult && !completing && (
          <div className="completion-card w-full max-w-md rounded-3xl border-2 border-slate-200 bg-white p-7 text-center shadow-sm">
            <p className="mb-2 text-3xl">🎉</p>
            <div className="mx-auto mb-4 grid h-20 w-20 place-items-center rounded-full bg-[#efffdc]"><svg viewBox="0 0 24 24" className="h-11 w-11 text-[#58cc02]" aria-hidden="true"><path d="m12 2.8 2.7 5.6 6.2.9-4.5 4.4 1.1 6.2-5.5-3-5.5 3 1.1-6.2-4.5-4.4 6.2-.9Z" fill="currentColor"/></svg></div>
            <h2 className="mb-2 text-3xl font-black text-slate-700">
              Lesson complete!
            </h2>

            <p className="font-bold text-slate-500">Great work! Here&apos;s what you earned.</p>
            <div className="mt-6 space-y-3 text-left text-sm">
              <p className="flex justify-between">
                <span className="text-slate-500">XP earned</span>
                <span className="font-bold text-slate-900">
                  {completionResult.already_completed
                    ? "0 (already completed)"
                    : `+${completionResult.xp_earned}`}
                </span>
              </p>
              <p className="flex justify-between">
                <span className="text-slate-500">Total XP</span>
                <span className="font-bold text-slate-900">
                  {completionResult.total_xp}
                </span>
              </p>
              <p className="flex justify-between">
                <span className="text-slate-500">Streak</span>
                <span className="font-bold text-slate-900">
                  🔥 {completionResult.streak}
                </span>
              </p>
              <p className="flex justify-between">
                <span className="text-slate-500">Skill progress</span>
                <span className="font-bold text-slate-900">
                  {completionResult.skill.lessons_completed} lessons ·{" "}
                  {"👑".repeat(completionResult.skill.crowns)}
                </span>
              </p>
              <p className="flex justify-between">
                <span className="text-slate-500">Skill status</span>
                <span className="font-bold capitalize text-slate-900">
                  {completionResult.skill.status}
                </span>
              </p>
              {completionResult.unlocked_skill_id !== null && (
                <p className="mt-2 rounded-lg bg-green-50 p-2 text-center font-semibold text-green-700">
                  🔓 New skill unlocked!
                </p>
              )}
            </div>

            <Link
              href="/"
              className="mt-7 block rounded-2xl bg-[#58cc02] px-6 py-4 font-extrabold uppercase tracking-wide text-white shadow-[0_4px_0_#46a302]"
            >
              Back to Dashboard
            </Link>
          </div>
        )}
      </main>
    );
  }

  const progressPct = total > 0 ? ((currentIndex + 1) / total) * 100 : 0;
  const canCheck = isAnswerValid(currentExercise, answer) && !submitting;

  return (
    <main className="min-h-screen bg-[#f7f7f7]">
      <header className="border-b-2 border-slate-100 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-5">
          <Link href="/" aria-label="Exit lesson" className="lesson-exit grid h-11 w-11 place-items-center rounded-2xl border-2 border-slate-200 text-slate-500 hover:border-[#ffb3b3] hover:bg-[#fff0f0] hover:text-[#ff4b4b]">
            ✕ Exit
          </Link>

          <span className="hidden text-sm font-semibold">
            ❤️ {hearts}/{user.stats.hearts_max}
          </span>
          <div className="flex items-center gap-2 rounded-2xl bg-[#fff0f0] px-4 py-2 font-extrabold text-[#ff4b4b]">
            <svg viewBox="0 0 24 24" className="h-7 w-7" aria-hidden="true"><path d="M12 20.5 4.5 13C1.7 10.2 2.3 5.5 6.2 4.3c2-.6 4.2.1 5.8 2 1.6-1.9 3.8-2.6 5.8-2C21.7 5.5 22.3 10.2 19.5 13Z" fill="currentColor" /></svg>
            <span>{hearts}/{user.stats.hearts_max}</span>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-6">
          <p className="mb-3 text-sm font-extrabold uppercase tracking-wide text-slate-500">
            Lesson {lesson.order} · Exercise {currentIndex + 1} of {total}
          </p>
          <div className="h-4 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-[#58cc02] transition-all"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        {currentExercise && (
          <ExerciseRenderer
            key={currentExercise.id}
            exercise={currentExercise}
            answer={answer}
            onAnswerChange={setAnswer}
            disabled={feedback !== null}
          />
        )}

        {feedback && (
          <div
            className={`mt-5 rounded-2xl border-2 p-5 ${
              feedback.correct
                ? "border-[#a5e973] bg-[#efffdc] text-[#46a302]"
                : "border-[#ffb3b3] bg-[#fff0f0] text-[#e53935]"
            }`}
          >
            <p className="font-bold">
              {feedback.correct ? "✓ Correct!" : "✗ Incorrect"}
            </p>
            {!feedback.correct && (
              <p className="mt-1 text-sm">
                Correct answer: {formatCorrectAnswer(feedback.correct_answer)}
              </p>
            )}
          </div>
        )}

        {submitError && (
          <p className="mt-4 text-sm font-semibold text-red-600">
            {submitError}
          </p>
        )}

        <div className="mt-8 flex justify-end">
          {feedback === null && (
            <button
              onClick={handleCheck}
              disabled={!canCheck}
              className="rounded-2xl bg-[#58cc02] px-8 py-4 font-extrabold uppercase tracking-wide text-white shadow-[0_4px_0_#46a302] disabled:cursor-not-allowed disabled:opacity-40"
            >
              {submitting ? "Checking..." : "Check"}
            </button>
          )}

          {feedback !== null && feedback.correct && (
            <button
              onClick={handleContinue}
              className="rounded-2xl bg-[#58cc02] px-8 py-4 font-extrabold uppercase tracking-wide text-white shadow-[0_4px_0_#46a302]"
            >
              Continue
            </button>
          )}

          {feedback !== null && !feedback.correct && !outOfHearts && (
            <button
              onClick={handleRetry}
              className="rounded-2xl bg-[#ff4b4b] px-8 py-4 font-extrabold uppercase tracking-wide text-white shadow-[0_4px_0_#d93c3c]"
            >
              Try Again
            </button>
          )}
        </div>
      </section>
    </main>
  );
}
