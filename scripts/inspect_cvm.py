import csv
from pathlib import Path


def inspect_csv(filename):
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "raw" / filename

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")

        seen_keys = set()
        unique_funds = set()

        row_count = 0
        duplicate_count = 0
        missing_subclass_count = 0

        for row in reader:
            row_count += 1
            record_key = (
                row["CNPJ_FUNDO_CLASSE"],
                row["ID_SUBCLASSE"],
                row["DT_COMPTC"],
            )

            unique_funds.add(record_key[0])

            if row["ID_SUBCLASSE"] == "":
                missing_subclass_count += 1

            if record_key not in seen_keys:
                seen_keys.add(record_key)

            else:
                duplicate_count += 1

        print(f"Total records: {row_count}")
        print(f"Duplicate records: {duplicate_count}")
        print(f"Missing subclasses: {missing_subclass_count}")
        print(f"Unique CNPJ: {len(unique_funds)}")


if __name__ == "__main__":
    inspect_csv("inf_diario_fi_202610.csv")
