# Contributing to Resume-Tailor MCP

Thanks for your interest in improving this project! 🎉 Contributions of every
size are welcome — bug fixes, new skill keywords, better export layouts, docs,
or entirely new tools.

This project is **MIT-licensed** and beginner-friendly. If it's your first pull
request ever, this guide walks you through it step by step.

## Quick overview of the workflow

```
Fork  ─►  Clone your fork  ─►  Create a branch  ─►  Make changes
      ─►  Test  ─►  Commit  ─►  Push  ─►  Open a Pull Request
```

## 1. Fork the repository

Click the **Fork** button at the top-right of
[the repo page](https://github.com/NmaaAlhawary/MCP-Resume-Tailor-).
This creates your own copy under your GitHub account.

## 2. Clone your fork locally

```bash
git clone git@github.com:YOUR-USERNAME/MCP-Resume-Tailor-.git
cd MCP-Resume-Tailor-
```

Then link the original repo as `upstream` so you can pull in future updates:

```bash
git remote add upstream git@github.com:NmaaAlhawary/MCP-Resume-Tailor-.git
git remote -v   # origin = your fork, upstream = the original
```

## 3. Set up the dev environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
```

Smoke-test that the server imports and all six tools register:

```bash
python -c "import asyncio, server; print([t.name for t in asyncio.run(server.mcp.list_tools())])"
```

## 4. Create a branch

Never work directly on `main`. Give your branch a short, descriptive name:

```bash
git checkout -b add-rust-keywords      # e.g. adding new skills
git checkout -b fix-pdf-margins        # e.g. fixing a bug
```

## 5. Make your change

Some good first contributions and where to make them, all in `server.py`:

| Want to… | Edit this |
|---|---|
| Add recognized single skills (e.g. `Elixir`, `Terraform`) | `KNOWN_TERMS` |
| Add multi-word skills/phrases (e.g. `"data pipelines"`) | `KNOWN_PHRASES` (map every spelling to one display name) |
| Filter out a filler word showing up as a "skill" | `STOPLIST` |
| Improve the PDF/DOCX layout | `_export_pdf` / `_export_docx` |
| Add a brand-new tool | Add a function decorated with `@mcp.tool()` |

**Keep the style consistent:** typed inputs, a clear docstring on every tool
(Claude reads these to understand the flow), and readable errors.

## 6. Test your change

Run a quick end-to-end check of the tools you touched. For example, to verify
keyword extraction on a sample job description:

```bash
python - <<'PY'
import os, tempfile
os.environ["RESUME_STORE_PATH"] = os.path.join(tempfile.mkdtemp(), "master.json")
import server as s
job = "Requirements:\n- Experience with Rust, Terraform, and Kubernetes."
print(s.extract_keywords(job)["keywords"])
PY
```

If you added a keyword, confirm it appears. If you touched export, confirm the
file opens and the text is selectable (ATS-safe).

## 7. Commit and push

Write a clear, present-tense commit message:

```bash
git add -A
git commit -m "Add Rust and Terraform to known skills"
git push origin add-rust-keywords
```

## 8. Open a Pull Request

Go to your fork on GitHub — it will show a **"Compare & pull request"** button.
Open a PR against `NmaaAlhawary/MCP-Resume-Tailor-` `main`. In the description,
briefly explain:

- **What** you changed.
- **Why** it helps.
- A short example of the before/after output, if relevant.

## Keeping your fork up to date

Before starting new work, sync with the original repo:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

## Ideas looking for contributors

- Expand `KNOWN_TERMS` / `KNOWN_PHRASES` for more industries (data, design, DevOps, marketing).
- A `cover_letter` export helper.
- Optional themes for `export_resume` (still ATS-safe).
- A small test suite (`tests/`) pinning the ATS-scoring logic.
- Better JavaScript-rendered job-page handling in `fetch_job_posting`.

## Code of conduct

Be kind and constructive. We're all here to build something useful together. 💛

Questions? Open an [issue](https://github.com/NmaaAlhawary/MCP-Resume-Tailor-/issues)
and ask — no question is too small.
