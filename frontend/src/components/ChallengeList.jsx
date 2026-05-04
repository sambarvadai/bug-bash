import { useState, useMemo } from "react";

const LANG_LABEL = { python: "Py", javascript: "JS", typescript: "TS" };

function baseId(id) {
  return id.replace(/_(js|ts)$/, "");
}

export default function ChallengeList({ challenges, solved, onSelect }) {
  const [filter, setFilter] = useState("all");

  const rows = useMemo(() => {
    const groups = {};
    for (const c of challenges) {
      const base = baseId(c.id);
      if (!groups[base]) groups[base] = { primary: c, langs: [] };
      groups[base].langs.push(c.language || "python");
      if (!c.id.endsWith("_js") && !c.id.endsWith("_ts")) {
        groups[base].primary = c;
      }
    }
    return Object.values(groups);
  }, [challenges]);

  const difficulties = ["all", "easy", "medium", "hard"];
  const visible = filter === "all" ? rows : rows.filter((r) => r.primary.difficulty === filter);

  const counts = useMemo(() => {
    const c = { easy: 0, medium: 0, hard: 0 };
    rows.forEach((r) => c[r.primary.difficulty]++);
    return c;
  }, [rows]);

  const solvedCount = rows.filter((r) => solved.has(r.primary.id)).length;

  return (
    <div className="cl-page">
      <div className="cl-header">
        <div className="cl-title-row">
          <h1 className="cl-title">Challenges</h1>
          <span className="cl-progress">
            {solvedCount} / {rows.length} solved
          </span>
        </div>

        <div className="cl-tabs">
          {difficulties.map((d) => (
            <button
              key={d}
              className={`cl-tab${filter === d ? " active" : ""}${d !== "all" ? ` cl-tab-${d}` : ""}`}
              onClick={() => setFilter(d)}
            >
              {d === "all" ? "All" : d.charAt(0).toUpperCase() + d.slice(1)}
              {d !== "all" && (
                <span className="cl-tab-count">{counts[d]}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="cl-table">
        <div className="cl-table-head">
          <span className="cl-col-status" />
          <span className="cl-col-title">Title</span>
          <span className="cl-col-category">Category</span>
          <span className="cl-col-langs">Languages</span>
          <span className="cl-col-diff">Difficulty</span>
        </div>

        {visible.map((row) => {
          const { primary, langs } = row;
          const isSolved = solved.has(primary.id);
          return (
            <div
              key={primary.id}
              className={`cl-row${isSolved ? " cl-row-solved" : ""}`}
              onClick={() => onSelect(primary.id)}
            >
              <span className="cl-col-status">
                {isSolved && <span className="cl-check">✓</span>}
              </span>
              <span className="cl-col-title cl-row-title">{primary.title}</span>
              <span className="cl-col-category">
                <span className="category-tag">{primary.category}</span>
              </span>
              <span className="cl-col-langs">
                {langs.map((lang) => (
                  <span key={lang} className={`cl-lang cl-lang-${lang}`}>
                    {LANG_LABEL[lang] || lang}
                  </span>
                ))}
              </span>
              <span className="cl-col-diff">
                <span className={`badge badge-${primary.difficulty}`}>
                  {primary.difficulty}
                </span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
