# Product Requirements: ArcGIS Enterprise Administration Professional 2025 Practice Test

## Purpose

Provide a lightweight, offline-capable practice test for the **ArcGIS Enterprise Administration Professional 2025 (EAEP_2025)** certification exam. Users run the test from HTML plus a JSON question bank (or a generated single-file standalone), without Node.js. **This product is unofficial study material**; see repository `LICENSING.md` for affiliation and trademark notices.

## Scope

- **In scope:** Practice UI; load bank via `fetch`, file picker, or embedded standalone; **75** questions per attempt (matching real exam count); shuffle question order and option order; score and per-option feedback; Python scripts to build the bank and standalone HTML.
- **Out of scope:** Timed mode, score persistence, accounts, proctoring, or official Esri exam delivery.

## Users

- Candidates preparing for EAEP_2025.
- Administrators who want **domain-weighted**, **scenario-style** practice aligned to the EIG.

## Goals

1. Match **real exam mechanics:** 75 questions per session, multiple choice, **105 minutes** on the label (timer not enforced in-app), **65% passing score (scored)** reflected in `exam-spec.json` and the submit score card.
2. Match **EIG domain weights** within each authored segment of the **default question bank** (Deploy 34%, Troubleshoot 18%, Maintain and Support 22%, Manage Content and Users 26% on the 90-item core block and separately on the 400-item extended block).
3. Prefer **best-answer** practice: plausible wrong options and production-relevant stems for scenario items—not only definitional recall.
4. Single source of truth: **`questions.json`** for bank data; **`practice-test.html`** does not embed the bank; **`practice-test-standalone.html`** embeds it for `file://` use.
5. Runtime: HTML/CSS/JS only; Python used **offline** to generate or merge JSON and to build the standalone file.

## Question content (requirements)

| Aspect | Requirement |
|--------|-------------|
| **Domains** | Items use `domainId` values from `exam-spec.json`: `deploy-enterprise`, `troubleshoot-enterprise`, `maintain-support-enterprise`, `manage-content-users`. |
| **Default bank composition** | **1000** items: **10** scenario-style items from `old_questions.json`; **90** `SCENARIO_SPECS`; **400** `eaep_extra_400.py`; **100** `eaep_extra_100_case_study.py`; **200** `eaep_extra_200.py`; **100** `eaep_extra_100_ops.py`; **100** `eaep_extra_100_skills.py`; domain weights hold per segment where authored. |
| **Scenario style** | Stems describe realistic constraints (operations, architecture, security, collaboration). Correct answer is the **most appropriate** action or explanation for the situation; distractors remain plausible. No mandatory `Case:` prefix on stems. |
| **Opening block (q1–q10)** | First 10 questions in `old_questions.json` (scenario/case-study stems) are merged as **q1–q10** when running `build_eaep_scenario_bank.py`. |
| **Supplementary generators** | `generate_questions.py` / `emit_bulk_questions.py` produce **template drill** items for volume; documented as lower fidelity than scenario bank for “exam feel.” |
| **Cursor workflow** | `generate_questions_cursor.py` + `prompt_for_cursor_questions.txt` instruct models to emit **case-study / best-answer** JSON for merges. |

## Functional Requirements

| ID | Requirement | Notes |
|----|-------------|--------|
| FR-1 | Load `questions.json` over HTTP/HTTPS when served. | `fetch`; same origin. |
| FR-2 | If `fetch` fails (`file://`), show error UI + file input to load JSON. | `practice-test.html`. |
| FR-2b | Provide `practice-test-standalone.html` with embedded bank for `file://` without fetch or picker. | `build_standalone.py`. |
| FR-3 | Each exam shows **75** questions drawn at random from the bank (or every item if the bank has fewer than 75). | `EXAM_QUESTION_COUNT = 75`. |
| FR-4 | Shuffle order of selected questions and shuffle option keys **a–d** while preserving correct mapping. | Implemented in page script. |
| FR-5 | Submit shows score and per-option correct/incorrect. | Submit + inline labels. |
| FR-6 | Reset clears selections and score for current 75 without redraw. | Reset button. |
| FR-7 | New exam draws a new random 75 without reload. | New exam button. |
| FR-8 | Meta line shows bank size, current exam size, duration from `EXAM_SPEC`, format. | `updateMetaLine()`. |
| FR-9 | Each item shows **domain tag** (human-readable name from spec), stem, four options **a–d**. | From `domainId` + `exam-spec` domains. |

## Data and Sources of Truth

- **Exam structure:** `exam-spec.json` and inline spec in `practice-test.html`: 75 questions, 105 min, **passingScorePercent** 65, four domains with **weightPercent** and objectives.
- **Question bank:** `questions.json` — `{ "examId", "source", "questions": [ { "id", "domainId", "text", "options", "correctKey" } ] }`.
- **Scenario source code:** `build_eaep_scenario_bank.py` (`SCENARIO_SPECS`) + `eaep_extra_*.py` modules + CertFun rows from `old_questions.json`.
- **Session state:** In-memory only; not persisted.

## Non-Functional Requirements

- **Portability:** Modern browsers; optional Python 3 for maintenance scripts.
- **No embedded bank in main HTML template** except via `build_standalone.py` output.
- **Errors:** Invalid JSON or empty bank → clear message; no silent exam start.

## Scripts (maintenance)

- **`build_eaep_scenario_bank.py`** — Rebuild `questions.json` (q1–q10 from `old_questions.json` + 90 scenarios + domain mix). Then **`build_standalone.py`**.
- **`generate_help.py`** — Short usage for merge, Cursor, emit-bulk, rebuild.
- **`generate_questions_cursor.py`** — `prompt` / `merge` / `wizard` for appending model-generated scenario-style JSON.
- **`generate_questions.py`** — Template-only output for drills; merge optional.
- **`emit_bulk_questions.py`** — Intro × template combinations for volume; merge optional.

## Constraints

- Local `file://` cannot `fetch` sibling JSON; use standalone build or file picker.
- Each question must include `id`, `domainId`, `text`, four `options`, `correctKey`.

## References

- [Esri Academy – ArcGIS Enterprise Administration Professional 2025](https://www.esri.com/training/catalog/67e2da62d6844f1703724c6f/arcgis-enterprise-administration-professional-2025/)
- [EAEP 2025 EIG (PDF)](https://community.esri.com/t5/esri-technical-certification-exams/eaep-2025-eig/ba-p/1595261)
- q1–q10 source: first 10 rows of `old_questions.json` (described in `questions.json` `source` string)
