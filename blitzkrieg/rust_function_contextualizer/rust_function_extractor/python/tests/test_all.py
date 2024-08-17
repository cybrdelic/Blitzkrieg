import pytest
import rust_function_extractor


def test_sum_as_string():
    assert rust_function_extractor.sum_as_string(1, 1) == "2"
