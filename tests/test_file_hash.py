from fundwatch.file_hash import calculate_file_hash


def test_identical_files_produce_same_hash(tmp_path):
    file_a = tmp_path / "file_a.csv"
    file_b = tmp_path / "file_b.csv"

    file_a.write_bytes(b"CNPJ;VALUE\n123;1500")
    file_b.write_bytes(b"CNPJ;VALUE\n123;1500")

    hash_a = calculate_file_hash(file_a)
    hash_b = calculate_file_hash(file_b)

    assert hash_a == hash_b


def test_different_files_produce_different_hashes(tmp_path):
    file_a = tmp_path / "file_a.csv"
    file_b = tmp_path / "file_b.csv"

    file_a.write_bytes(b"CNPJ;VALUE\n123;1500")
    file_b.write_bytes(b"CNPJ;VALUE\n123;1501")

    hash_a = calculate_file_hash(file_a)
    hash_b = calculate_file_hash(file_b)

    assert hash_a != hash_b


def test_empty_file_produces_valid_hash(tmp_path):
    file_a = tmp_path / "file_a.csv"
    file_a.write_bytes(b"")

    hash_a = calculate_file_hash(file_a)

    assert hash_a == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
