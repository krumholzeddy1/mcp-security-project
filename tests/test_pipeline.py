"""
Basic smoke tests. Run with: python -m pytest tests/ -v
(or just: python -m tests.test_pipeline)

Proportion-based assertions (rather than absolute invariants) reflect the
intentional noise model in generate_corpus.py — see NOISE_RATES there for
the rates that drive the expected ranges below.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.generate_corpus import generate, text_entropy, keyword_hits, NOISE_RATES
from baseline.schema_validator import flag_at_registration

N = 200  # large enough for stable proportion estimates given the noise rates


def test_generate_produces_all_three_classes():
    rows = generate(n_per_class=10)
    labels = {r["label"] for r in rows}
    assert labels == {"benign", "poisoned", "rugpull"}
    assert len(rows) == 30


def test_benign_mostly_has_no_keyword_hits():
    """
    Most benign sessions have no keyword hits. Up to ~20% may have accidental
    hits (NOISE_RATES["benign_accidental_keyword"] = 8%; 20% allows for
    description-update suffixes that might also hit keywords).
    """
    rows = generate(n_per_class=N)
    benign = [r for r in rows if r["label"] == "benign"]
    reg_hit_rate = sum(1 for r in benign if r["reg_suspicious_keyword_hits"] > 0) / len(benign)
    call_hit_rate = sum(1 for r in benign if r["call_suspicious_keyword_hits"] > 0) / len(benign)
    assert reg_hit_rate <= 0.20, f"Too many benign reg keyword hits: {reg_hit_rate:.1%}"
    assert call_hit_rate <= 0.25, f"Too many benign call keyword hits: {call_hit_rate:.1%}"


def test_rugpull_mostly_changes_description():
    """
    Most rug-pulls mutate the description after registration. Up to ~15% may be
    'stealthy' (NOISE_RATES["rugpull_stealthy"] = 10%) — these revert before the
    metadata snapshot and are indistinguishable from benign sessions, representing
    the fundamental limit of point-in-time sampling.
    """
    rows = generate(n_per_class=N)
    rugpull = [r for r in rows if r["label"] == "rugpull"]
    changed_rate = sum(1 for r in rugpull if r["description_changed_after_registration"] == 1) / len(rugpull)
    assert changed_rate >= 0.80, f"Too few rugpulls changing description: {changed_rate:.1%}"


def test_rugpull_mostly_invisible_at_registration():
    """
    The majority of rug-pulls start with a clean registration description,
    making them invisible to the baseline. ~15% may be 'sloppy' (partial
    leak at registration, per NOISE_RATES["rugpull_partial_at_registration"]).
    """
    rows = generate(n_per_class=N)
    rugpull = [r for r in rows if r["label"] == "rugpull"]
    clean_rate = sum(1 for r in rugpull if r["reg_suspicious_keyword_hits"] == 0) / len(rugpull)
    assert clean_rate >= 0.70, f"Too few clean rugpull registrations: {clean_rate:.1%}"


def test_baseline_misses_majority_of_rugpulls():
    """
    The baseline structurally cannot see most rug-pulls. It may catch the
    'sloppy' subset (~15%) but should miss at least 70%.
    """
    rows = generate(n_per_class=N)
    rugpull = [r for r in rows if r["label"] == "rugpull"]
    flags = [flag_at_registration(r) for r in rugpull]
    miss_rate = sum(1 for f in flags if f == 0) / len(flags)
    assert miss_rate >= 0.70, f"Baseline catching too many rugpulls: {1 - miss_rate:.1%}"


def test_text_entropy_and_keyword_hits_basic_sanity():
    assert text_entropy("") == 0.0
    assert keyword_hits("this tool must be called before anything else") >= 1
    assert keyword_hits("a perfectly normal description") == 0


if __name__ == "__main__":
    test_generate_produces_all_three_classes()
    test_benign_mostly_has_no_keyword_hits()
    test_rugpull_always_changes_description()
    test_rugpull_mostly_invisible_at_registration()
    test_baseline_misses_majority_of_rugpulls()
    test_text_entropy_and_keyword_hits_basic_sanity()
    print("All smoke tests passed.")
