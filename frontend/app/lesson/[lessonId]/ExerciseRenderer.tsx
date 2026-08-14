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
    <div className="rounded-3xl border-2 border-slate-200 bg-white p-6 sm:p-9">
      <p className="mb-8 text-2xl font-black text-slate-700">
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
                  ? "border-[#1cb0f6] bg-[#e9f8ff] text-[#168ac2]"
                  : "border-2 border-slate-200 hover:border-[#84d8ff]"
              }`}
            >
              {choice}
            </button>
          ))}
        </div>
      )}

      {exercise.type === "translate" && exercise.options && (
        <div>
          <div className="mb-5 flex min-h-[4rem] flex-wrap gap-2 rounded-2xl border-2 border-dashed border-slate-300 p-4">
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
                className="rounded-xl bg-[#ddf4ff] px-4 py-2 font-bold text-[#168ac2] disabled:opacity-60"
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
                  className="rounded-xl border-2 border-slate-200 px-4 py-2 font-bold shadow-[0_2px_0_#d5d9dc] hover:border-[#84d8ff] disabled:opacity-60"
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
                      ? "border-[#58cc02] bg-[#efffdc] text-[#46a302]"
                      : selectedLeft === left ? "border-[#1cb0f6] bg-[#e9f8ff]" : "border-slate-200 hover:border-[#84d8ff]"
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
                      ? "border-[#58cc02] bg-[#efffdc] text-[#46a302]" : "border-slate-200 hover:border-[#84d8ff]"
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
          className="w-full rounded-2xl border-2 border-slate-200 p-4 text-lg font-bold focus:border-[#1cb0f6] focus:outline-none disabled:opacity-60"
        />
      )}
    </div>
  );
}
