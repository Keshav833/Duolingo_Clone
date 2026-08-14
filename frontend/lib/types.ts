export interface UserStats {
  xp_total: number;
  streak_count: number;
  hearts: number;
  hearts_max: number;
  daily_xp_goal: number;
  daily_xp_earned: number;
}

export interface User {
  id: number;
  username: string;
  stats: UserStats;
}

export interface Skill {
  id: number;
  title: string;
  icon: string | null;
  order: number;
  status: "locked" | "available" | "completed";
  crowns: number;
  lessons_completed: number;
}

export interface Unit {
  id: number;
  title: string;
  order: number;
  skills: Skill[];
}

export interface Course {
  id: number;
  name: string;
  language: string;
  units: Unit[];
}

export interface LessonSummary {
  id: number;
  order: number;
  xp_reward: number;
}

export interface SkillLessonsResponse {
  skill: Skill;
  lessons: LessonSummary[];
}

interface BaseExercise {
  id: number;
  order: number;
  question: string;
}

export interface MultipleChoiceExercise extends BaseExercise {
  type: "multiple_choice";
  options: { choices: string[] } | null;
}

export interface TranslateExercise extends BaseExercise {
  type: "translate";
  options: { word_bank: string[] } | null;
}

export interface MatchPairsExercise extends BaseExercise {
  type: "match_pairs";
  options: { pairs: [string, string][] } | null;
}

export interface FillBlankExercise extends BaseExercise {
  type: "fill_blank";
  options: null;
}

export interface TypeAnswerExercise extends BaseExercise {
  type: "type_answer";
  options: null;
}

export type Exercise =
  | MultipleChoiceExercise
  | TranslateExercise
  | MatchPairsExercise
  | FillBlankExercise
  | TypeAnswerExercise;

export interface Lesson {
  id: number;
  order: number;
  xp_reward: number;
  exercises: Exercise[];
}

export type SubmittedAnswer = string | string[] | Record<string, string>;

export interface AnswerSubmitRequest {
  exercise_id: number;
  submitted_answer: SubmittedAnswer;
}

export interface AnswerSubmitResponse {
  correct: boolean;
  hearts: number;
  correct_answer: SubmittedAnswer;
}

export interface SkillProgress {
  id: number;
  status: "locked" | "available" | "completed";
  crowns: number;
  lessons_completed: number;
}

export interface CompleteLessonResponse {
  lesson_completed: boolean;
  already_completed: boolean;
  xp_earned: number;
  total_xp: number;
  daily_xp_earned: number;
  streak: number;
  skill: SkillProgress;
  unlocked_skill_id: number | null;
}

export interface ProfileProgress {
  skills_completed: number;
  lessons_completed: number;
}

export interface Profile {
  id: number;
  username: string;
  stats: UserStats;
  progress: ProfileProgress;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  xp: number;
}

export interface Leaderboard {
  entries: LeaderboardEntry[];
  current_user_rank: number;
}