"""End-to-end demo of the Resume-Tailor MCP tools.

Runs every tool once with sample data and prints the output, so you can see the
whole load -> analyze -> check -> export flow without an MCP client.

Uses a throwaway temp store, so it never touches your real master.json.

    python demo.py
"""

from __future__ import annotations

import json
import os
import tempfile

# Point the store at a temp dir BEFORE importing the server.
os.environ["RESUME_STORE_PATH"] = os.path.join(tempfile.mkdtemp(), "master.json")

import server as s  # noqa: E402


def show(title: str, obj: object) -> None:
    print("\n" + "=" * 68 + f"\n{title}\n" + "=" * 68)
    print(obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False))


SAMPLE_MASTER = {
    "contact": {"name": "Nmaa Hawary", "email": "nmaa@example.com",
                "location": "Amman, JO"},
    "summary": "Full-stack developer building web apps and 3D interfaces.",
    "experience": [{
        "title": "Software Engineer", "company": "HTU",
        "start": "2023", "end": "Present",
        "bullets": ["Built React dashboards", "Shipped REST APIs in Python"],
    }],
    "skills": ["Python", "JavaScript", "React", "Git"],
    "education": [{"degree": "BSc CS", "school": "HTU", "start": "2021", "end": "2025"}],
}

SAMPLE_JOB = """Senior Frontend Engineer

Requirements:
- 5+ years with React and TypeScript
- Strong experience with REST APIs and GraphQL
- Familiarity with Docker, AWS, and CI/CD pipelines
- Experience with Next.js and Tailwind CSS
- Unit testing with Jest
"""


def main() -> None:
    # 1 & 2 — persist and load the master CV.
    show("1) save_master_resume", s.save_master_resume(SAMPLE_MASTER))
    show("2) load_master_resume", s.load_master_resume())

    # 3 — pull the job posting (paste path; URL path is best-effort).
    fetched = s.fetch_job_posting(pasted_text=SAMPLE_JOB)
    show("3) fetch_job_posting", {"source": fetched["source"], "chars": fetched["char_count"]})

    # 4 — deterministic keyword extraction.
    kw = s.extract_keywords(fetched["text"])
    show("4) extract_keywords", kw["keywords"])

    # 5 — the ATS gap check against the (untailored) master CV text.
    resume_text = SAMPLE_MASTER["summary"] + " " + " ".join(
        b for job in SAMPLE_MASTER["experience"] for b in job["bullets"]
    ) + " Skills: " + ", ".join(SAMPLE_MASTER["skills"])
    gap = s.ats_gap_check(resume_text, kw["keywords"])
    show("5) ats_gap_check", gap["summary"])

    # 6 — export to DOCX and PDF.
    show("6) export_resume (docx)", s.export_resume(SAMPLE_MASTER, format="docx"))
    show("6) export_resume (pdf)", s.export_resume(SAMPLE_MASTER, format="pdf"))

    # 7 — export a matching cover letter (Claude writes the text; the tool formats it).
    cover = (
        "Dear Hiring Manager,\n\n"
        "I'm excited to apply for the Senior Frontend Engineer role. My work in "
        "React, TypeScript and REST APIs maps directly to your stack, and I've "
        "shipped production features end-to-end.\n\n"
        "I'd welcome the chance to bring that experience to your team.\n\n"
        "Sincerely,\nNmaa Hawary"
    )
    show("7) export_cover_letter (pdf)", s.export_cover_letter(cover, format="pdf"))

    print("\nDone. Exports written next to the temp store:")
    print("  ", os.path.join(os.path.dirname(os.environ["RESUME_STORE_PATH"]), "exports"))


if __name__ == "__main__":
    main()
