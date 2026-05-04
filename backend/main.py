import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from runner import run_challenge

app = FastAPI(title="Bug Squash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_DIR = Path(__file__).parent
CHALLENGES_DIR = BACKEND_DIR.parent / "challenges"


def load_all_challenges() -> list[dict]:
    challenges = []
    for difficulty in ["easy", "medium", "hard"]:
        diff_dir = CHALLENGES_DIR / difficulty
        if not diff_dir.is_dir():
            continue
        for name in sorted(os.listdir(diff_dir)):
            path = diff_dir / name
            json_path = path / "challenge.json"
            if not json_path.is_file():
                continue
            with open(json_path, encoding="utf-8") as f:
                ch = json.load(f)
            ch["_dir"] = str(path)
            for fi in ch["files"]:
                fp = path / fi["name"]
                with open(fp, encoding="utf-8") as f:
                    fi["initial_code"] = f.read()
            challenges.append(ch)
    return challenges


_challenges: list[dict] = load_all_challenges()
_challenge_map: dict[str, dict] = {ch["id"]: ch for ch in _challenges}


@app.get("/api/challenges")
def list_challenges():
    return [
        {
            "id": ch["id"],
            "title": ch["title"],
            "difficulty": ch["difficulty"],
            "category": ch["category"],
            "language": ch.get("language", "python"),
        }
        for ch in _challenges
    ]


@app.get("/api/challenges/{challenge_id}")
def get_challenge(challenge_id: str):
    ch = _challenge_map.get(challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    # Return everything except _dir
    result = {k: v for k, v in ch.items() if k != "_dir"}
    return result


class RunRequest(BaseModel):
    files: dict[str, str]
    active_update_ids: list[str] = []


@app.post("/api/run/{challenge_id}")
def run(challenge_id: str, body: RunRequest):
    ch = _challenge_map.get(challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Assemble test cases: base + additional from each fired update (in order)
    test_cases = list(ch["test_cases"])
    for update in ch.get("requirements_updates", []):
        if update["id"] in body.active_update_ids:
            test_cases.extend(update.get("additional_test_cases", []))

    ch_for_run = {**ch, "test_cases": test_cases}
    return run_challenge(ch_for_run, body.files)


# Serve built React app in production
_frontend_dist = BACKEND_DIR.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="spa")
