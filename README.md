# Resume-Tailor MCP

An open-source **MCP server** that helps an AI client (Claude Desktop, Cursor, etc.)
tailor your CV to a specific job — automatically.

You say: *"Here's a job link — tailor my CV and export a PDF."*
Claude reads the posting and your master CV, rewrites the CV to match, and hands
you a clean file ready to send.

## Why install this instead of just pasting into chat?

Claude can already rewrite a CV in a normal chat. This MCP is worth installing
for the three things a plain chat **can't** do:

1. **A persistent master CV** — stored locally as JSON, set up once, reused for every job.
2. **A real ATS gap score** — deterministic keyword math (not vibes) that tells you *concretely* which keywords you're missing.
3. **Clean file export** — ATS-safe PDF/DOCX with real text, single column, standard fonts.

**The MCP does not rewrite your CV — Claude does that.** The MCP supplies the
persistent storage, the job fetch, the ATS math, and the export. Claude ties it
together.

## The flow: load → analyze → rewrite → check → export

```
load_master_resume  ─┐
                     ├─► Claude rewrites the CV ─► ats_gap_check ─► export_resume
fetch_job_posting ──►│                                  ▲
extract_keywords ────┘──────────────────────────────────┘
```

1. **load** your master CV (`load_master_resume`).
2. **analyze** the job: `fetch_job_posting` → `extract_keywords`.
3. **rewrite** — *Claude* rewrites the CV to surface the missing keywords honestly.
4. **check** the rewrite with `ats_gap_check` — did the score go up?
5. **export** the finished CV to PDF or DOCX (`export_resume`).

## Tools

| Tool | Purpose |
|---|---|
| `save_master_resume` | Store/update the base CV (structured JSON: contact, summary, experience, projects, skills, education). |
| `load_master_resume` | Return the stored master CV so Claude can work from it. |
| `fetch_job_posting` | Fetch a job URL → clean text. Falls back to pasted text if the site is blocked/login-walled. |
| `extract_keywords` | Deterministically pull the ranked skills/tools an ATS scans for. |
| `ats_gap_check` | Compare a CV against the job keywords → match score (%) + the exact missing terms. |
| `export_resume` | Render finished CV content (markdown or JSON) to a clean PDF or DOCX. Returns the file path. |

## Install

```bash
git clone <your-repo-url> resume-tailor-mcp
cd resume-tailor-mcp
python3 -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
```

Run it directly to smoke-test:

```bash
python server.py
```

### PDF export note
PDF export uses **reportlab** (pure Python, installs cleanly on macOS/Windows/Linux
with no system libraries). DOCX export uses **python-docx**. Both produce
single-column, real-text output that ATS parsers can read.

## Connect to Claude Desktop

Add this to your `claude_desktop_config.json`
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "resume-tailor": {
      "command": "/absolute/path/to/resume-tailor-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/resume-tailor-mcp/server.py"],
      "env": {
        "RESUME_STORE_PATH": "~/.resume-mcp/master.json"
      }
    }
  }
}
```

Restart Claude Desktop. The six tools appear under the 🔌 menu.

## First-time setup: store your master CV

Copy `master.template.json`, fill in your details, then ask Claude:

> "Save this as my master resume: *(paste the JSON)*"

Claude calls `save_master_resume` and it persists at `RESUME_STORE_PATH`
(default `~/.resume-mcp/master.json`). You only do this once.

## Example session

> **You:** Here's a job link — tailor my CV for it and export a PDF:
> `https://example.com/careers/senior-frontend`

Behind the scenes Claude runs:

1. `load_master_resume()` → your stored CV.
2. `fetch_job_posting(url="…/senior-frontend")` → clean job text
   *(if the site is blocked, Claude asks you to paste the description; then it calls `fetch_job_posting(pasted_text="…")`).*
3. `extract_keywords(job_text)` →
   `["REST APIs", "GraphQL", "Unit Testing", "CI/CD", "React", "TypeScript", "Docker", "AWS", "Jest", "Figma", "Next.js", "Tailwind CSS", …]`
4. `ats_gap_check(resume_text, keywords)` →
   `{ "match_score": 20.0, "missing": ["GraphQL", "TypeScript", "Docker", "AWS", "Jest", …] }`
5. **Claude rewrites** your CV — truthfully surfacing the real skills you have
   that match the missing terms, rephrasing bullets to use the job's language.
6. `ats_gap_check(new_resume_text, keywords)` → `{ "match_score": 85.0 }` ✅
7. `export_resume(content=<rewritten CV>, format="pdf")` →
   `{ "path": "~/.resume-mcp/exports/Jane_Developer_20260715-…​.pdf" }`

> **Claude:** Tailored your CV — keyword match went from **20% → 85%**. I added
> your Docker/AWS and testing experience to match their stack. Exported here:
> `~/.resume-mcp/exports/Jane_Developer_….pdf`

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `RESUME_STORE_PATH` | `~/.resume-mcp/master.json` | Where the master CV JSON lives. Exports go to `exports/` next to it. |

Everything runs **locally**. No secrets, no external accounts.

## ATS-safe export guarantees

- Single column — no text boxes, no multi-column tricks that break ATS parsers.
- Standard fonts (Calibri / Helvetica).
- Real selectable text — never image-rendered.
- Plain headings and bullet lists that map cleanly to resume sections.

## Contributing

Contributions are very welcome — this is an open-source project and PRs of any
size help. The quickest way in is to **fork** the repo, add what you want (new
skill keywords, a nicer export layout, a new tool), and open a pull request.

```bash
# 1. Fork on GitHub, then clone your fork
git clone git@github.com:YOUR-USERNAME/MCP-Resume-Tailor-.git
cd MCP-Resume-Tailor-

# 2. Set up and create a branch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
git checkout -b my-improvement

# 3. Make your change, commit, push
git commit -am "Describe your change"
git push origin my-improvement

# 4. Open a Pull Request on GitHub
```

Great first contributions: add skills to `KNOWN_TERMS` / `KNOWN_PHRASES` in
`server.py`, filter a filler word in `STOPLIST`, or improve the PDF/DOCX layout.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full step-by-step guide,
including how to keep your fork in sync and where each part of the code lives.

## License

MIT — see [LICENSE](LICENSE). By contributing, you agree your contributions are
licensed under the same MIT license.
