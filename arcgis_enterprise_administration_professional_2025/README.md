# ArcGIS Enterprise Administration Professional 2025 (EAEP_2025) Practice Test

Practice materials for the **ArcGIS Enterprise Administration Professional 2025** exam (EAEP_2025), aligned to the Exam Information Guide ([EAEP2025_EIG_JAN2026.pdf](https://community.esri.com/t5/esri-technical-certification-exams/eaep-2025-eig/ba-p/1595261)). Same delivery pattern as `arcgis_pro_foundation_2025`: single-page HTML; optional local server; standalone build for `file://`.

**Developer:** Kyros

Legal / affiliation: see repository root **[LICENSING.md](../LICENSING.md)**. This practice test is **not** affiliated with Esri or certification vendors.

## Place the EIG PDF locally

Download **EAEP2025_EIG_JAN2026.pdf** from the [Esri Community EAEP 2025 EIG article](https://community.esri.com/t5/esri-technical-certification-exams/eaep-2025-eig/ba-p/1595261) and save it in this folder as `EAEP2025_EIG_JAN2026.pdf` so it matches `exam-spec.json`.

## Contents

| File | Description |
|------|-------------|
| `EAEP2025_EIG_JAN2026.pdf` | Official Esri Exam Information Guide (place locally; see above). |
| `exam-spec.json` | Exam metadata and **domain weights** from the EIG (objectives listed per domain). |
| `questions.json` | **1000** questions: **q1–q10** scenario/case-study stems from `old_questions.json` (four options each); **q11–q100** core; **q101–q500** `eaep_extra_400.py`; **q501–q600** `eaep_extra_100_case_study.py`; **q601–q800** `eaep_extra_200.py`; **q801–q900** `eaep_extra_100_ops.py`; **q901–q1000** `eaep_extra_100_skills.py` (EIG skills-measured themes: Monitor, data stores, federation, airgap, collaboration, usage, publishing access). Domain mix **34% / 18% / 22% / 26%** per segment where authored. Rebuild with `build_eaep_scenario_bank.py`. |
| `practice-test.html` | UI: loads `questions.json` or file picker when `file://`. |
| `practice-test-standalone.html` | Single file, bank embedded. Build: `python build_standalone.py`. |
| `build_standalone.py` | Embeds `questions.json` into standalone HTML. |
| `serve.py` | Local HTTP server for `practice-test.html`. |
| `build_eaep_scenario_bank.py` | **Primary bank builder:** **q1–q10** from `old_questions.json` + **90** `SCENARIO_SPECS` + **400** + **100** case-study + **200** + **100** ops + **100** skills (`eaep_extra_*.py`). Uses `eaep_text_rephrase.py`. Then run `build_standalone.py`. |
| `eaep_distractor_design.py` | **Distractor rules** (wrong answers stay in the same technical domain as the stem). Run `python eaep_distractor_design.py` for heuristic lint over all scenario tuples. |
| `eaep_text_rephrase.py` | Build-time rewrite of “Only …” option text so distractors do not telegraph as obviously wrong. |
| `eaep_extra_400.py` | **400** additional weighted scenarios (programmatic stems). |
| `eaep_extra_100_case_study.py` | **100** case-study-style scenarios. |
| `eaep_extra_200.py` | **200** themed scenarios (licensing counts, auth design, DR blank tiles, upgrade paths, collaboration workspaces, Enterprise Builder/cloud, hosted 3D/cache/web layers). |
| `eaep_extra_100_ops.py` | **100** scenarios: portal usage vs ArcGIS Monitor, firewall/DMZ and **443** vs **6443/7443**, maintenance windows, Server Manager vs Portal admin, groups/roles/sharing, WebGISDR, tokens, LDAP, WebContextURL, ArcGIS Server account. |
| `eaep_extra_100_skills.py` | **100** scenarios aligned to EIG **Skills Measured** weights (34/18/22/26): deploy, troubleshoot, maintain, manage—airgap authorization, federation/additional sites, data stores, Web Adaptor/OAuth, Monitor vs usage reports, collaboration, content sharing, publishing/SDE/layer package access. |
| `old_questions.json` | **First 10** rows supply **q1–q10** (scenario-style stems, four options each); remaining rows are archive/merge source if used elsewhere. |
| `generate_questions_cursor.py` | Cursor **prompt** / **merge** for **new** questions (append to bank). |
| `prompt_for_cursor_questions.txt` | Generated prompt: **case-study / best-answer** style. Regenerate: `python generate_questions_cursor.py prompt [--count N]`. |
| `generate_questions.py` | **Template drills** (short factual stems)—supplementary; not the same as the scenario bank. See docstring in file. |
| `emit_bulk_questions.py` | High volume: intro phrases × templates from `generate_questions.py`; merge for extra drills. |
| `generate_help.py` | Command summary. |
| `PRD.md` | Product requirements. |

## Exam at a glance (from EIG)

- **Questions:** 75  
- **Duration:** 1 hour 45 minutes (105 minutes)  
- **Format:** Multiple choice  
- **Passing score:** 65% (scored), per Esri’s published exam summary  
- **Domains and weight:**  
  - Deploy ArcGIS Enterprise **34%**  
  - Troubleshoot ArcGIS Enterprise **18%**  
  - Maintain and Support ArcGIS Enterprise **22%**  
  - Manage Content and Users in ArcGIS Enterprise **26%**

Official summary: [ArcGIS Enterprise Administration Professional 2025 – Esri Academy](https://www.esri.com/training/catalog/67e2da62d6844f1703724c6f/arcgis-enterprise-administration-professional-2025/).

## Question bank (requirements this repo targets)

| Layer | Role |
|--------|------|
| **Opening block (q1–q10)** | Scenario/case-study stems (four options each), loaded from the first 10 rows of `old_questions.json`. External [CertFun samples](https://www.certfun.com/esri/esri-arcgis-enterprise-administration-professional-eaep-2025-certification-sample-questions) are a useful topic reference, not verbatim text. |
| **Scenarios (q11–q100)** | Core **production-style** stems. Same style as below; counts match EIG on the 90-item segment. |
| **Extra scenarios (q101–q500)** | From `eaep_extra_400.py`: **SSO/SAML/OAuth**, **enterprise/IWA**, **AD/LDAP**, **3D/scene/tile cache**, **WebGISDR/backup/DR**, etc. Weights **34% / 18% / 22% / 26%** on the 400-item segment. |
| **Case-study block (q501–q600)** | From `eaep_extra_100_case_study.py`: longer, layered **production-style** stems. |
| **Themed block (q601–q800)** | From `eaep_extra_200.py`: licensing arithmetic, SAML/IWA/built-in, DR/restore and blank-cache symptoms, version upgrade discipline, parent/distributed collaboration, Enterprise Builder and cloud ops, hosted 3D / web layers / caching. |
| **Ops block (q801–q900)** | From `eaep_extra_100_ops.py`: usage vs Monitor, DMZ/port **443** patterns, maintenance windows, WebGISDR, administrative groups, portal groups and sharing, tokens, LDAP, WebContext, Server account. |
| **Skills block (q901–q1000)** | From `eaep_extra_100_skills.py`: full EIG domain mix on a dedicated segment—federation, data stores, Web Adaptor, troubleshooting with Monitor, backups/upgrades, collaboration and content access patterns. |

**Rebuild default bank:** `python build_eaep_scenario_bank.py` then `python build_standalone.py`. Edit **`SCENARIO_SPECS`** and the **`eaep_extra_*.py`** modules to change scenarios.

## How to use the practice test

**Standalone:** open `practice-test-standalone.html` (after `build_standalone.py` if you changed the bank).

**Two-file:** open `practice-test.html`; use `python serve.py` or the file picker for `questions.json`.

Each run draws **75** random questions from the bank (**1000** items available).

## Adding or generating questions

1. **Scenario items (exam-like):** edit `SCENARIO_SPECS` and rebuild with `build_eaep_scenario_bank.py`, **or** use Cursor: `python generate_questions_cursor.py prompt`, paste into Chat, save JSON, `python generate_questions_cursor.py merge new_questions.json`, then `build_standalone.py`. The prompt emphasizes **best answer** and **realistic distractors** (`prompt_for_cursor_questions.txt`).
2. **Template drills (volume):** `python generate_questions.py` → merge; or `emit_bulk_questions.py` → merge. See `generate_help.py`.

## References

- [Esri Academy – ArcGIS Enterprise Administration Professional 2025](https://www.esri.com/training/catalog/67e2da62d6844f1703724c6f/arcgis-enterprise-administration-professional-2025/)  
- [Esri Community – EAEP 2025 EIG](https://community.esri.com/t5/esri-technical-certification-exams/eaep-2025-eig/ba-p/1595261)  
- [CertFun – EAEP_2025 sample questions](https://www.certfun.com/esri/esri-arcgis-enterprise-administration-professional-eaep-2025-certification-sample-questions) (external topic reference; q1–q10 are original scenario stems in this repo)
