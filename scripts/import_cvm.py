import sys
from pathlib import Path

from fundwatch.import_service import import_cvm_file


def main():
    args = sys.argv[1:]

    if len(args) == 1:
        file_path = Path(args[0])
        schema = "fundwatch"

    elif len(args) == 3 and args[1] == "--schema":
        file_path = Path(args[0])
        schema = args[2]

    else:
        print(
            "Usage: python scripts/import_cvm.py "
            "<csv_file> [--schema fundwatch|fundwatch_test]"
        )
        return 1

    if schema not in {"fundwatch", "fundwatch_test"}:
        print(f"Invalid schema: {schema}")
        return 1

    try:
        import_cvm_file(
            file_path=file_path,
            schema=schema,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Import failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
