# Bug Bash

> **This is a proof of concept. Everything is subject to change.**

A LeetCode-style platform for debugging Python code. You're given broken code — find the bug, fix it, pass the tests.

## Current Features

- 10 challenges across easy and medium difficulty
- Monaco editor (VS Code's editor) with syntax highlighting and multi-file tab support
- Mid-challenge requirement changes — because real work never stays the same
- Sandboxed code execution

## Stack

- **Frontend**: React + Vite + Monaco Editor
- **Backend**: FastAPI + Python subprocess runner

## Coming Soon

- Hard difficulty challenges
- More challenge variety
- User accounts and leaderboard
- Better tagging and filtering
