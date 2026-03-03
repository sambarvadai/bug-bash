import { useState, useEffect, useCallback } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChallengeInfo from "./components/ChallengeInfo.jsx";
import CodeEditor from "./components/CodeEditor.jsx";
import UpdateFeed from "./components/UpdateFeed.jsx";
import Results from "./components/Results.jsx";
import LandingPage from "./components/LandingPage.jsx";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

const SOLVED_KEY = "bug-bash-solved";
const FIRED_KEY  = "bug-bash-fired";

function loadSolved() {
  try { return new Set(JSON.parse(localStorage.getItem(SOLVED_KEY) || "[]")); }
  catch { return new Set(); }
}
function saveSolved(set) {
  localStorage.setItem(SOLVED_KEY, JSON.stringify([...set]));
}
function loadFiredUpdates() {
  try { return JSON.parse(localStorage.getItem(FIRED_KEY) || "{}"); }
  catch { return {}; }
}
function saveFiredUpdates(obj) {
  localStorage.setItem(FIRED_KEY, JSON.stringify(obj));
}

export default function App() {
  const [page, setPage] = useState("landing");
  const [challenges, setChallenges] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [hintShown, setHintShown] = useState(false);
  const [solved, setSolved] = useState(loadSolved);

  // runCounts: NOT persisted — fresh each page load (Option A: chaos mode)
  const [runCounts, setRunCounts] = useState({});
  // firedUpdates: { challengeId: [updateId, ...] } — persisted, once fired stays fired
  const [firedUpdates, setFiredUpdates] = useState(loadFiredUpdates);
  // randomThresholds: { "challengeId/updateId": N } — NOT persisted, re-rolled each load
  const [randomThresholds, setRandomThresholds] = useState({});
  // IDs that fired on the most recent run (drives "new" animation)
  const [newlyFiredIds, setNewlyFiredIds] = useState([]);

  // Re-roll random thresholds whenever a new challenge loads
  useEffect(() => {
    if (!challenge) return;
    const thresholds = {};
    for (const update of challenge.requirements_updates || []) {
      if (update.trigger.type === "random") {
        const key = `${challenge.id}/${update.id}`;
        const { min_runs, max_runs } = update.trigger;
        thresholds[key] = Math.floor(Math.random() * (max_runs - min_runs + 1)) + min_runs;
      }
    }
    if (Object.keys(thresholds).length > 0) {
      setRandomThresholds((prev) => ({ ...prev, ...thresholds }));
    }
    setNewlyFiredIds([]);
  }, [challenge]);

  // Fetch challenge list once
  useEffect(() => {
    fetch(`${API_BASE}/api/challenges`)
      .then((r) => r.json())
      .then((data) => {
        setChallenges(data);
        if (data.length > 0) setSelectedId(data[0].id);
      })
      .catch(console.error);
  }, []);

  // Fetch full challenge when selection changes
  useEffect(() => {
    if (!selectedId) return;
    setChallenge(null);
    setResults(null);
    setHintShown(false);
    fetch(`${API_BASE}/api/challenges/${selectedId}`)
      .then((r) => r.json())
      .then(setChallenge)
      .catch(console.error);
  }, [selectedId]);

  const handleRun = useCallback(
    async (files) => {
      if (!challenge) return;
      setRunning(true);

      // Increment run count (not persisted)
      const newRunCount = (runCounts[challenge.id] || 0) + 1;
      setRunCounts((prev) => ({ ...prev, [challenge.id]: newRunCount }));

      // active_update_ids = what was already fired BEFORE this run
      const currentlyFired = new Set(firedUpdates[challenge.id] || []);
      const activeUpdateIds = [...currentlyFired];

      try {
        const res = await fetch(`${API_BASE}/api/run/${challenge.id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ files, active_update_ids: activeUpdateIds }),
        });
        const data = await res.json();
        setResults(data);

        if (data.passed) {
          setSolved((prev) => {
            const next = new Set(prev);
            next.add(challenge.id);
            saveSolved(next);
            return next;
          });
        }

        // Check triggers for unfired updates
        const newlyFired = [];
        for (const update of challenge.requirements_updates || []) {
          if (currentlyFired.has(update.id)) continue;

          let shouldFire = false;
          const { type } = update.trigger;

          if (type === "on_pass" && data.passed) {
            shouldFire = true;
          } else if (type === "after_runs") {
            shouldFire = newRunCount >= update.trigger.count;
          } else if (type === "random") {
            const key = `${challenge.id}/${update.id}`;
            const threshold = randomThresholds[key];
            shouldFire = threshold !== undefined && newRunCount >= threshold;
          }

          if (shouldFire) newlyFired.push(update.id);
        }

        if (newlyFired.length > 0) {
          setFiredUpdates((prev) => {
            const next = {
              ...prev,
              [challenge.id]: [...(prev[challenge.id] || []), ...newlyFired],
            };
            saveFiredUpdates(next);
            return next;
          });
          setNewlyFiredIds(newlyFired);
        } else {
          setNewlyFiredIds([]);
        }
      } catch (err) {
        setResults({ passed: false, error: String(err), results: [] });
        setNewlyFiredIds([]);
      } finally {
        setRunning(false);
      }
    },
    [challenge, runCounts, firedUpdates, randomThresholds]
  );

  if (page === "landing") {
    return <LandingPage onStart={() => setPage("app")} />;
  }

  return (
    <div className="app">
      <Sidebar
        challenges={challenges}
        selectedId={selectedId}
        solved={solved}
        onSelect={setSelectedId}
      />
      <div className="main">
        {!challenge ? (
          <div className="empty-state">
            {challenges.length === 0 ? "Loading challenges…" : "Loading…"}
          </div>
        ) : (
          <div className="workspace">
            <div className="left-panel">
              <ChallengeInfo challenge={challenge} />
            </div>
            <div className="right-panel">
              <CodeEditor
                key={challenge.id}
                challenge={challenge}
                running={running}
                hintShown={hintShown}
                onRun={handleRun}
                onHint={() => setHintShown(true)}
              />
              <UpdateFeed
                challenge={challenge}
                firedUpdates={firedUpdates[challenge.id] || []}
                newlyFiredIds={newlyFiredIds}
              />
              {results && (
                <Results
                  results={results}
                  challenge={challenge}
                  firedUpdates={firedUpdates[challenge.id] || []}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
