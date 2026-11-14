from datetime import date
from decimal import Decimal

import pytest

from fundwatch.record_validation import validate_record


@pytest.fixture
def valid_row():
    return {
        "TP_FUNDO_CLASSE": "1",
        "CNPJ_FUNDO_CLASSE": "12345678000190",
        "ID_SUBCLASSE": "",
        "DT_COMPTC": "2026-10-15",
        "VL_TOTAL": "1750000.50",
        "VL_QUOTA": "1.234567890123",
        "VL_PATRIM_LIQ": "1500000.75",
        "CAPTC_DIA": "50000.00",
        "RESG_DIA": "25000.00",
        "NR_COTST": "150",
    }


def test_validate_record_valid(valid_row):
    result = validate_record(valid_row)

    assert result["cnpj"] == "12345678000190"
    assert result["class_type"] == "1"
    assert result["subclass_id"] is None
    assert result["reference_date"] == date(2026, 10, 15)
    assert result["total_value"] == Decimal("1750000.50")
    assert result["quota_value"] == Decimal("1.234567890123")
    assert result["net_equity"] == Decimal("1500000.75")
    assert result["inflow"] == Decimal("50000.00")
    assert result["outflow"] == Decimal("25000.00")
    assert result["shareholders"] == 150


@pytest.mark.parametrize(
    "field_name,invalid_value",
    [
        ("VL_QUOTA", "abc"),
        ("DT_COMPTC", "2026-15-40"),
        ("NR_COTST", "-10"),
    ],
)
def test_validate_record_invalid(valid_row, field_name, invalid_value):
    valid_row[field_name] = invalid_value

    with pytest.raises(ValueError, match=f"Field {field_name}"):
        validate_record(valid_row)


def test_validate_record_missing_cnpj(valid_row):
    valid_row.pop("CNPJ_FUNDO_CLASSE")

    with pytest.raises(ValueError, match="Field CNPJ_FUNDO_CLASSE"):
        validate_record(valid_row)


def test_validate_record_missing_subclass_column(valid_row):
    valid_row.pop("ID_SUBCLASSE")

    with pytest.raises(ValueError, match="Field ID_SUBCLASSE"):
        validate_record(valid_row)


def test_validate_record_invalid_with_row_number(valid_row):
    valid_row["VL_QUOTA"] = "abc"

    with pytest.raises(ValueError, match=r"CSV row 15234: Field VL_QUOTA"):
        validate_record(valid_row, row_number=15234)
