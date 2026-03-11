import pytest
from ExplicitUtil.nfo_tool import detect_date_in_name

@pytest.mark.parametrize("input_name, expected_output", [
    # YYYY-MM-DD
    ("movie_2023-10-27", "2023-10-27"),
    ("2023_10_27_video", "2023-10-27"),
    ("test.2023.10.27.mp4", "2023-10-27"),

    # DD-MM-YYYY
    ("movie_27-10-2023", "2023-10-27"),
    ("27_10_2023_video", "2023-10-27"),
    ("test.27.10.2023.mp4", "2023-10-27"),

    # YY-MM-DD (2-digit year)
    # < 25 -> 20xx
    ("movie_24-10-27", "2024-10-27"),
    # >= 25 -> 19xx
    ("movie_99-10-27", "1999-10-27"),
    ("movie_25-10-27", "1925-10-27"),

    # Mixed separators (if supported by regex)
    # The regexes are:
    # r"(\d{4})[-_.](\d{2})[-_.](\d{2})"
    # r"(\d{2})[-_.](\d{2})[-_.](\d{4})"
    # r"(\d{2})[-._](\d{2})[-._](\d{2})"
    ("movie_2023.10-27", "2023-10-27"), # mixed . and -
    ("movie_27_10.2023", "2023-10-27"), # mixed _ and .

    # Embedded in strings
    ("Something.2023-10-27.SomethingElse", "2023-10-27"),
    ("2023-10-27-at-the-start", "2023-10-27"),
    ("at-the-end-2023-10-27", "2023-10-27"),

    # No date
    ("movie_without_date", None),
    ("202-10-27", None), # Malformed year
    ("2023-1-27", None),  # Malformed month (needs 2 digits)

    # Edge case: which pattern takes precedence?
    # "2023-10-27" matches first pattern.
    # "27-10-2023" matches second pattern.
    # What if it's "10-11-12"?
    # Matches third pattern: r"(\d{2})[-._](\d{2})[-._](\d{2})"
    # 10 < 25 -> 2010-11-12
    ("10-11-12", "2010-11-12"),
])
def test_detect_date_in_name(input_name, expected_output):
    assert detect_date_in_name(input_name) == expected_output
