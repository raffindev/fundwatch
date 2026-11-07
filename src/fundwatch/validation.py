from datetime import date, datetime


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
