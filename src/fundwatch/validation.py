from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def parse_reference_date(value: str) -> date:
    if value == "":
        raise ValueError("Reference date is required.")

    if len(value) != 10 or (value[4], value[7]) != ("-", "-"):
        raise ValueError("Invalid reference date format. Expected YYYY-MM-DD.")

    date_digits = value.replace("-", "")
    for digit in date_digits:
        if digit not in "0123456789":
            raise ValueError("Invalid reference date format. Expected YYYY-MM-DD.")

    parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    return parsed_date


def parse_decimal(value: str, required: bool = True):
    if value == "":
        if required:
            raise ValueError("Decimal value is required.")

        return None

    try:
        decimal_value = Decimal(value)

        if not decimal_value.is_finite():
            raise ValueError("Invalid decimal value.")

        return decimal_value

    except InvalidOperation as exc:
        raise ValueError("Invalid decimal value.") from exc


def parse_integer(value: str, required: bool = True):
    if value == "":
        if required:
            raise ValueError("Integer value is required.")

        return None

    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError("Invalid integer value.") from exc

    if number < 0:
        raise ValueError("Integer value cannot be negative.")

    return number
