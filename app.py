import streamlit as st
import json
import os

from backend.runner import run_challenge

st.set_page_config(
    page_title="Bug Squash",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
textarea { font-family: 'Courier New', monospace !important; font-size: 13px !important; }
.stTextArea label { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

CHALLENGES_DIR = os.path.join(os.path.dirname(__file__), "challenges")

DIFF_ICON = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
DIFF_LABEL = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}


@st.cache_resource
def load_all_challenges():
    challenges = []
    for difficulty in ["easy", "medium", "hard"]:
        diff_dir = os.path.join(CHALLENGES_DIR, difficulty)
        if not os.path.isdir(diff_dir):
            continue
        for name in sorted(os.listdir(diff_dir)):
            path = os.path.join(diff_dir, name)
            json_path = os.path.join(path, "challenge.json")
            if not os.path.isfile(json_path):
                continue
            with open(json_path, encoding="utf-8") as f:
                ch = json.load(f)
            ch["_dir"] = path
            for fi in ch["files"]:
                fp = os.path.join(path, fi["name"])
                with open(fp, encoding="utf-8") as f:
                    fi["initial_code"] = f.read()
            challenges.append(ch)
    return challenges


challenges = load_all_challenges()
challenge_map = {ch["id"]: ch for ch in challenges}

# --- Session state ---
if "selected_id" not in st.session_state:
    st.session_state.selected_id = challenges[0]["id"] if challenges else None
if "user_code" not in st.session_state:
    st.session_state.user_code = {}
if "results" not in st.session_state:
    st.session_state.results = {}
if "hints_shown" not in st.session_state:
    st.session_state.hints_shown = set()
if "solved" not in st.session_state:
    st.session_state.solved = set()


def get_user_code(ch):
    cid = ch["id"]
    if cid not in st.session_state.user_code:
        st.session_state.user_code[cid] = {
            fi["name"]: fi["initial_code"] for fi in ch["files"]
        }
    return st.session_state.user_code[cid]


def reset_challenge(ch):
    cid = ch["id"]
    st.session_state.user_code.pop(cid, None)
    st.session_state.results.pop(cid, None)
    for fi in ch["files"]:
        key = f"editor_{cid}_{fi['name']}"
        st.session_state.pop(key, None)


# --- Sidebar ---
with st.sidebar:
    st.title("🐛 Bug Squash")
    st.caption("Find the bug. Fix it. Pass all tests.")
    st.markdown("---")

    by_diff = {}
    for ch in challenges:
        by_diff.setdefault(ch["difficulty"], []).append(ch)

    for diff in ["easy", "medium", "hard"]:
        if diff not in by_diff:
            continue
        st.subheader(f"{DIFF_ICON[diff]} {diff.capitalize()}")
        for ch in by_diff[diff]:
            solved = ch["id"] in st.session_state.solved
            label = ("✅ " if solved else "") + ch["title"]
            if st.button(label, key=f"nav_{ch['id']}", use_container_width=True):
                st.session_state.selected_id = ch["id"]
        st.markdown("---")

    total = len(challenges)
    solved_count = len(st.session_state.solved)
    st.progress(solved_count / total if total else 0)
    st.caption(f"{solved_count} / {total} solved")


# --- Main content ---
if not st.session_state.selected_id:
    st.info("Select a challenge from the sidebar to get started.")
    st.stop()

ch = challenge_map[st.session_state.selected_id]
user_code = get_user_code(ch)

# Header
col_title, col_diff, col_cat = st.columns([4, 1, 1])
with col_title:
    st.title(ch["title"])
with col_diff:
    st.markdown(f"**{DIFF_LABEL[ch['difficulty']]}**")
with col_cat:
    st.markdown(f"`{ch['category']}`")

st.markdown(ch["description"])
st.markdown("---")

# Code editor(s)
st.subheader("Editor")

if len(ch["files"]) == 1:
    fi = ch["files"][0]
    fname = fi["name"]
    code = st.text_area(
        fname,
        value=user_code[fname],
        height=320,
        key=f"editor_{ch['id']}_{fname}",
    )
    user_code[fname] = code
else:
    tabs = st.tabs([fi["name"] for fi in ch["files"]])
    for tab, fi in zip(tabs, ch["files"]):
        with tab:
            fname = fi["name"]
            code = st.text_area(
                fname,
                value=user_code[fname],
                height=320,
                key=f"editor_{ch['id']}_{fname}",
            )
            user_code[fname] = code

# Action buttons
btn_run, btn_hint, btn_reset, _ = st.columns([1, 1, 1, 3])
with btn_run:
    run_clicked = st.button("▶ Run Tests", type="primary", use_container_width=True)
with btn_hint:
    hint_clicked = st.button("💡 Hint", use_container_width=True)
with btn_reset:
    reset_clicked = st.button("🔄 Reset", use_container_width=True)

if hint_clicked:
    st.session_state.hints_shown.add(ch["id"])

if reset_clicked:
    reset_challenge(ch)
    st.rerun()

if ch["id"] in st.session_state.hints_shown:
    st.info(f"💡 **Hint:** {ch['hint']}")

# Run tests
if run_clicked:
    with st.spinner("Running tests..."):
        result = run_challenge(ch, user_code)
    st.session_state.results[ch["id"]] = result
    if result["passed"]:
        st.session_state.solved.add(ch["id"])

# Results
if ch["id"] in st.session_state.results:
    result = st.session_state.results[ch["id"]]
    st.markdown("---")
    st.subheader("Results")

    if result.get("error") and not result.get("results"):
        st.error(f"**Error:** {result['error']}")
    else:
        n_pass = sum(1 for r in result["results"] if r["passed"])
        n_total = len(result["results"])

        if result["passed"]:
            st.success(f"🎉 All {n_total} tests passed!")
        else:
            st.error(f"❌ {n_pass} / {n_total} tests passed")

        for i, r in enumerate(result["results"], 1):
            status = "✅ Pass" if r["passed"] else "❌ Fail"
            with st.expander(f"Test {i}: {status}", expanded=not r["passed"]):
                left, right = st.columns(2)
                with left:
                    st.write("**Input:**", r.get("input"))
                    st.write("**Expected:**", r["expected"])
                with right:
                    if r.get("error"):
                        st.error(f"**Error:** {r['error']}")
                    else:
                        st.write("**Got:**", r["got"])
