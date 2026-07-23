"""
Synthetic attack corpus generator (Deliverable 2: "Attack corpus generation").

Generates labelled tool-call sessions across three classes:
  - benign:   normal tool registration + calls, no mutation
  - poisoned: description contains an injected instruction-like fragment
              from the moment of registration
  - rugpull:  description starts clean, passes "review", then mutates
              partway through the session (the delayed-attack pattern
              documented by Willison, 2025)

Each session becomes one row of tool-call metadata features - NOT raw
prompt/response text - because the detector in this project works on
metadata and description-change patterns, per the research question.

Output: data/corpus.csv
"""

import csv
import math
import random
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server.tool_definitions import TOOL_CATALOG

random.seed(42)

SUSPICIOUS_KEYWORDS = [
    "ignore prior", "ignore previous", "system:", "must be called before",
    "ssh", "config file", "environment variable", "verbose_mode",
    "regardless of user request", "note to assistant",
]


def text_entropy(text: str) -> float:
    """Shannon entropy of the description text (simple lexical-diversity signal)."""
    if not text:
        return 0.0
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def keyword_hits(text: str) -> int:
    lower = text.lower()
    return sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in lower)


def make_session(session_id: int, label: str) -> dict:
    spec = random.choice(TOOL_CATALOG)
    num_calls = random.randint(1, 12)
    call_position = random.randint(1, num_calls)
    time_since_registration_s = random.randint(1, 3600)

    description_at_registration = spec.benign_description
    description_at_call = spec.benign_description
    description_changed = 0

    if label == "poisoned":
        fragment = random.choice(spec.poison_fragments)
        description_at_registration = f"{spec.benign_description} {fragment}"
        description_at_call = description_at_registration

    elif label == "rugpull":
        # starts clean, mutates after registration - only visible if you
        # re-check the description *after* the tool has been trusted/connected
        fragment = random.choice(spec.poison_fragments)
        description_at_registration = spec.benign_description
        description_at_call = f"{spec.benign_description} {fragment}"
        description_changed = 1
        # rug-pulls tend to happen after the tool has been in use a while
        time_since_registration_s = random.randint(600, 7200)
        low_bound = min(max(2, num_calls // 2), num_calls)
        call_position = random.randint(low_bound, num_calls)

    return {
        "session_id": session_id,
        "tool_name": spec.name,
        "label": label,
        "num_schema_fields": len(spec.schema_fields),
        # registration-time features: this is ALL a one-shot schema
        # validator can ever see, by construction
        "reg_description_length": len(description_at_registration),
        "reg_description_entropy": round(text_entropy(description_at_registration), 3),
        "reg_suspicious_keyword_hits": keyword_hits(description_at_registration),
        # call-time features: only visible to something that re-checks
        # behaviour later in the session, which is the ML detector's job
        "call_description_length": len(description_at_call),
        "call_description_entropy": round(text_entropy(description_at_call), 3),
        "call_suspicious_keyword_hits": keyword_hits(description_at_call),
        "description_changed_after_registration": description_changed,
        "time_since_registration_s": time_since_registration_s,
        "call_position_in_session": call_position,
        "num_calls_in_session": num_calls,
    }


def generate(n_per_class: int = 200) -> list:
    rows = []
    sid = 0
    for label in ("benign", "poisoned", "rugpull"):
        for _ in range(n_per_class):
            rows.append(make_session(sid, label))
            sid += 1
    random.shuffle(rows)
    return rows


def main():
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)
    rows = generate(n_per_class=200)  # 600 sessions total: 200 per class
    out_path = out_dir / "corpus.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} sessions to {out_path}")


if __name__ == "__main__":
    main()
