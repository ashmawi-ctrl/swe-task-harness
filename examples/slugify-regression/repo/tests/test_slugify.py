from string_utils import slugify


def test_basic_slug() -> None:
    assert slugify("Hello World") == "hello-world"


def test_repeated_whitespace_collapses_to_one_separator() -> None:
    assert slugify("Hello   World") == "hello-world"


def test_leading_and_trailing_whitespace_is_removed() -> None:
    assert slugify("  Payment Status  ") == "payment-status"
