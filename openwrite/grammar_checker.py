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

    _present_auxiliaries = {"am", "is", "are", "has", "have", "does", "do"}
    _past_auxiliaries = {"was", "were", "had", "did"}
    _present_base_verbs = {
        "walk",
        "talk",
        "run",
        "go",
        "come",
        "make",
        "take",
        "write",
        "speak",
        "think",
        "know",
        "feel",
        "see",
        "eat",
        "give",
        "use",
        "find",
        "tell",
        "look",
        "work",
        "live",
        "love",
        "like",
        "need",
        "want",
        "call",
        "ask",
        "play",
        "move",
        "create",
        "study",
        "build",
        "learn",
    }
    _present_s_verbs = {
        "walks",
        "talks",
        "runs",
        "goes",
        "comes",
        "makes",
        "takes",
        "writes",
        "speaks",
        "thinks",
        "knows",
        "feels",
        "sees",
        "eats",
        "gives",
        "uses",
        "finds",
        "tells",
        "looks",
        "works",
        "lives",
        "loves",
        "likes",
        "needs",
        "wants",
        "calls",
        "asks",
        "plays",
        "moves",
        "creates",
        "studies",
        "builds",
        "learns",
    }
    _irregular_past_verbs = {
        "went",
        "saw",
        "ate",
        "ran",
        "spoke",
        "wrote",
        "took",
        "made",
        "bought",
        "brought",
        "felt",
        "thought",
        "knew",
        "kept",
        "left",
        "lost",
        "paid",
        "said",
        "told",
        "found",
        "gave",
        "came",
    }
    _ed_adjective_exceptions = {
        "tired",
        "excited",
        "interested",
        "pleased",
        "prepared",
        "advanced",
        "experienced",
        "related",
        "married",
        "beloved",
        "belated",
        "concerned",
        "opposed",
        "supposed",
        "mixed",
        "fixed",
        "learned",
        "used",
        "detailed",
        "gifted",
        "honored",
        "increased",
        "creed",
    }
    _pronouns = {"i", "you", "he", "she", "it", "we", "they"}
    _possessive_determiners = {"my", "your", "his", "her", "its", "our", "their"}
    _connectors = {"and", "or", "but", "so", "yet", "nor", "also", "still", "then"}
    _modals = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
    _subordinate_markers = {
        "that",
        "which",
        "who",
        "whom",
        "whose",
        "where",
        "wherever",
        "when",
        "whenever",
        "while",
        "because",
        "since",
        "although",
        "though",
        "whereas",
        "if",
        "before",
        "after",
        "once",
        "until",
        "unless",
        "as",
        "than",
        "whether",
    }

    _auxiliary_markers = {
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "has",
        "have",
        "had",
    }

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
            issues.extend(self._check_verb_tense(sentence, start))

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

    def _check_verb_tense(self, sentence: str, offset: int) -> Iterable[GrammarIssue]:
        tokens = list(re.finditer(r"\b[A-Za-z']+\b", sentence))
        if len(tokens) < 2:
            return []

        present_markers: list[tuple[int, re.Match[str]]] = []
        past_markers: list[tuple[int, re.Match[str]]] = []

        for index, match in enumerate(tokens):
            word = match.group(0)
            lower = word.lower()

            if self._is_present_marker(lower, tokens, index):
                present_markers.append((index, match))
            elif self._is_past_marker(lower, tokens, index):
                past_markers.append((index, match))

        if present_markers and past_markers:
            for past_index, past_match in past_markers:
                for present_index, present_match in present_markers:
                    if not self._markers_in_same_clause(tokens, past_index, present_index):
                        continue
                    issue_start = min(past_match.start(), present_match.start())
                    issue_end = max(past_match.end(), present_match.end())
                    context = self._issue_context(sentence, issue_start, issue_end)
                    return [
                        GrammarIssue(
                            rule="verb-tense",
                            message="Sentence mixes past and present tense verbs.",
                            start=offset + issue_start,
                            end=offset + issue_end,
                            context=context,
                        )
                    ]

        return []

    def _markers_in_same_clause(
        self, tokens: List[re.Match[str]], first_index: int, second_index: int
    ) -> bool:
        low = min(first_index, second_index)
        high = max(first_index, second_index)
        for i in range(low + 1, high):
            word = tokens[i].group(0).lower()
            if word in self._subordinate_markers:
                return False
        return True

    def _is_present_marker(
        self, word: str, tokens: List[re.Match[str]], index: int
    ) -> bool:
        if word in self._present_auxiliaries:
            prev = self._previous_content_word(tokens, index)
            if word in {"has", "have"} and prev in {"there"}:
                return False
            return True

        if word in self._present_s_verbs:
            prev = self._previous_content_word(tokens, index)
            if prev in self._possessive_determiners:
                return False
            return prev != "to"

        if word in self._present_base_verbs:
            prev = self._previous_content_word(tokens, index)
            if prev in self._pronouns:
                return True
            if prev in {"to", "does", "do"}:
                return False
            if prev in self._modals or prev in self._auxiliary_markers:
                return False
            if prev in {"the", "a", "an", "this", "that", "these", "those"}:
                prev = self._previous_content_word(tokens, index, steps=2)
                if prev in self._possessive_determiners:
                    return False
            if prev and prev[0].isupper():
                return True
            if prev and prev not in self._connectors and prev not in self._pronouns:
                return True
        return False

    def _is_past_marker(
        self, word: str, tokens: List[re.Match[str]], index: int
    ) -> bool:
        if word in self._past_auxiliaries:
            return True

        if word in self._irregular_past_verbs:
            prev = self._previous_content_word(tokens, index)
            if word == "found" and prev == "newly":
                return False
            if prev in self._subordinate_markers:
                return False
            return True

        if word.endswith("ed") and len(word) > 3 and word not in self._ed_adjective_exceptions:
            if self._is_part_of_perfect_or_passive(tokens, index):
                return False
            prev = self._previous_content_word(tokens, index)
            if prev in self._subordinate_markers:
                return False
            return True

        return False

    def _previous_content_word(
        self, tokens: List[re.Match[str]], index: int, *, steps: int = 1
    ) -> str | None:
        skip_words = self._connectors | {"the", "a", "an"}
        j = index - 1
        taken = 0
        while j >= 0:
            candidate = tokens[j].group(0).lower()
            if candidate in skip_words:
                j -= 1
                continue
            taken += 1
            if taken == steps:
                return candidate
            j -= 1
        return None

    def _is_part_of_perfect_or_passive(
        self, tokens: List[re.Match[str]], index: int
    ) -> bool:
        for j in range(index - 1, max(-1, index - 6), -1):
            if j < 0:
                break
            candidate = tokens[j].group(0).lower()
            if candidate in self._connectors or candidate in {"the", "a", "an"}:
                continue
            if candidate in self._auxiliary_markers or candidate == "to":
                return True
        return False

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
