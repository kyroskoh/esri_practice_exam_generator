#!/usr/bin/env python3
"""
Emit a JSON array of new practice questions, unique vs existing questions.json
(by normalized stem text). Combines INTROS with generate_questions.TEMPLATES.

Usage:
  python emit_bulk_questions.py --count 400 > new_questions.json
  python generate_questions_cursor.py merge new_questions.json
"""
import argparse
import json
import os
import random
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from generate_questions import TEMPLATES  # noqa: E402

QUESTIONS_PATH = os.path.join(SCRIPT_DIR, "questions.json")

INTROS = [
    "Following Esri documentation for ArcGIS Pro, ",
    "When using ArcGIS Pro workflows, ",
    "In standard ArcGIS Pro practice, ",
    "When working with maps and layers in ArcGIS Pro, ",
    "As described in ArcGIS Pro help topics, ",
    "From a cartography workflow perspective, ",
    "When preparing a project in ArcGIS Pro, ",
    "During editing in ArcGIS Pro, ",
    "To align with common ArcGIS Pro tasks, ",
    "When troubleshooting display in ArcGIS Pro, ",
]

EXTRA_INTROS = [
    "In the context of map symbology, ",
    "For layout and export workflows, ",
    "Regarding geoprocessing in ArcGIS Pro, ",
    "When managing geodatabase data, ",
    "For sharing content from ArcGIS Pro, ",
]


def norm_text(s):
    if not s:
        return ""
    s = s.strip().lower()
    return re.sub(r"\s+", " ", s)


def load_seen():
    seen = set()
    if not os.path.isfile(QUESTIONS_PATH):
        return seen
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for q in data.get("questions", []):
        seen.add(norm_text(q.get("text", "")))
    return seen


def stem_with_intro(intro, stem):
    if not stem:
        return intro.rstrip()
    if stem[0].isupper():
        return intro + stem[0].lower() + stem[1:]
    return intro + stem


def parse_template(t):
    """Return (domain, stem, opts list of 4, correct_idx)."""
    if len(t) == 5:
        domain, stem, opts, correct_idx = t[0], t[1], t[2], t[3]
    else:
        domain, stem, opts = t[0], t[1], t[2]
        correct_idx = 0
    if len(opts) != 4:
        opts = (list(opts) + ["None of the above"] * 4)[:4]
    return domain, stem, opts, correct_idx


def build_combos(count, seen):
    out = []
    seed = 9000
    n_intro = len(INTROS)
    n_t = len(TEMPLATES)
    total_slots = n_intro * n_t
    for k in range(total_slots):
        if len(out) >= count:
            break
        intro = INTROS[k % n_intro]
        t = TEMPLATES[(k // n_intro) % n_t]
        domain, stem, opts, correct_idx = parse_template(t)
        text = stem_with_intro(intro, stem)
        nt = norm_text(text)
        if nt in seen:
            continue
        seen.add(nt)
        random.seed(seed)
        correct_val = opts[correct_idx]
        shuffled = list(opts)
        random.shuffle(shuffled)
        keys = ["a", "b", "c", "d"]
        correct_key = keys[shuffled.index(correct_val)]
        options = [{"key": kk, "text": shuffled[i]} for i, kk in enumerate(keys)]
        out.append({
            "domainId": domain,
            "text": text,
            "options": options,
            "correctKey": correct_key,
        })
        seed += 1

    ei = 0
    t_idx = 0
    while len(out) < count and ei < len(EXTRA_INTROS) * n_t * 3:
        intro = EXTRA_INTROS[ei % len(EXTRA_INTROS)]
        t = TEMPLATES[t_idx % n_t]
        domain, stem, opts, correct_idx = parse_template(t)
        text = stem_with_intro(intro, stem)
        nt = norm_text(text)
        if nt not in seen:
            seen.add(nt)
            random.seed(seed)
            correct_val = opts[correct_idx]
            shuffled = list(opts)
            random.shuffle(shuffled)
            keys = ["a", "b", "c", "d"]
            correct_key = keys[shuffled.index(correct_val)]
            options = [{"key": kk, "text": shuffled[i]} for i, kk in enumerate(keys)]
            out.append({
                "domainId": domain,
                "text": text,
                "options": options,
                "correctKey": correct_key,
            })
            seed += 1
        ei += 1
        t_idx += 1

    return out


def main():
    parser = argparse.ArgumentParser(
        description="Emit unique EAPF (ArcGIS Pro Foundation) questions as JSON array to stdout."
    )
    parser.add_argument("--count", "-n", type=int, default=400, help="Target number of questions (default: 400)")
    args = parser.parse_args()
    seen = load_seen()
    before = len(seen)
    out = build_combos(args.count, seen)
    if len(out) < args.count:
        print(
            "Warning: only generated {} unique questions (target {}). "
            "Add more INTROS or TEMPLATES.".format(len(out), args.count),
            file=sys.stderr,
        )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(
        "Emitted: {} (existing unique stems in bank before run: {})".format(len(out), before),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
