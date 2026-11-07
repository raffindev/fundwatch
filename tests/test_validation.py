from datetime import date
import pytest
from src.fundwatch.validation import parse_reference_date

INVALID_FORMAT_INPUTS = [
    "2026/10/15",
    "2026-1-15",
    "2026-10-5",
    "abcd-ef-gh",
    "２０２６-１０-１５",
    " 2026-10-15",
    "2026-10-15 ",
    " 2026-10-15 ",
]

INVALID_CALENDAR_DATES = [
    "2026-02-30",
    "2025-02-29",
    "2026-13-15",
    "2026-00-15",
]


def test_parse_reference_date_valid():
    result = parse_reference_date("2026-10-15")
    assert result == date(2026, 10, 15)


def test_parse_reference_date_empty():
    with pytest.raises(
        ValueError,
        match=r"^Reference date is required\.$",
    ):
        parse_reference_date("")


@pytest.mark.parametrize("value", INVALID_FORMAT_INPUTS)
def test_parse_reference_date_invalid_format(value):
    with pytest.raises(
        ValueError,
        match=r"^Invalid reference date format\. Expected YYYY-MM-DD\.$",
    ):
        parse_reference_date(value)


@pytest.mark.parametrize("value", INVALID_CALENDAR_DATES)
def test_parse_reference_date_invalid_calendar_date(value):
    with pytest.raises(ValueError):
        parse_reference_date(value)


def test_parse_reference_date_leap_year():
    result = parse_reference_date("2024-02-29")
    assert result == date(2024, 2, 29)
