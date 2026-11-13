from pathlib import Path
import hashlib


def calculate_file_hash(file_path: Path) -> str:
    hash_value = hashlib.sha256()
    chunk_size = 64 * 1024

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            hash_value.update(chunk)

    return hash_value.hexdigest()


if __name__ == "__main__":
    file_path = Path("data/raw/inf_diario_fi_202610.csv")
    result = calculate_file_hash(file_path)
    print(result)
