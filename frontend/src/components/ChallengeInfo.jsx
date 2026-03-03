import ReactMarkdown from "react-markdown";

/**
 * Splits a description string into:
 *   intro    - prose before the first Example
 *   examples - [{id, content}] one per Example block
 *   footer   - Constraints / Note / Tasks section
 */
function parseDescription(text) {
  // Locate where the footer section starts
  const footerIdx = text.search(/\n\n\*\*(Constraints|Note|Notes|Tasks)\b/);
  const main   = footerIdx >= 0 ? text.slice(0, footerIdx) : text;
  const footer = footerIdx >= 0 ? text.slice(footerIdx).trim() : "";

  // Split on **Example N:** headers
  const parts  = main.split(/\*\*Example \d+:\*\*\n?/);
  const intro  = parts[0].trim();
  const examples = parts.slice(1).map((content, i) => ({
    id: i + 1,
    content: content.trim(),
  }));

  return { intro, examples, footer };
}

function InlineValue({ text }) {
  const parts = text.split(/`([^`]+)`/);
  return parts.map((part, i) =>
    i % 2 === 1 ? <code key={i}>{part}</code> : part
  );
}

function parseExampleRows(content) {
  const lines = content.split("\n");
  const rows = [];
  let i = 0;

  while (i < lines.length) {
    const m = lines[i].match(/^(Input|Output|Explanation):\s*(.*)/);
    if (!m) { i++; continue; }

    const label = m[1];
    const inline = m[2].trim();
    i++;

    if (inline) {
      // Value is on the same line: Input: `n = 5`
      rows.push({ label, value: inline, isBlock: false });
    } else if (lines[i] && lines[i].trim() === "```") {
      // Value is a fenced code block on the next lines
      i++; // skip opening fence
      const codeLines = [];
      while (i < lines.length && lines[i].trim() !== "```") {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing fence
      rows.push({ label, value: codeLines.join("\n"), isBlock: true });
    } else {
      rows.push({ label, value: "", isBlock: false });
    }
  }

  return rows;
}

function ExampleBox({ id, content }) {
  const rows = parseExampleRows(content);

  return (
    <div className="example-box">
      <div className="example-box-title">Example {id}</div>
      {rows.length > 0 ? (
        <div className="example-structured">
          {rows.map((row, i) => (
            <div key={i} className={`example-row${row.isBlock ? " example-row-block" : ""}`}>
              <span className="example-label">{row.label}</span>
              {row.isBlock ? (
                <pre className="example-block"><code>{row.value}</code></pre>
              ) : (
                <span className="example-value"><InlineValue text={row.value} /></span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="example-box-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}


export default function ChallengeInfo({ challenge }) {
  const { intro, examples, footer } = parseDescription(challenge.description);

  return (
    <div className="challenge-info">
      <div className="challenge-meta">
        <span className="challenge-title">{challenge.title}</span>
        <span className={`badge badge-${challenge.difficulty}`}>
          {challenge.difficulty}
        </span>
      </div>

      <div className="challenge-description">
        {intro && <ReactMarkdown>{intro}</ReactMarkdown>}

        {examples.length > 0 && (
          <div className="examples-list">
            {examples.map((ex) => (
              <ExampleBox key={ex.id} id={ex.id} content={ex.content} />
            ))}
          </div>
        )}

        {footer && (
          <div className="challenge-footer">
            <ReactMarkdown>{footer}</ReactMarkdown>
          </div>
        )}
      </div>

    </div>
  );
}
