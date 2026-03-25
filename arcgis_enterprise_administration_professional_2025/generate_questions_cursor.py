#!/usr/bin/env python3
"""
Generate EAEP 2025 practice questions using Cursor's in-editor model (no API key).

Flow:
  1. python generate_questions_cursor.py prompt [--count N]   → writes a prompt file
  2. Paste the prompt into Cursor Chat; ask the model to generate N questions
  3. Save the model's JSON output to a file (e.g. new_questions.json)
  4. python generate_questions_cursor.py merge <file> [--count N]   → appends to questions.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_QUESTIONS_BASENAME = "new_questions.json"
CURSOR_INSTRUCTION = (
    'Generate exactly the number of questions requested above. Output only a JSON array '
    'of question objects, no markdown code fence and no explanation before or after. Start with [ and end with ]. '
    'Save the output as new_questions.json'
)
QUESTIONS_PATH = os.path.join(SCRIPT_DIR, "questions.json")
EXAM_SPEC_PATH = os.path.join(SCRIPT_DIR, "exam-spec.json")
PROMPT_BASENAME = "prompt_for_cursor_questions.txt"

DOMAIN_IDS = [
    "deploy-enterprise",
    "troubleshoot-enterprise",
    "maintain-support-enterprise",
    "manage-content-users",
]

DOMAIN_DISTRIBUTION = {
    "deploy-enterprise": 34,
    "troubleshoot-enterprise": 18,
    "maintain-support-enterprise": 22,
    "manage-content-users": 26,
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_prompt(count, skip_content=False):
    spec = load_json(EXAM_SPEC_PATH)
    data = load_json(QUESTIONS_PATH)
    questions = data.get("questions", [])
    next_num = len(questions) + 1
    end_num = next_num + count - 1
    examples = questions[:3] if len(questions) >= 3 else questions

    domain_block = "\n".join(
        "- **{}** ({}%): {}".format(
            d["name"], d["weightPercent"],
            "; ".join(d.get("objectives", [])[:2]) or "See EIG."
        )
        for d in spec.get("domains", [])
    )

    domain_id_list = ", ".join(DOMAIN_IDS)

    prompt = """You are helping create practice questions for the ArcGIS Enterprise Administration Professional 2025 (EAEP_2025) exam.

## Exam domains and weights (distribute questions accordingly)
{domain_block}

## Required JSON format for each question
- "id": omit (will be assigned later)
- "domainId": one of: {domain_id_list}
- "text": question stem (one sentence, clear and specific)
- "options": array of exactly 4 objects, each: {{ "key": "a"|"b"|"c"|"d", "text": "option text" }}
- "correctKey": "a"|"b"|"c"|"d" (the key of the correct option)

## Example questions (match this structure exactly)
{examples}

## Task
Generate exactly **{count} new** practice questions for this exam. Rules:
- Distribute by domain: about 34% deploy-enterprise, 18% troubleshoot-enterprise, 22% maintain-support-enterprise, 26% manage-content-users.
- Each question must have exactly 4 options; one correct, three plausible distractors.
- Do not repeat or rephrase the example questions above.
- Do not duplicate the CertFun sample stems already in the bank as questions 1–10 (write original stems).
- Use only the four domainId values listed.
- Output **only** a JSON array of {count} objects. No markdown code fence, no explanation before or after. Start with [ and end with ].


---
Send this to the model (after pasting the prompt above):

