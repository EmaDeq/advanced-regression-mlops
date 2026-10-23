import hashlib

import pytest

from advanced_regression_mlops.release_provenance import (
    dvc_expected_snapshot,
    verified_dataset,
    verified_model,
)


def test_verified_dataset_matches_dvc_bytes(tmp_path):
    dataset = tmp_path / "boston.csv"
    dataset.write_bytes(b"a,b\n1,2\n")
    md5 = hashlib.md5(dataset.read_bytes()).hexdigest()
    pointer = tmp_path / "boston.csv.dvc"
    pointer.write_text(
        f"outs:\n- md5: {md5}\n  size: {dataset.stat().st_size}\n  hash: md5\n  path: boston.csv\n",
        encoding="utf-8",
    )
    assert dvc_expected_snapshot(pointer) == (md5, dataset.stat().st_size)
    assert verified_dataset(dataset, pointer)["dvc_md5"] == md5

    dataset.write_bytes(b"a,b\n1,3\n")
    with pytest.raises(ValueError, match="differs from the DVC-tracked snapshot"):
        verified_dataset(dataset, pointer)


def test_verified_model_rejects_different_sha256(tmp_path):
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model-contents")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    checksum = tmp_path / "model.sha256"
    checksum.write_text(f"{digest}  artifacts/model.joblib\n", encoding="utf-8")
    assert verified_model(model, checksum)["sha256"] == digest
    checksum.write_text(f"{'0' * 64}  artifacts/model.joblib\n", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        verified_model(model, checksum)
