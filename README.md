# Esri practice exam generator

Self-contained practice tests for selected **Esri Technical Certification** exams. Each exam lives in its own folder with a browser-based UI, JSON question bank, optional Python helpers to grow the bank, and materials aligned to the official Exam Information Guide (EIG).

This project is **not affiliated with Esri** or any certification body, partner, or third-party sample site. Certification names refer to Esri’s public program for identification only. Full notices, trademarks, and license terms: **[LICENSING.md](LICENSING.md)**.

## Exams in this repository

| Folder | Exam | Code |
|--------|------|------|
| [arcgis_pro_foundation_2025](arcgis_pro_foundation_2025/README.md) | ArcGIS Pro Foundation 2025 | EAPF_2025 |
| [arcgis_enterprise_administration_professional_2025](arcgis_enterprise_administration_professional_2025/README.md) | ArcGIS Enterprise Administration Professional 2025 | EAEP_2025 |

Open the linked README for exam structure, question counts, how to run the test, and how to add questions.

## Practice online (GitHub Pages)

Direct links to the standalone practice tests (question bank embedded in the page):

- [ArcGIS Pro Foundation 2025 (EAPF_2025) — practice test](https://kyroskoh.github.io/esri_practice_exam_generator/arcgis_pro_foundation_2025/practice-test-standalone.html)
- [ArcGIS Enterprise Administration Professional 2025 (EAEP_2025) — practice test](https://kyroskoh.github.io/esri_practice_exam_generator/arcgis_enterprise_administration_professional_2025/practice-test-standalone.html)

## Quick start (local)

1. Open the exam folder.
2. Open **`practice-test-standalone.html`** in a browser (double-click or drag into the window). The question bank is embedded; no web server or file picker is required.
3. Alternatively, use **`practice-test.html`** with a local server (`python serve.py` in that folder) or load `questions.json` via the file picker when opening the file as `file://`.

## Requirements

- **To take a practice:** a modern browser (Chrome, Edge, Firefox, Safari).
- **To rebuild the standalone HTML or merge new questions:** Python 3. See each folder’s README (for example `build_standalone.py`, `build_eaep_scenario_bank.py` for EAEP, `generate_questions_cursor.py`, `emit_bulk_questions.py`).

## Developer

Kyros
