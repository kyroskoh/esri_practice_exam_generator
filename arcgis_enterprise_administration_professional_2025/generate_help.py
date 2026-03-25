#!/usr/bin/env python3
"""
Helper script: print usage for EAEP 2025 question generation and merge.
Run with --help or -h for this message.
"""
import argparse

HELP_TEXT = """
EAEP 2025 – Question generation

Default (generate 100 questions, then merge):
  python generate_questions.py > new_questions.json 2>&1 && python generate_questions_cursor.py merge new_questions.json

Template-based (generate only):
  python generate_questions.py [--count N] [--start N]
  python generate_questions.py --help

Cursor-assisted (prompt + merge):
  python generate_questions_cursor.py wizard
  python generate_questions_cursor.py prompt [--count N]
  python generate_questions_cursor.py merge <file> [--count N]
  python generate_questions_cursor.py --help

Bulk emit (unique vs existing bank):
  python emit_bulk_questions.py --count 400 > new_questions.json && python generate_questions_cursor.py merge new_questions.json

Other:
  python build_standalone.py   # refresh standalone HTML after updating questions.json
  python serve.py             # run local server for practice-test.html
"""


def main():
    parser = argparse.ArgumentParser(
        description="EAEP 2025 practice test – question generation helper.",
        epilog="For full options: python generate_questions.py --help ; python generate_questions_cursor.py --help",
    )
    parser.parse_args()
    print(HELP_TEXT.strip())


if __name__ == "__main__":
    main()
