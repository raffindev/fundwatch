import csv
from pathlib import Path


def read_cvm_csv(file_path: Path):
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            yield row
