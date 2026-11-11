import csv
from pathlib import Path
from src.fundwatch.validation import parse_decimal, parse_integer


def inspect_csv(filename):
    numeric_fields = [
        "VL_TOTAL",
        "VL_QUOTA",
        "VL_PATRIM_LIQ",
        "CAPTC_DIA",
        "RESG_DIA",
        "NR_COTST",
    ]

    empty_counts = {field: 0 for field in numeric_fields}
    positive_counts = {field: 0 for field in numeric_fields}
    zero_counts = {field: 0 for field in numeric_fields}
    negative_counts = {field: 0 for field in numeric_fields}
    negative_examples = {field: [] for field in numeric_fields}
    negative_funds = {field: set() for field in numeric_fields}

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

            for field in numeric_fields:
                if row[field] == "":
                    empty_counts[field] += 1
                    continue

                if field == "NR_COTST":
                    numeric_value = parse_integer(row[field])
                else:
                    numeric_value = parse_decimal(row[field])

                if numeric_value > 0:
                    positive_counts[field] += 1

                elif numeric_value == 0:
                    zero_counts[field] += 1

                else:
                    negative_counts[field] += 1
                    negative_funds[field].add(row["CNPJ_FUNDO_CLASSE"])

                    if len(negative_examples[field]) < 5:
                        example = {
                            "cnpj": row["CNPJ_FUNDO_CLASSE"],
                            "subclass": row["ID_SUBCLASSE"],
                            "date": row["DT_COMPTC"],
                            "value": numeric_value,
                        }

                        negative_examples[field].append(example)

        print("\n" + "=" * 65)
        print("FUNDWATCH - CVM DATA INSPECTION")
        print("=" * 65)

        print("\nGENERAL STATISTICS")
        print("-" * 65)
        print(f"Total records       : {row_count:,}")
        print(f"Duplicate records   : {duplicate_count:,}")
        print(f"Missing subclasses  : {missing_subclass_count:,}")
        print(f"Unique funds (CNPJ) : {len(unique_funds):,}")

        print("\nNUMERIC FIELD ANALYSIS")
        print("-" * 65)
        print(f"{'Field':<20} {'Empty':>8} {'Positive':>8} {'Zero':>8} {'Negative':>9}")
        print("-" * 65)

        for field in numeric_fields:
            print(
                f"{field:<20} "
                f"{empty_counts[field]:>8,} "
                f"{positive_counts[field]:>8,} "
                f"{zero_counts[field]:>8,} "
                f"{negative_counts[field]:>9,}"
            )

        print("=" * 65)
        print("\nNEGATIVE VALUE EXAMPLES")
        print("-" * 55)

        for field, examples in negative_examples.items():
            if not examples:
                continue

            print(f"\n{field} ({negative_counts[field]:,} negative records)")
            print(f"Distinct funds: {len(negative_funds[field])}")

            for example in examples:
                print(
                    f"  CNPJ: {example['cnpj']} | "
                    f"Subclass: {example['subclass'] or 'N/A'} | "
                    f"Date: {example['date']} | "
                    f"Value: {example['value']}"
                )


if __name__ == "__main__":
    inspect_csv("inf_diario_fi_202610.csv")
