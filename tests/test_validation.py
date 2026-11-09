import pytest
from datetime import date
from decimal import Decimal

from src.fundwatch.validation import parse_reference_date, parse_decimal

# Reference date validation tests
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


# Funções de teste de parse_reference_date()
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


# Decimal validation tests
VALID_DECIMAL_INPUTS = [
    ("1500000.75", Decimal("1500000.75")),
    ("0", Decimal("0")),
    ("12.345678901234", Decimal("12.345678901234")),
    ("-150.50", Decimal("-150.50")),
    ("0.000001", Decimal("0.000001")),
]

INVALID_DECIMAL_INPUTS = [
    "abc",
    "12.34.56",
    "1,500.75",
    "NaN",
    "Infinity",
    "-Infinity",
]


# Funções de teste de parse_decimal()
@pytest.mark.parametrize("value, expected", VALID_DECIMAL_INPUTS)
def test_parse_decimal_valid(value, expected):
    result = parse_decimal(value)
    assert result == expected
    assert isinstance(result, Decimal)


def test_parse_decimal_required_empty():
    with pytest.raises(
        ValueError,
        match=r"^Decimal value is required\.$",
    ):
        parse_decimal("")


def test_parse_decimal_optional_empty():
    result = parse_decimal("", required=False)
    assert result is None


@pytest.mark.parametrize("value", INVALID_DECIMAL_INPUTS)
def test_parse_decimal_invalid(value):
    with pytest.raises(
        ValueError,
        match=r"^Invalid decimal value\.$",
    ):
        parse_decimal(value)
