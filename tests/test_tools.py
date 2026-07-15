"""Tests for the Resume-Tailor MCP tools.

Run with:  pytest

Every test uses a fresh temp store via the `srv` fixture, so nothing touches
your real ~/.resume-mcp/master.json.
"""

from __future__ import annotations

import importlib
import os

import pytest


@pytest.fixture()
def srv(tmp_path, monkeypatch):
    """Import the server with the store pointed at an isolated temp dir."""
    monkeypatch.setenv("RESUME_STORE_PATH", str(tmp_path / "master.json"))
    import server
    importlib.reload(server)  # re-resolve _store_path() against the temp env
    return server


# --------------------------------------------------------------------------- #
# save_master_resume / load_master_resume
# --------------------------------------------------------------------------- #

def test_save_and_load_roundtrip(srv):
    data = {"contact": {"name": "Nmaa Hawary"}, "skills": ["Python", "React"]}
    msg = srv.save_master_resume(data)
    assert "Nmaa Hawary" in msg
    assert srv.load_master_resume() == data


def test_load_without_saving_raises(srv):
    with pytest.raises(FileNotFoundError):
        srv.load_master_resume()


# --------------------------------------------------------------------------- #
# fetch_job_posting
# --------------------------------------------------------------------------- #

def test_fetch_pasted_text(srv):
    out = srv.fetch_job_posting(pasted_text="We need React and Docker.")
    assert out["source"] == "pasted"
    assert "React" in out["text"]
    assert out["char_count"] > 0


def test_fetch_no_input_is_clear(srv):
    out = srv.fetch_job_posting()
    assert out["source"] == "none"
    assert "paste" in out["message"].lower()


def test_fetch_bad_url_never_fails_silently(srv):
    out = srv.fetch_job_posting(url="http://127.0.0.1:9/nope")
    assert out["source"] == "url_failed"
    assert "paste" in out["message"].lower()


# --------------------------------------------------------------------------- #
# extract_keywords
# --------------------------------------------------------------------------- #

def test_extract_finds_known_skills(srv):
    job = (
        "Requirements:\n- React, TypeScript, Next.js\n"
        "- REST APIs, Docker, AWS\n- Unit testing with Jest"
    )
    kws = srv.extract_keywords(job)["keywords"]
    for expected in ["React", "TypeScript", "Docker", "AWS", "REST APIs"]:
        assert expected in kws


def test_extract_drops_filler_words(srv):
    kws = [k.lower() for k in srv.extract_keywords("Requirements: strong team player")["keywords"]]
    assert "strong" not in kws
    assert "team" not in kws


def test_extract_collapses_phrase_duplicates(srv):
    # "rest api" and "rest apis" should collapse to one display entry.
    kws = srv.extract_keywords("We build REST APIs and REST API endpoints.")["keywords"]
    assert kws.count("REST APIs") <= 1


# --------------------------------------------------------------------------- #
# ats_gap_check
# --------------------------------------------------------------------------- #

def test_gap_check_math_and_missing(srv):
    keywords = ["Python", "React", "Docker", "AWS"]
    result = srv.ats_gap_check("Built apps with Python and React.", keywords)
    assert result["match_score"] == 50.0
    assert set(result["matched"]) == {"Python", "React"}
    assert set(result["missing"]) == {"Docker", "AWS"}
    assert result["total_keywords"] == 4


def test_gap_check_full_match(srv):
    result = srv.ats_gap_check("Python React Docker", ["Python", "React", "Docker"])
    assert result["match_score"] == 100.0
    assert result["missing"] == []


def test_gap_check_tolerates_plurals(srv):
    result = srv.ats_gap_check("Designed REST APIs for the platform.", ["REST API"])
    assert result["match_score"] == 100.0


# --------------------------------------------------------------------------- #
# export_resume
# --------------------------------------------------------------------------- #

def test_export_docx_creates_file(srv):
    out = srv.export_resume({"contact": {"name": "Nmaa"}, "skills": ["Python"]}, format="docx")
    assert os.path.exists(out["path"])
    assert out["path"].endswith(".docx")
    assert os.path.getsize(out["path"]) > 0


def test_export_pdf_creates_file(srv):
    out = srv.export_resume("# Nmaa\n## Skills\nPython, React", format="pdf")
    assert os.path.exists(out["path"])
    assert out["path"].endswith(".pdf")
    with open(out["path"], "rb") as fh:
        assert fh.read(5) == b"%PDF-"  # real PDF header


def test_export_empty_content_raises(srv):
    with pytest.raises(ValueError):
        srv.export_resume("", format="docx")
