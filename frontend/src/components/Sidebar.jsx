const DIFF_ICON = { easy: "🟢", medium: "🟡", hard: "🔴" };
const DIFF_ORDER = ["easy", "medium", "hard"];

export default function Sidebar({ challenges, selectedId, solved, onSelect }) {
  const byDiff = {};
  for (const ch of challenges) {
    (byDiff[ch.difficulty] ??= []).push(ch);
  }

  const total = challenges.length;
  const solvedCount = [...solved].filter((id) =>
    challenges.some((c) => c.id === id)
  ).length;
  const pct = total > 0 ? (solvedCount / total) * 100 : 0;

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
              const isActive = ch.id === selectedId;
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
        <p>
          {solvedCount} / {total} solved
        </p>
      </div>
    </aside>
  );
}
