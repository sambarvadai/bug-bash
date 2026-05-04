# Bug Bash

A LeetCode-style platform for debugging code. You're given broken code — find the bug, fix it, pass the tests.

## Features

- **21 easy + 18 medium challenges** across Python, JavaScript, and TypeScript
- **In-editor language switcher** — same problem, pick your language (like LeetCode)
- **Monaco editor** — VS Code's editor with syntax highlighting and multi-file tab support
- **Mid-challenge requirement changes** — a PM drops new requirements while you're mid-fix, because real work never stays the same
- **Sandboxed execution** — Python subprocess runner + Node/ts-node for JS/TS

## Stack

- **Frontend**: React + Vite + Monaco Editor
- **Backend**: FastAPI + Python subprocess runner

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

The frontend proxies API calls to `http://localhost:8000` by default. To override, create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

## Docker

```bash
docker build -t bug-bash .
docker run -p 8000:8000 bug-bash
```

Then build and serve the frontend separately, or set `VITE_API_URL` to point at the container.

## Challenge Structure

```
challenges/
  easy/
    01_sum_range/        # Python
    08_sum_range_js/     # JavaScript
    15_sum_range_ts/     # TypeScript
    ...
  medium/
    01_student_grades/   # Python
    07_student_grades_js/
    13_student_grades_ts/
    ...
```

Each challenge folder contains a `challenge.json` (metadata + test cases) and one or more buggy source files.

## Coming Soon

- Hard difficulty challenges
- User accounts and leaderboard
