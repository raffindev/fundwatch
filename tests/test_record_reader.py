from datetime import date
from decimal import Decimal

from fundwatch.record_reader import read_validated_records


def test_read_validated_records(tmp_path):
    csv_file = tmp_path / "test_cvm.csv"

    csv_file.write_text(
        "TP_FUNDO_CLASSE;CNPJ_FUNDO_CLASSE;ID_SUBCLASSE;"
        "DT_COMPTC;VL_TOTAL;VL_QUOTA;VL_PATRIM_LIQ;"
        "CAPTC_DIA;RESG_DIA;NR_COTST\n"
        "1;12345678000190;;2026-10-15;1750000.50;"
        "1.234567890123;1500000.75;50000.00;25000.00;150\n",
        encoding="utf-8",
    )

    records = read_validated_records(csv_file)
    record = next(records)

    assert record["cnpj"] == "12345678000190"
    assert record["subclass_id"] is None
    assert record["reference_date"] == date(2026, 10, 15)
    assert record["quota_value"] == Decimal("1.234567890123")
    assert record["shareholders"] == 150
