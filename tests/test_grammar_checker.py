import pytest

from openwrite.grammar_checker import GrammarChecker


@pytest.fixture()
def checker() -> GrammarChecker:
    return GrammarChecker()


def test_detects_repeated_words(checker: GrammarChecker) -> None:
    text = "This is is a mistake."
    issues = checker.check(text)
    rules = {issue.rule for issue in issues}
    assert "repeated-word" in rules


def test_requires_sentence_punctuation(checker: GrammarChecker) -> None:
    text = "This is a sentence without punctuation"
    issues = checker.check(text)
    assert any(issue.rule == "punctuation" for issue in issues)


def test_requires_sentence_capitalization(checker: GrammarChecker) -> None:
    text = "this sentence starts incorrectly."
    issues = checker.check(text)
    assert any(issue.rule == "capitalization" for issue in issues)


def test_allows_clean_sentence(checker: GrammarChecker) -> None:
    text = "This sentence is correct."
    issues = checker.check(text)
    assert not issues


def test_detects_long_sentence(checker: GrammarChecker) -> None:
    text = (
        "This sentence contains many clauses and keeps going without pause "
        "which makes it difficult to read and likely signals a run on sentence "
        "because it lacks proper punctuation and continues to accumulate words "
        "beyond what a reader can comfortably parse without help."
    )
    issues = checker.check(text)
    assert any(issue.rule == "long-sentence" for issue in issues)


def test_double_spaces(checker: GrammarChecker) -> None:
    text = "This  sentence has double spaces."
    issues = checker.check(text)
    assert any(issue.rule == "double-space" for issue in issues)
