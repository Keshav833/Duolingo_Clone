"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { Course, Skill, User } from "@/lib/types";

type IconName = "learn" | "leaderboard" | "quest" | "shop" | "profile" | "more" | "fire" | "gem" | "heart" | "book" | "lock" | "star";

function Icon({ name, className = "" }: { name: IconName; className?: string }) {
  const paths: Record<IconName, ReactNode> = {
    learn: <><path d="m3 10 9-7 9 7v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-9Z" fill="#ff4b4b"/><path d="M6 11h12v10H6z" fill="#ffc800"/><path d="M9.5 21v-5h5v5" fill="#ff9f1c"/></>,
    leaderboard: <><path d="M4 4h16v16H4z" rx="3" fill="#ffd11a"/><path d="M4 4h16l-8 9Z" fill="#ffef70"/><path d="M8 20h8l4-7H4Z" fill="#ffb000"/></>,
    quest: <><path d="M5 5h14v14H5z" rx="3" fill="#ffbf00"/><path d="M9 9h6v6H9z" rx="1" fill="#fff3b0"/><path d="M12 10.5v3M10.5 12h3" stroke="#b77900" strokeWidth="1.7" strokeLinecap="round"/></>,
    shop: <><path d="M4 9h16v11H4z" rx="2" fill="#51a7ee"/><path d="M3 7h18l-2-4H5Z" fill="#ff4b4b"/><path d="M12 3v17" stroke="#fff" strokeWidth="2"/><path d="M4 9h16" stroke="#fff" strokeWidth="2"/></>,
    profile: <><circle cx="12" cy="12" r="9" fill="#c7c7c7"/><circle cx="12" cy="9" r="3" fill="#fff"/><path d="M6.8 18c1.2-3.8 7.2-3.8 8.4 0" fill="#fff"/></>,
    more: <><circle cx="12" cy="12" r="10" fill="#b76cf2"/><circle cx="7.5" cy="12" r="1.4" fill="white"/><circle cx="12" cy="12" r="1.4" fill="white"/><circle cx="16.5" cy="12" r="1.4" fill="white"/></>,
    fire: <><path d="M12 22c4.1 0 7-2.9 7-7.1 0-3.2-2.2-5.4-4.5-7.9.2 2.4-1.2 3.7-2.6 4.6C12.1 7.8 9.5 5.5 8 3c-2.8 3.2-3 6.7-3 9.3C5 18.1 8 22 12 22Z" fill="#ff9600"/><path d="M12 20c2.1 0 3.6-1.5 3.6-3.7 0-1.5-.9-2.8-2.1-3.8-.1 1.5-.8 2.1-1.7 2.7-.4-1.3-1.3-2.2-2.2-2.9-.8 1.1-1.1 2.2-1.1 3.4C8.5 18.2 10 20 12 20Z" fill="#ffdc00"/></>,
    gem: <><path d="m12 3 8 5v8l-8 5-8-5V8l8-5Z" fill="#1cb0f6"/><path d="m12 3 8 5-8 5-8-5 8-5Z" fill="#63d4ff"/></>,
    heart: <path d="M12 20.5 4.5 13C1.7 10.2 2.3 5.5 6.2 4.3c2-.6 4.2.1 5.8 2 1.6-1.9 3.8-2.6 5.8-2C21.7 5.5 22.3 10.2 19.5 13Z" fill="#ff4b4b"/>,
    book: <><rect x="4" y="3" width="15" height="18" rx="3" fill="#fff"/><path d="M8 8h7M8 12h7M8 16h5" stroke="#58cc02" strokeWidth="2" strokeLinecap="round"/><path d="M4 6H2m2 5H2m2 5H2" stroke="#58cc02" strokeWidth="2" strokeLinecap="round"/></>,
    lock: <><rect x="5" y="10" width="14" height="11" rx="3" fill="#aeb7bf"/><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="#aeb7bf" strokeWidth="3"/><circle cx="12" cy="15.5" r="1.5" fill="#7d8790"/></>,
    star: <path d="m12 2.8 2.7 5.6 6.2.9-4.5 4.4 1.1 6.2-5.5-3-5.5 3 1.1-6.2-4.5-4.4 6.2-.9Z" fill="currentColor"/>,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true" className={className}>{paths[name]}</svg>;
}

const navItems: { label: string; icon: IconName; href: string }[] = [
  { label: "Learn", icon: "learn", href: "/" },
  { label: "Leaderboards", icon: "leaderboard", href: "/leaderboard" },
  { label: "Quests", icon: "quest", href: "/" },
  { label: "Shop", icon: "shop", href: "/" },
  { label: "Profile", icon: "profile", href: "/profile" },
  { label: "More", icon: "more", href: "/" },
];

function SkillNode({ skill, index }: { skill: Skill; index: number }) {
  const locked = skill.status === "locked";
  const completed = skill.status === "completed";
  const offset = index % 2 === 0 ? "mr-16" : "ml-16";
  const node = (
    <div className={`group relative flex flex-col items-center ${offset}`}>
      <div className={`relative grid h-24 w-24 place-items-center rounded-full border-[7px] border-white shadow-[0_7px_0_#a8a8a8] transition-transform ${locked ? "bg-slate-200 text-slate-400 shadow-[0_7px_0_#b6b6b6]" : completed ? "bg-amber-400 text-white shadow-[0_7px_0_#d99500]" : "bg-[#58cc02] text-white shadow-[0_7px_0_#46a302] group-hover:-translate-y-1"}`}>
        <Icon name={locked ? "lock" : "star"} className="h-12 w-12" />
      </div>
      <span className={`mt-5 text-sm font-extrabold uppercase tracking-wide ${locked ? "text-slate-400" : "text-slate-600"}`}>{skill.title}</span>
      {!locked && <span className="mt-1 text-xs font-bold text-slate-400">{skill.lessons_completed} lessons</span>}
    </div>
  );
  return locked ? node : <Link href={`/skill/${skill.id}`} aria-label={`Open ${skill.title}`}>{node}</Link>;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [userData, courseData] = await Promise.all([apiFetch<User>("/api/me"), apiFetch<Course>("/api/course")]);
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

  if (loading) return <main className="grid min-h-screen place-items-center bg-white font-bold text-slate-500">Loading your learning path...</main>;
  if (error || !user || !course) return <main className="grid min-h-screen place-items-center bg-white font-bold text-slate-500">{error ?? "Something went wrong."}</main>;

  const skills = course.units.flatMap((unit) => unit.skills);
  const currentSkill = skills.find((skill) => skill.status === "available") ?? skills[0];

  return (
    <main className="min-h-screen bg-white text-[#3c3c3c]">
      <aside className="fixed inset-y-0 hidden w-80 border-r-2 border-slate-100 bg-white px-6 py-11 lg:block">
        <Link href="/" className="mb-11 block text-4xl font-black tracking-tight text-[#58cc02]">lingua</Link>
        <nav className="space-y-3">
          {navItems.map((item, index) => <Link key={item.label} href={item.href} className={`flex items-center gap-5 rounded-2xl border-2 px-6 py-4 text-lg font-extrabold uppercase tracking-wide ${index === 0 ? "border-[#84d8ff] bg-[#ddf4ff] text-[#1cb0f6]" : "border-transparent text-[#6f7780] hover:bg-slate-50"}`}><Icon name={item.icon} className="h-8 w-8" />{item.label}</Link>)}
        </nav>
      </aside>

      <div className="lg:ml-80">
        <header className="flex h-24 items-center justify-between border-b-2 border-slate-100 px-6 md:px-10">
          <div className="flex items-center gap-3 lg:hidden"><span className="text-3xl font-black text-[#58cc02]">lingua</span></div>
          <div className="hidden md:flex items-center gap-2 rounded-lg bg-[#ff4b4b] px-3 py-2 font-black text-white"><span className="h-4 w-6 rounded-sm bg-[#ffdf37]" />SPANISH</div>
          <div className="ml-auto flex items-center gap-5 sm:gap-8">
            <span className="flex items-center gap-2 font-extrabold text-[#ff9600]"><Icon name="fire" className="h-8 w-8" />{user.stats.streak_count}</span>
            <span className="hidden sm:flex items-center gap-2 font-extrabold text-[#1cb0f6]"><Icon name="gem" className="h-8 w-8" />{user.stats.xp_total}</span>
            <span className="flex items-center gap-2 font-extrabold text-[#ff4b4b]"><Icon name="heart" className="h-8 w-8" />{user.stats.hearts}</span>
          </div>
        </header>

        <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-12 px-6 py-8 xl:grid-cols-[minmax(0,1fr)_350px] xl:px-10">
          <section className="min-w-0">
            <div className="rounded-3xl bg-[#58cc02] px-7 py-6 text-white shadow-[0_6px_0_#46a302] sm:flex sm:items-center sm:justify-between">
              <div><p className="mb-2 text-sm font-extrabold uppercase tracking-wide text-[#d7ffb8]">Section {course.units[0]?.order ?? 1}, Unit {course.units[0]?.order ?? 1}</p><h1 className="text-3xl font-black">{course.name}</h1></div>
              <button className="mt-5 flex items-center gap-3 rounded-2xl border-[3px] border-[#46a302] bg-[#58cc02] px-5 py-3 text-base font-extrabold uppercase sm:mt-0"><Icon name="book" className="h-8 w-8" />Guidebook</button>
            </div>
            <div className="relative mx-auto flex min-h-[590px] max-w-md flex-col items-center gap-12 py-16 before:absolute before:top-24 before:h-[360px] before:w-3 before:rounded-full before:bg-slate-100">
              <div className="relative z-10 text-center"><div className="mb-3 rounded-2xl border-2 border-slate-200 bg-white px-5 py-3 text-lg font-extrabold uppercase text-[#58cc02] shadow-sm">Start</div><div className="mx-auto -mt-3 h-5 w-5 rotate-45 border-r-2 border-b-2 border-slate-200 bg-white" /></div>
              {skills.map((skill, index) => <div key={skill.id} className="relative z-10"><SkillNode skill={skill} index={index} /></div>)}
            </div>
          </section>

          <aside className="space-y-6">
            <section className="rounded-3xl border-2 border-slate-200 p-7"><span className="inline-flex rounded-md bg-gradient-to-r from-[#2ce3ff] to-[#bc59f2] px-3 py-1 text-sm font-black italic text-white">SUPER</span><h2 className="mt-5 text-2xl font-black">Learn more, faster</h2><p className="mt-3 text-lg font-medium leading-relaxed text-slate-500">Practice without limits and keep your learning streak going.</p><button className="mt-6 w-full rounded-2xl bg-[#4c4cff] py-4 font-extrabold uppercase tracking-wide text-white shadow-[0_5px_0_#3535ce]">Try 1 week free</button></section>
            <section className="rounded-3xl border-2 border-slate-200 p-7"><h2 className="text-2xl font-black">Daily quests</h2><div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full w-2/3 rounded-full bg-[#ffbf00]" /></div><p className="mt-3 font-bold text-slate-500">Keep going to earn more rewards!</p></section>
            <section className="rounded-3xl border-2 border-slate-200 p-7"><h2 className="text-2xl font-black">{currentSkill.title}</h2><p className="mt-2 font-bold text-slate-500">Your next lesson is ready.</p><Link href={`/skill/${currentSkill.id}`} className="mt-5 inline-flex rounded-xl bg-[#1cb0f6] px-5 py-3 font-extrabold uppercase text-white shadow-[0_4px_0_#168ac2]">Continue</Link></section>
          </aside>
        </div>
      </div>
    </main>
  );
}
