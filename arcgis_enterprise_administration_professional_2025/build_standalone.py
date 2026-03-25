#!/usr/bin/env python3
"""
Build a single-file practice test that works when opened via file://.
Reads questions.json and practice-test.html; writes practice-test-standalone.html
with the question bank embedded so no fetch or file picker is needed.
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(SCRIPT_DIR, "questions.json")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "practice-test.html")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "practice-test-standalone.html")

MARKER = "var questionBank = [];"


def main():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])
    if not questions:
        raise SystemExit("questions.json has no 'questions' array or it is empty")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    embedded_json = json.dumps(questions, ensure_ascii=False)
    embedded_json = embedded_json.replace("</script>", "</scr\" + \"ipt>")

    replacement = (
        "var EMBEDDED_QUESTIONS = "
        + embedded_json
        + ";\n      var questionBank = EMBEDDED_QUESTIONS.slice();"
    )
    if MARKER not in html:
        raise SystemExit("Template does not contain expected marker: " + MARKER)
    html = html.replace(MARKER, replacement, 1)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote " + OUTPUT_PATH + " (" + str(len(questions)) + " questions embedded)")


if __name__ == "__main__":
    main()
