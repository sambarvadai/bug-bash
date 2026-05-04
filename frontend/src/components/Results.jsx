import { useState } from "react";

function getTestSource(index, challenge, firedUpdates) {
  if (!challenge) return null;
  const baseCount = challenge.test_cases.length;
  if (index < baseCount) return null;

  let offset = baseCount;
  for (const update of challenge.requirements_updates || []) {
    if (!firedUpdates.includes(update.id)) continue;
    const count = update.additional_test_cases?.length || 0;
    if (index < offset + count) return update.id;
    offset += count;
  }
  return null;
}

function ErrorFrame({ errors }) {
  return (
    <div className="error-frame">
      <div className="error-frame-label">Error</div>
      {errors.map((err, i) => (
        <pre key={i} className="error-frame-content">{err}</pre>
      ))}
    </div>
  );
}

function ResultRow({ result, index, source }) {
  const [open, setOpen] = useState(!result.passed);

  return (
    <div className="result-row">
      <div className="result-row-header" onClick={() => setOpen((o) => !o)}>
        <span className="icon">{result.passed ? "✅" : "❌"}</span>
        <span className="label">Test {index + 1}</span>
        {source && <span className="result-source-tag">{source}</span>}
        <span className={`chevron${open ? " open" : ""}`}>▶</span>
      </div>
      {open && (
        <div className={`result-detail${result.error ? " two-col" : ""}`}>
          <div className="field">
            <label>Input</label>
            <code>{JSON.stringify(result.input)}</code>
          </div>
          <div className="field">
            <label>Expected</label>
            <code>{JSON.stringify(result.expected)}</code>
          </div>
          {!result.error && (
            <div className="field">
              <label>Got</label>
              <code>{JSON.stringify(result.got)}</code>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function Results({ results, challenge, firedUpdates = [] }) {
  const hasTopError = results.error && results.results.length === 0;

  if (hasTopError) {
    return (
      <div className="results">
        <div className="results-banner error">Error</div>
        <ErrorFrame errors={[results.error]} />
      </div>
    );
  }

  const nPass = results.results.filter((r) => r.passed).length;
  const nTotal = results.results.length;
  const uniqueErrors = [...new Set(results.results.filter((r) => r.error).map((r) => r.error))];

  return (
    <div className="results">
      <div className={`results-banner ${results.passed ? "pass" : "fail"}`}>
        {results.passed
          ? `🎉 All ${nTotal} tests passed!`
          : `❌ ${nPass} / ${nTotal} tests passed`}
      </div>
      {uniqueErrors.length > 0 && <ErrorFrame errors={uniqueErrors} />}
      {results.results.map((r, i) => (
        <ResultRow
          key={i}
          result={r}
          index={i}
          source={getTestSource(i, challenge, firedUpdates)}
        />
      ))}
    </div>
  );
}
