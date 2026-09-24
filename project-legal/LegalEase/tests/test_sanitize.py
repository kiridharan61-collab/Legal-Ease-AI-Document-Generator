from utils.sanitize import sanitize_text, split_terms


def test_sanitize_text():
    text = "Hello\u2014world\n\n\nNext"
    assert sanitize_text(text) == "Hello-world\n\nNext"


def test_split_terms():
    assert split_terms("One; Two; Three") == ["One", "Two", "Three"]
