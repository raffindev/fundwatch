import pytest
from fundwatch.csv_reader import read_cvm_csv


def test_read_cvm_csv(tmp_path):
    file_path = tmp_path / "test_cvm.csv"

    file_path.write_text(
        "CNPJ_FUNDO_CLASSE;DT_COMPTC\n"
        "12345678000190;2026-10-15\n"
        "98765432000110;2026-10-16\n",
        encoding="utf-8",
    )

    reader = read_cvm_csv(file_path)
    first_row = next(reader)
    second_row = next(reader)

    assert first_row["CNPJ_FUNDO_CLASSE"] == "12345678000190"
    assert first_row["DT_COMPTC"] == "2026-10-15"
    assert second_row["CNPJ_FUNDO_CLASSE"] == "98765432000110"
    assert second_row["DT_COMPTC"] == "2026-10-16"


def test_read_cvm_csv_without_records(tmp_path):

    file_path = tmp_path / "test_cvm.csv"

    file_path.write_text(
        "CNPJ_FUNDO_CLASSE;DT_COMPTC\n",
        encoding="utf-8",
    )

    reader = read_cvm_csv(file_path)
    with pytest.raises(StopIteration):
        next(reader)
