"use client";

import { useState } from "react";
import type { Exercise, SubmittedAnswer } from "@/lib/types";

interface Props {
  exercise: Exercise;
  answer: SubmittedAnswer | null;
  onAnswerChange: (answer: SubmittedAnswer) => void;
  disabled: boolean;
}

export default function ExerciseRenderer({
  exercise,
  answer,
  onAnswerChange,
  disabled,
}: Props) {
  // Only transient, non-submitted UI state stays local (e.g. which left
  // item is highlighted before it's paired). Everything that's part of
  // the actual submitted_answer is owned by the parent so CHECK can read it.
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <p className="mb-6 text-xl font-bold text-slate-900">
        {exercise.question}
      </p>

      {exercise.type === "multiple_choice" && (
        <div className="space-y-3">
          {exercise.options?.choices.map((choice) => (
            <button
              key={choice}
              disabled={disabled}
              onClick={() => onAnswerChange(choice)}
              className={`block w-full rounded-xl border p-3 text-left font-medium disabled:opacity-60 ${
                answer === choice
                  ? "border-green-500 bg-green-50 text-green-700"
                  : "border-slate-200 hover:border-slate-300"
              }`}
            >
              {choice}
            </button>
          ))}
        </div>
      )}

      {exercise.type === "translate" && exercise.options && (
        <div>
          <div className="mb-4 flex min-h-[3rem] flex-wrap gap-2 rounded-xl border border-dashed border-slate-300 p-3">
            {selectedIndices.length === 0 && (
              <span className="text-sm text-slate-400">Tap words below</span>
            )}
            {selectedIndices.map((idx) => (
              <button
                key={idx}
                disabled={disabled}
                onClick={() => {
                  const next = selectedIndices.filter((i) => i !== idx);
                  setSelectedIndices(next);
                  onAnswerChange(next.map((i) => exercise.options!.word_bank[i]));
                }}
                className="rounded-lg bg-green-100 px-3 py-1 font-medium text-green-800 disabled:opacity-60"
              >
                {exercise.options!.word_bank[idx]}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap gap-2">
            {exercise.options.word_bank.map((word, idx) =>
              selectedIndices.includes(idx) ? null : (
                <button
                  key={idx}
                  disabled={disabled}
                  onClick={() => {
                    const next = [...selectedIndices, idx];
                    setSelectedIndices(next);
                    onAnswerChange(next.map((i) => exercise.options!.word_bank[i]));
                  }}
                  className="rounded-lg border border-slate-200 px-3 py-1 font-medium hover:border-slate-300 disabled:opacity-60"
                >
                  {word}
                </button>
              )
            )}
          </div>
        </div>
      )}

      {exercise.type === "match_pairs" && exercise.options && (
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            {exercise.options.pairs.map(([left]) => {
              const matches = (answer as Record<string, string>) ?? {};
              const isMatched = left in matches;
              return (
                <button
                  key={left}
                  disabled={disabled || isMatched}
                  onClick={() => setSelectedLeft(left)}
                  className={`block w-full rounded-xl border p-3 text-left font-medium disabled:opacity-60 ${
                    isMatched
                      ? "border-green-500 bg-green-50 text-green-700"
                      : selectedLeft === left
                      ? "border-blue-500 bg-blue-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  {left}
                </button>
              );
            })}
          </div>

          <div className="space-y-2">
            {exercise.options.pairs.map(([, right]) => {
              const matches = (answer as Record<string, string>) ?? {};
              const alreadyMatched = Object.values(matches).includes(right);
              return (
                <button
                  key={right}
                  disabled={disabled || alreadyMatched || !selectedLeft}
                  onClick={() => {
                    if (!selectedLeft) return;
                    onAnswerChange({ ...matches, [selectedLeft]: right });
                    setSelectedLeft(null);
                  }}
                  className={`block w-full rounded-xl border p-3 text-left font-medium disabled:opacity-60 ${
                    alreadyMatched
                      ? "border-green-500 bg-green-50 text-green-700"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  {right}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {(exercise.type === "fill_blank" || exercise.type === "type_answer") && (
        <input
          type="text"
          disabled={disabled}
          value={(answer as string) ?? ""}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder="Type your answer"
          className="w-full rounded-xl border border-slate-200 p-3 font-medium focus:border-green-500 focus:outline-none disabled:opacity-60"
        />
      )}
    </div>
  );
}