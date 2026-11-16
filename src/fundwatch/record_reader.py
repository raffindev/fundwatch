from pathlib import Path

from .csv_reader import read_cvm_csv
from .record_validation import validate_record


def read_validated_records(file_path: Path):
    for line_number, record in enumerate(read_cvm_csv(file_path), start=2):
        validated_record = validate_record(record, line_number)
        yield validated_record
