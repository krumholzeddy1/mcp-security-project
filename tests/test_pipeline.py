"""
Basic smoke tests. Run with: python -m pytest tests/ -v
(or just: python -m tests.test_pipeline)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.generate_corpus import generate, text_entropy, keyword_hits
from baseline.schema_validator import flag_at_registration


def test_generate_produces_all_three_classes():
    rows = generate(n_per_class=10)
    labels = {r["label"] for r in rows}
    assert labels == {"benign", "poisoned", "rugpull"}
    assert len(rows) == 30


def test_benign_has_no_keyword_hits():
    rows = generate(n_per_class=20)
    benign_rows = [r for r in rows if r["label"] == "benign"]
    assert all(r["reg_suspicious_keyword_hits"] == 0 for r in benign_rows)
    assert all(r["call_suspicious_keyword_hits"] == 0 for r in benign_rows)


def test_rugpull_is_invisible_at_registration_but_visible_at_call():
    rows = generate(n_per_class=30)
    rugpull_rows = [r for r in rows if r["label"] == "rugpull"]
    assert all(r["description_changed_after_registration"] == 1 for r in rugpull_rows)
    # this is the whole point of the project: registration-time keyword
    # hits should be 0 for rug-pulls, call-time hits should not be
    assert all(r["reg_suspicious_keyword_hits"] == 0 for r in rugpull_rows)
    assert all(r["call_suspicious_keyword_hits"] > 0 for r in rugpull_rows)


def test_baseline_structurally_cannot_see_rugpull():
    rows = generate(n_per_class=30)
    rugpull_rows = [r for r in rows if r["label"] == "rugpull"]
    flags = [flag_at_registration(r) for r in rugpull_rows]
    assert all(f == 0 for f in flags), "Baseline should miss every rug-pull by construction"


def test_text_entropy_and_keyword_hits_basic_sanity():
    assert text_entropy("") == 0.0
    assert keyword_hits("this tool must be called before anything else") >= 1
    assert keyword_hits("a perfectly normal description") == 0


if __name__ == "__main__":
    test_generate_produces_all_three_classes()
    test_benign_has_no_keyword_hits()
    test_rugpull_is_invisible_at_registration_but_visible_at_call()
    test_baseline_structurally_cannot_see_rugpull()
    test_text_entropy_and_keyword_hits_basic_sanity()
    print("All smoke tests passed.")
