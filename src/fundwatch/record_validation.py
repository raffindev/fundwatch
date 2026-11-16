from .validation import parse_decimal, parse_integer, parse_reference_date


def validate_field(row: dict, field_name: str, parser):
    try:
        return parser(row[field_name])
    except (ValueError, KeyError) as exc:
        raise ValueError(f"Field {field_name}: {exc}") from exc


def require_field(row: dict, field_name: str) -> str:
    try:
        value = row[field_name]
    except KeyError as exc:
        raise ValueError(f"Field {field_name}: Required column is missing.") from exc

    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field {field_name}: Value is required.")

    return value


def optional_field(row: dict, field_name: str) -> str | None:
    try:
        value = row[field_name]
    except KeyError as exc:
        raise ValueError(f"Field {field_name}: Required column is missing.") from exc

    if value is None or not isinstance(value, str):
        raise ValueError(f"Field {field_name}: Invalid value.")

    return value.strip() or None


def validate_record(row: dict, row_number: int | None = None) -> dict:
    try:
        return {
            "cnpj": require_field(row, "CNPJ_FUNDO_CLASSE"),
            "class_type": require_field(row, "TP_FUNDO_CLASSE"),
            "subclass_id": optional_field(row, "ID_SUBCLASSE"),
            "reference_date": validate_field(row, "DT_COMPTC", parse_reference_date),
            "total_value": validate_field(
                row, "VL_TOTAL", lambda value: parse_decimal(value, required=False)
            ),
            "quota_value": validate_field(
                row, "VL_QUOTA", lambda value: parse_decimal(value, required=False)
            ),
            "net_equity": validate_field(
                row, "VL_PATRIM_LIQ", lambda value: parse_decimal(value, required=False)
            ),
            "inflow": validate_field(
                row, "CAPTC_DIA", lambda value: parse_decimal(value, required=False)
            ),
            "outflow": validate_field(
                row, "RESG_DIA", lambda value: parse_decimal(value, required=False)
            ),
            "shareholders": validate_field(
                row, "NR_COTST", lambda value: parse_integer(value, required=False)
            ),
        }

    except ValueError as exc:
        if row_number is not None:
            raise ValueError(f"CSV row {row_number}: {exc}") from exc

        raise
