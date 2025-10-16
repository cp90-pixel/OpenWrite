"""Rule-based grammar checker implementation."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, List


@dataclass
class GrammarIssue:
    """Represents a single grammar issue discovered in the text."""

    rule: str
    message: str
    start: int
    end: int
    context: str

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        return f"[{self.rule}] {self.message} (position {self.start}:{self.end})"


class GrammarChecker:
    """A lightweight grammar checker built on heuristic rules.

    The checker focuses on frequent grammar mistakes such as repeated words,
    missing capitalization, missing sentence-ending punctuation, double spaces
    and excessively long sentences that may indicate run-ons.
    """

    _double_space_pattern = re.compile(r" {2,}")
    _repeated_word_pattern = re.compile(r"\b([A-Za-z']+)\b(\s+\1\b)+", re.IGNORECASE)

    def check(self, text: str) -> List[GrammarIssue]:
        """Inspect *text* and return any detected grammar issues."""

        issues: List[GrammarIssue] = []
        issues.extend(self._find_double_spaces(text))
        sentences = list(self._sentence_spans(text))

        for start, end in sentences:
            sentence = text[start:end]
            stripped_sentence = sentence.strip()
            if not stripped_sentence:
                continue

            issues.extend(self._check_sentence_capitalization(sentence, start))
            issues.extend(self._check_sentence_punctuation(sentence, start))
            issues.extend(self._check_repeated_words(sentence, start))
            issues.extend(self._check_sentence_length(sentence, start))

        return sorted(issues, key=lambda issue: issue.start)

    def _find_double_spaces(self, text: str) -> Iterable[GrammarIssue]:
        for match in self._double_space_pattern.finditer(text):
            start, end = match.span()
            context = self._issue_context(text, start, end)
            yield GrammarIssue(
                rule="double-space",
                message="Multiple consecutive spaces detected.",
                start=start,
                end=end,
                context=context,
            )

    def _check_sentence_capitalization(self, sentence: str, offset: int) -> Iterable[GrammarIssue]:
        stripped = sentence.lstrip()
        if not stripped:
            return []
        leading_ws = len(sentence) - len(stripped)
        first_char = stripped[0]
        if first_char.isalpha() and not first_char.isupper():
            start = offset + leading_ws
            end = start + 1
            context = self._issue_context(sentence, leading_ws, leading_ws + 1)
            return [
                GrammarIssue(
                    rule="capitalization",
                    message="Sentence should start with a capital letter.",
                    start=start,
                    end=end,
                    context=context,
                )
            ]
        return []

    def _check_sentence_punctuation(self, sentence: str, offset: int) -> Iterable[GrammarIssue]:
        stripped = sentence.rstrip()
        if not stripped:
            return []
        trailing_ws = len(sentence) - len(stripped)
        core = stripped.rstrip("\"'”’)")
        if not core:
            return []
        last_char = core[-1]
        if last_char not in ".!?":
            end = offset + len(sentence) - trailing_ws
            context = self._issue_context(sentence, 0, len(sentence) - trailing_ws)
            return [
                GrammarIssue(
                    rule="punctuation",
                    message="Sentence should end with terminal punctuation.",
                    start=end - 1,
                    end=end,
                    context=context,
                )
            ]
        return []

    def _check_repeated_words(self, sentence: str, offset: int) -> Iterable[GrammarIssue]:
        for match in self._repeated_word_pattern.finditer(sentence):
            start, end = match.span()
            context = self._issue_context(sentence, start, end)
            word = match.group(1)
            yield GrammarIssue(
                rule="repeated-word",
                message=f"Repeated word '{word}'.",
                start=offset + start,
                end=offset + end,
                context=context,
            )

    def _check_sentence_length(self, sentence: str, offset: int) -> Iterable[GrammarIssue]:
        words = [w for w in re.findall(r"\b\w+\b", sentence)]
        if len(words) > 40:
            start = offset
            end = offset + len(sentence)
            context = self._issue_context(sentence, 0, len(sentence))
            yield GrammarIssue(
                rule="long-sentence",
                message="Sentence is long and may be a run-on.",
                start=start,
                end=end,
                context=context,
            )

    def _sentence_spans(self, text: str) -> Iterable[tuple[int, int]]:
        pattern = re.compile(r"[^.!?]+(?:[.!?]|$)", re.MULTILINE)
        for match in pattern.finditer(text):
            raw = match.group()
            stripped = raw.strip()
            if not stripped:
                continue
            leading_ws = len(raw) - len(raw.lstrip())
            trailing_ws = len(raw) - len(raw.rstrip())
            start = match.start() + leading_ws
            end = match.end() - trailing_ws
            if start < end:
                yield start, end

    @staticmethod
    def _issue_context(source: str, start: int, end: int, padding: int = 30) -> str:
        context_start = max(0, start - padding)
        context_end = min(len(source), end + padding)
        snippet = source[context_start:context_end]
        return snippet.replace("\n", " ")


__all__ = ["GrammarChecker", "GrammarIssue"]
