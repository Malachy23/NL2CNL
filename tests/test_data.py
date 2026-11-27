"""Checks that the data files are consistent with the grammar used by the benchmark."""
from collections import Counter
from pathlib import Path

import pytest

from nl2cnl.evaluation.validator import is_syntax_valid
from nl2cnl.loaders import load_examples, load_test_cases

EXAMPLES = load_examples(Path("data/examples/bioquery_examples.json"))
CASES = load_test_cases(Path("data/tests/test_cases.json"))


@pytest.mark.parametrize("text", [cnl for case in CASES for cnl in case["expected_cnl"]])
def test_expected_cnl_is_valid(text):
    assert is_syntax_valid(text)


@pytest.mark.parametrize("text", [example["cnl_output"] for example in EXAMPLES])
def test_example_output_is_valid(text):
    assert is_syntax_valid(text)


def test_examples_have_no_duplicate_outputs():
    counts = Counter(example["cnl_output"] for example in EXAMPLES)
    assert [text for text, n in counts.items() if n > 1] == []


def test_invalid_sentences_rejected():
    assert not is_syntax_valid("drugs that treat asthma")
    assert not is_syntax_valid("Which drugs treat the disease Asthma")  # missing "?"


def test_test_case_ids_are_unique():
    ids = [case["id"] for case in CASES]
    assert len(ids) == len(set(ids))
