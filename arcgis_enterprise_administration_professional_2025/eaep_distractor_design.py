#!/usr/bin/env python3
"""
EAEP question bank: distractor design rules and optional lint.

Design goals (same subsystem as the stem; plausible “almost right” wrong answers):

1. **Same problem domain** — Wrong options should address the same failure class as the stem
   (e.g. TLS/Web Adaptor/browser trust → chain, binding, SNI/SAN, mixed content, client URL—
   not licensing, relational data store, or portal sharing unless the stem involves those).

2. **Tricky, not random** — Prefer common misconfigurations, partial fixes, or wrong layer of the
   stack over unrelated product areas.

3. **No free elimination** — Avoid answers that could never apply to the scenario or that
   contradict basic platform facts in an obvious way.

4. **No cartographic red herrings for ops questions** — Do not use joke distractors such as
   north arrow, map rotation, legend patch size, or basemap color as wrong answers for
   Web Adaptor, backup, database, or federation issues. Those belong in cartography exams,
   not Enterprise administration.

Use this module when authoring or reviewing tuples:
(domainId, stem, correct, wrong1, wrong2, wrong3).

Run: python eaep_distractor_design.py
"""

import sys


def _lower(s):
    return (s or "").lower()


# Stem “theme” detectors (rough, for lint only).
def _stem_tls_cert(stem_l):
    """TLS / certificate / browser trust scenarios (do not use 'san' — matches 'SAN LUN')."""
    if "subject alternative" in stem_l:
        return True
    keys = (
        "tls",
        "ssl",
        "certificate",
        "pfx",
        "not secure",
        "cipher",
        "public ca",
        "self-signed",
        "handshake",
        "binding",
    )
    return any(k in stem_l for k in keys)


def _stem_oauth_saml(stem_l):
    keys = ("oauth", "redirect_uri", "saml", "idp", "enterprise login", "federated login")
    return any(k in stem_l for k in keys)


def _stem_data_store(stem_l):
    keys = (
        "data store",
        "relational",
        "tile cache",
        "hosted layer",
        "hosted feature",
        "hosted scene",
        "scene layer",
        "scene cache",
        "object store",
        "spatiotemporal",
    )
    return any(k in stem_l for k in keys)


def _stem_license(stem_l):
    keys = ("license", "licensing", "authorize", "provisioning", "named user")
    return any(k in stem_l for k in keys)


# Off-topic phrases in *wrong* options when stem theme is narrow.
_TLS_OFF_TOPIC = (
    "relational data store",
    "portal sharing",
    "not licensed",
    "license manager",
    "tile cache data store is full",
    "hosting server is offline",
    "kml capability",
)


def _tls_warnings(i, wl, stem_l):
    out = []
    for phrase in _TLS_OFF_TOPIC:
        if phrase in wl and phrase not in stem_l:
            out.append("wrong{}: '{}' looks off-topic for a TLS/cert stem".format(i, phrase))
    return out


_OAUTH_REDIRECT_OFF_TOPIC = (
    "tile cache data store is full",
    "hosting server is offline",
    "arcgis license manager",
    "relational data store",
)


def _oauth_redirect_warnings(i, wl):
    out = []
    for phrase in _OAUTH_REDIRECT_OFF_TOPIC:
        if phrase in wl:
            out.append(
                "wrong{}: '{}' often reads as unrelated to redirect/OAuth symptoms".format(i, phrase)
            )
    return out


def lint_tuple(_domain, stem, _correct, w1, w2, w3):
    """Return human-readable warning strings for suspicious distractors."""
    stem_l = _lower(stem)
    warnings = []
    wrongs = [w1, w2, w3]

    tls = _stem_tls_cert(stem_l) and not _stem_data_store(stem_l) and not _stem_license(stem_l)
    oauth_redirect = (
        ("redirect_uri" in stem_l or "redirect uri" in stem_l or "redirect" in stem_l)
        and ("oauth" in stem_l or "saml" in stem_l or "portal" in stem_l)
    )

    for i, w in enumerate(wrongs, 1):
        wl = _lower(w)
        if tls:
            warnings.extend(_tls_warnings(i, wl, stem_l))
        if oauth_redirect:
            warnings.extend(_oauth_redirect_warnings(i, wl))

    return warnings


def iter_all_bank_tuples():
    """Import scenario modules and yield (source_name, domain, stem, c, w1, w2, w3)."""
    from eaep_extra_100_case_study import get_extra_100_case_study_scenarios
    from eaep_extra_100_ops import get_extra_100_ops_scenarios
    from eaep_extra_100_skills import get_extra_100_skills_scenarios
    from eaep_extra_200 import get_extra_200_scenarios
    from eaep_extra_400 import get_extra_400_scenarios

    from build_eaep_scenario_bank import SCENARIO_SPECS

    for t in SCENARIO_SPECS:
        yield ("SCENARIO_SPECS",) + t
    for fn, getter in (
        ("eaep_extra_400", get_extra_400_scenarios),
        ("eaep_extra_100_case_study", get_extra_100_case_study_scenarios),
        ("eaep_extra_200", get_extra_200_scenarios),
        ("eaep_extra_100_ops", get_extra_100_ops_scenarios),
        ("eaep_extra_100_skills", get_extra_100_skills_scenarios),
    ):
        for row in getter():
            yield (fn,) + row


def main():
    total = 0
    flagged = 0
    by_source = {}
    for row in iter_all_bank_tuples():
        src = row[0]
        domain, stem, c, w1, w2, w3 = row[1:7]
        total += 1
        msgs = lint_tuple(domain, stem, c, w1, w2, w3)
        if msgs:
            flagged += 1
            by_source[src] = by_source.get(src, 0) + 1
            for m in msgs:
                print("{} | {} | {}".format(src, stem[:60] + "..." if len(stem) > 60 else stem, m))

    print("---")
    print("Linted {} scenarios; {} rows flagged (heuristic).".format(total, flagged))
    print("By source: {}".format(dict(sorted(by_source.items()))))


if __name__ == "__main__":
    import os

    _dir = os.path.dirname(os.path.abspath(__file__))
    if _dir not in sys.path:
        sys.path.insert(0, _dir)
    main()
