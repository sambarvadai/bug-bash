import { useState } from "react";

const DIFF_ICON = { easy: "🟢", medium: "🟡", hard: "🔴" };
const DIFF_ORDER = ["easy", "medium", "hard"];

function baseId(id) {
  return id.replace(/_(js|ts)$/, "");
}

export default function Sidebar({ challenges, selectedId, solved, onSelect }) {
  // Deduplicate: one entry per base challenge (drop _js / _ts variants)
  const seen = new Set();
  const deduped = challenges.filter((c) => {
    const base = baseId(c.id);
    if (seen.has(base)) return false;
    seen.add(base);
    return true;
  });

  const byDiff = {};
  for (const ch of deduped) {
    (byDiff[ch.difficulty] ??= []).push(ch);
  }

  const total = deduped.length;
  const solvedCount = [...solved].filter((id) =>
    deduped.some((c) => baseId(id) === baseId(c.id))
  ).length;
  const pct = total > 0 ? (solvedCount / total) * 100 : 0;

  // A sidebar item is active if selectedId belongs to the same base group
  const activeBase = baseId(selectedId || "");

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>🐛 Bug Bash</h1>
        <p>Find the bug. Fix it. Pass all tests.</p>
      </div>

      <div className="sidebar-list">
        {DIFF_ORDER.filter((d) => byDiff[d]).map((diff) => (
          <div key={diff}>
            <div className="sidebar-group-label">
              {DIFF_ICON[diff]} {diff}
            </div>
            {byDiff[diff].map((ch) => {
              const isSolved = solved.has(ch.id);
              const isActive = baseId(ch.id) === activeBase;
              return (
                <button
                  key={ch.id}
                  className={`sidebar-item${isActive ? " active" : ""}`}
                  onClick={() => onSelect(ch.id)}
                >
                  {isSolved && <span className="check">✓</span>}
                  <span className="title">{ch.title}</span>
                </button>
              );
            })}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{ width: `${pct}%` }}
          />
        </div>
        <p>{solvedCount} / {total} solved</p>
      </div>
    </aside>
  );
}
