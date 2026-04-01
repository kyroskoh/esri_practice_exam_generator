"""Rewrite distractor phrasing that starts with 'Only …' so options do not telegraph wrong answers.

Distractors are authored following **eaep_distractor_design.py** (same technical domain as the stem;
plausible misconfigurations rather than unrelated product areas).
"""

import re


def rephrase_option(text):
    """Return distractor text unchanged; authored wording is used as-is."""
    return text


def rephrase_stem(text):
    """Adjust scenario stems that used 'Only' in ways that read like answer giveaways."""
    t = text
    t = re.sub(
        r"Only one region['\u2019]?s users report slowness\.\s*Others fine\.",
        "Users in one region report slowness. Other regions are unaffected.",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(
        r"(\[Diag case \d+\])\s+Only users from one AD site fail IWA",
        r"\1 Users at one AD site fail IWA",
        t,
    )
    t = re.sub(
        r"SAML logins fail after a daylight-saving change only for users in one region\.",
        "SAML logins fail after a daylight-saving change for users in one region.",
        t,
        flags=re.IGNORECASE,
    )
    return t


def rephrase_question_dict(raw):
    """Apply to a question object (mutates and returns). Used for CertFun JSON rows."""
    raw["text"] = rephrase_stem(raw["text"])
    for opt in raw.get("options", []):
        opt["text"] = rephrase_option(opt["text"])
    return raw
