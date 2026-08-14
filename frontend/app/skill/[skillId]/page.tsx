"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { SkillLessonsResponse, User } from "@/lib/types";

function StarIcon() {
  return <svg viewBox="0 0 64 64" aria-hidden="true" className="h-11 w-11"><circle cx="32" cy="32" r="30" fill="#1cb0f6"/><path d="m32 14 5.5 11.2 12.4 1.8-9 8.8 2.1 12.4L32 42.5l-11 5.7 2.1-12.4-9-8.8 12.4-1.8Z" fill="#fff"/></svg>;
}

export default function SkillPage() {
  const { skillId } = useParams<{ skillId: string }>();
  const router = useRouter();
  const [data, setData] = useState<SkillLessonsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkingLessonId, setCheckingLessonId] = useState<number | null>(null);
  const [heartsCheckError, setHeartsCheckError] = useState<string | null>(null);
  const [outOfHearts, setOutOfHearts] = useState(false);

  useEffect(() => {
    async function loadSkill() {
      try { setData(await apiFetch<SkillLessonsResponse>(`/api/skills/${skillId}/lessons`)); }
      catch (err) { console.error(err); setError("Could not load this skill."); }
      finally { setLoading(false); }
    }
    loadSkill();
  }, [skillId]);

  async function handleStartClick(lessonId: number) {
    setCheckingLessonId(lessonId); setHeartsCheckError(null);
    try {
      const user = await apiFetch<User>("/api/me");
      if (user.stats.hearts > 0) { router.push(`/lesson/${lessonId}`); return; }
      setOutOfHearts(true);
    } catch (err) { console.error(err); setHeartsCheckError("Could not check your hearts. Try again."); }
    finally { setCheckingLessonId(null); }
  }

  if (loading) return <main className="grid min-h-screen place-items-center bg-[#f7f7f7] font-bold text-slate-500">Loading your skill...</main>;
  if (error || !data) return <main className="grid min-h-screen place-items-center bg-[#f7f7f7] font-bold text-slate-500">{error ?? "Something went wrong."}</main>;
  const { skill, lessons } = data;

  return <main className="min-h-screen bg-[#f7f7f7]">
    <header className="border-b-2 border-slate-100 bg-white"><div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-5"><Link href="/" className="text-3xl font-black tracking-tight text-[#58cc02]">lingua</Link><Link href="/" className="rounded-xl px-4 py-2 text-sm font-extrabold uppercase text-slate-500 hover:bg-slate-50">Back to learn</Link></div></header>
    <section className="mx-auto max-w-3xl px-6 py-12">
      <div className="mb-10 rounded-3xl bg-[#1cb0f6] p-7 text-white shadow-[0_6px_0_#168ac2]"><div className="flex items-center gap-5"><div className="grid h-16 w-16 place-items-center rounded-2xl bg-white/20"><StarIcon /></div><div><p className="text-sm font-extrabold uppercase tracking-wide text-[#d8f4ff]">Spanish skill</p><h1 className="text-3xl font-black">{skill.title}</h1><p className="mt-2 text-sm font-bold text-white/85"><span className="capitalize">{skill.status}</span> · {skill.crowns} crowns · {skill.lessons_completed} lessons completed</p></div></div></div>
      {heartsCheckError && <p className="mb-5 rounded-2xl bg-[#fff0f0] p-4 font-bold text-[#e53935]">{heartsCheckError}</p>}
      <div className="space-y-5">{lessons.map((lesson) => <article key={lesson.id} className="flex items-center justify-between rounded-3xl border-2 border-slate-200 bg-white p-6 transition-transform hover:-translate-y-0.5"><div><p className="text-lg font-black text-slate-700">Lesson {lesson.order}</p><p className="mt-1 text-sm font-bold text-[#1cb0f6]">+{lesson.xp_reward} XP</p></div><button onClick={() => handleStartClick(lesson.id)} disabled={checkingLessonId === lesson.id} className="rounded-2xl bg-[#58cc02] px-6 py-3 font-extrabold uppercase tracking-wide text-white shadow-[0_4px_0_#46a302] hover:bg-[#62d80a] disabled:cursor-not-allowed disabled:opacity-60">{checkingLessonId === lesson.id ? "Checking..." : "Start"}</button></article>)}</div>
    </section>
    {outOfHearts && <div className="fixed inset-0 grid place-items-center bg-slate-900/40 px-6"><div className="w-full max-w-sm rounded-3xl bg-white p-7 text-center shadow-xl"><div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-full bg-[#fff0f0]"><svg viewBox="0 0 24 24" className="h-9 w-9"><path d="M12 20.5 4.5 13C1.7 10.2 2.3 5.5 6.2 4.3c2-.6 4.2.1 5.8 2 1.6-1.9 3.8-2.6 5.8-2C21.7 5.5 22.3 10.2 19.5 13Z" fill="#ff4b4b"/></svg></div><h2 className="text-2xl font-black text-slate-700">You&apos;re out of hearts</h2><p className="mt-2 text-slate-500">You need at least one heart to start a lesson.</p><Link href="/" className="mt-6 block rounded-2xl bg-[#58cc02] px-5 py-3 font-extrabold uppercase text-white shadow-[0_4px_0_#46a302]">Back to dashboard</Link><button onClick={() => setOutOfHearts(false)} className="mt-4 font-extrabold uppercase text-slate-500">Dismiss</button></div></div>}
  </main>;
}