{Cursor_instruction}
""".format(
        domain_block=domain_block,
        domain_id_list=domain_id_list,
        examples=json.dumps(examples, indent=2),
        count=count,
        Cursor_instruction=CURSOR_INSTRUCTION,
    )

    prompt_path = os.path.join(SCRIPT_DIR, PROMPT_BASENAME)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    script_name = os.path.basename(__file__)
    print("Wrote prompt to: " + prompt_path)
    print("\n--- Instructions (use Cursor free model, no API key) ---")
    print("1. Open " + prompt_path + " (or paste the content below) into Cursor Chat.")
    print("2. Send the message; ask the model to generate {} questions.".format(count))
    print("3. Copy the model's response (the JSON array only) and save to a file (e.g. new_questions.json) in this folder.")
    print("4. Run: python {} merge <path_to_file> [--count {}]".format(script_name, count))
    print("   This will append questions with ids q{}..q{} to questions.json.".format(next_num, end_num))
    if not skip_content:
        print("\n--- Prompt content (copy below) ---\n")
        print(prompt)
    return prompt_path


def strip_markdown_json(raw):
    raw = raw.strip()
    m = re.search(r"\[[\s\S]*\]", raw)
    if m:
        return m.group(0)
    return raw


def normalize_question(q, idx):
    domain_id = q.get("domainId") or ""
    if domain_id not in DOMAIN_IDS:
        domain_id = DOMAIN_IDS[idx % len(DOMAIN_IDS)]
    options = q.get("options") or []
    if len(options) != 4:
        return None
    keys = ["a", "b", "c", "d"]
    opts = []
    for i, k in enumerate(keys):
        o = options[i] if i < len(options) else {}
        opts.append({"key": k, "text": str(o.get("text", "") or "").strip() or "Option " + k})
    correct = str(q.get("correctKey") or "a").lower()
    if correct not in keys:
        correct = "a"
    text = (q.get("text") or "").strip()
    if not text:
        return None
    return {
        "domainId": domain_id,
        "text": text,
        "options": opts,
        "correctKey": correct,
    }


def merge(file_path, count):
    path = os.path.abspath(file_path)
    if not os.path.isfile(path):
        print("Error: file not found: " + path, file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    raw = strip_markdown_json(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("Error: invalid JSON in file: " + str(e), file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict) and "questions" in data:
        new_list = data["questions"]
    elif isinstance(data, list):
        new_list = data
    else:
        print("Error: file must contain a JSON array or object with 'questions' array.", file=sys.stderr)
        sys.exit(1)

    if count is not None:
        new_list = new_list[:count]

    existing = load_json(QUESTIONS_PATH)
    questions = existing.get("questions", [])
    start_id = len(questions) + 1
    added = 0

    for i, q in enumerate(new_list):
        normalized = normalize_question(q, i)
        if not normalized:
            continue
        normalized["id"] = "q{:d}".format(start_id + added)
        questions.append(normalized)
        added += 1

    existing["questions"] = questions
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    end_id = start_id + added - 1
    print("Merged {} questions into questions.json (ids q{}..q{}). Total: {}.".format(
        added, start_id, end_id, len(questions)))


def _open_prompt_file(prompt_path):
    path = os.path.abspath(prompt_path)
    if not os.path.isfile(path):
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except OSError:
        print("(Could not open file; open {} manually)".format(path))


def wizard(count, open_file, run_build):
    prompt_path = write_prompt(count, skip_content=True)
    print()

    if open_file:
        print("Opening prompt file...")
        _open_prompt_file(prompt_path)
        print()

    print("--- Do in Cursor Chat ---")
    print("1. Paste the prompt from the opened file (or from {}).".format(prompt_path))
    print("2. Send this to the model:")
    print('   "{}"'.format(CURSOR_INSTRUCTION))
    print("3. Copy the JSON array from the response (from [ to ] only).")
    print("4. Save it as {} in this folder.".format(NEW_QUESTIONS_BASENAME))
    print()
    try:
        input("Press Enter after you have saved {} to run merge (Ctrl+C to skip merge)... ".format(NEW_QUESTIONS_BASENAME))
    except KeyboardInterrupt:
        print("\nSkipped merge. Run: python {} merge {} when ready.".format(os.path.basename(__file__), NEW_QUESTIONS_BASENAME))
        return

    new_path = os.path.join(SCRIPT_DIR, NEW_QUESTIONS_BASENAME)
    if not os.path.isfile(new_path):
        print("Not found: {}. Run merge when ready: python {} merge {}".format(
            new_path, os.path.basename(__file__), NEW_QUESTIONS_BASENAME))
        return

    merge(new_path, count)

    if run_build:
        build_script = os.path.join(SCRIPT_DIR, "build_standalone.py")
        if os.path.isfile(build_script):
            print()
            subprocess.run([sys.executable, build_script], cwd=SCRIPT_DIR)
        else:
            print("(build_standalone.py not found; skip standalone build)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate practice questions via Cursor (prompt) or merge model output (merge)."
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    prompt_parser = subparsers.add_parser("prompt", help="Write a prompt file to paste into Cursor Chat")
    prompt_parser.add_argument(
        "--count", "-n", type=int, default=100, metavar="N",
        help="Number of questions to ask the model to generate (default: 100)"
    )

    merge_parser = subparsers.add_parser("merge", help="Merge a JSON file of questions into questions.json")
    merge_parser.add_argument("file", help="Path to JSON file (array or object with 'questions' array)")
    merge_parser.add_argument(
        "--count", "-n", type=int, default=None, metavar="N",
        help="Maximum number of questions to merge from the file (default: all)"
    )

    wizard_parser = subparsers.add_parser(
        "wizard",
        help="Automated flow: generate prompt, open file, then wait for new_questions.json and merge"
    )
    wizard_parser.add_argument(
        "--count", "-n", type=int, default=100, metavar="N",
        help="Number of questions to generate (default: 100)"
    )
    wizard_parser.add_argument(
        "--no-open", action="store_true",
        help="Do not open the prompt file automatically"
    )
    wizard_parser.add_argument(
        "--build", action="store_true",
        help="Run build_standalone.py after merge"
    )

    args = parser.parse_args()
    if args.cmd == "prompt":
        write_prompt(args.count)
    elif args.cmd == "merge":
        merge(args.file, args.count)
    elif args.cmd == "wizard":
        wizard(args.count, open_file=not args.no_open, run_build=args.build)


if __name__ == "__main__":
    main()
