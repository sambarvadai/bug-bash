const TEASERS = [
  {
    label: "easy_03.py",
    code: `def factorial(n):
    if n == 0:
        return 1
    factorial(n - 1)`,
  },
  {
    label: "medium_02.py",
    code: `class Tracker:
    log = []

    def record(self, entry):
        self.log.append(entry)`,
  },
  {
    label: "medium_01.py",
    code: `handlers = {}
for event in events:
    handlers[event] = (
        lambda: process(event)
    )`,
  },
];

export default function LandingPage({ onStart }) {
  return (
    <div className="landing">
      <div className="landing-hero">
        <h1 className="landing-title">Bug Bash</h1>
        <p className="landing-tagline">
          Your linter can't save you here.
        </p>
        <p className="landing-sub">
          10 Python bugs. Each one looks fine at a glance.
        </p>
        <button className="landing-cta" onClick={onStart}>
          Solve Now
        </button>
      </div>

      <div className="landing-teasers">
        {TEASERS.map((t) => (
          <div className="teaser-card" key={t.label}>
            <div className="teaser-header">{t.label}</div>
            <pre className="teaser-code"><code>{t.code}</code></pre>
            <div className="teaser-footer">spot the bug →</div>
          </div>
        ))}
      </div>
    </div>
  );
}
