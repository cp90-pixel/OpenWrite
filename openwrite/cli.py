"""Command line interface for the grammar checker."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

from .grammar_checker import GrammarChecker, GrammarIssue


def _format_issue(issue: GrammarIssue, index: int) -> str:
    location = f"{issue.start}-{issue.end}"
    context = issue.context.strip()
    return (
        f"{index}. [{issue.rule}] {issue.message}\n"
        f"   Location: {location}\n"
        f"   Context: {context}"
    )


def run_checker(text: str) -> Iterable[GrammarIssue]:
    checker = GrammarChecker()
    return checker.check(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check text for common grammar issues.")
    parser.add_argument(
        "path",
        nargs="?",
        help="Optional path to a text file. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Display the context snippet for each issue.",
    )
    args = parser.parse_args(argv)

    if args.path:
        text_path = Path(args.path)
        try:
            text = text_path.read_text(encoding="utf-8")
        except OSError as exc:  # pragma: no cover - user input handling
            print(f"Failed to read {text_path}: {exc}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    issues = run_checker(text)

    if not issues:
        print("No grammar issues found.")
        return 0

    print(f"Found {len(issues)} potential issue(s):")
    for index, issue in enumerate(issues, start=1):
        message = _format_issue(issue, index)
        if not args.show_context:
            message = message.splitlines()[0]
        print(message)

    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
