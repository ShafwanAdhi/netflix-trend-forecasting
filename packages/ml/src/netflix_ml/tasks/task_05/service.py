"""Read-only validated forecasting results and trusted project-owned fitted models."""

from pathlib import Path

import joblib
import sklearn

from netflix_ml.shared.io import digest, read_json, root


class Forecasting:
    def __init__(self, bundle):
        for name, expected in read_json(bundle / "checksums.json").items():
            if Path(name).name != name or digest(bundle / name) != expected:
                raise ValueError("Task 5 artifact integrity check failed")
        self.metadata = read_json(bundle / "metadata.json")
        self.results = read_json(bundle / "results.json")
        if (
            self.metadata["run_id"] != self.results["run_id"]
            or self.metadata["sklearn"] != sklearn.__version__
        ):
            raise ValueError("Task 5 environment or identity mismatch")
        self.models = joblib.load(bundle / "models.joblib")
        if len(self.results["series"]) != 6:
            raise ValueError("Incomplete forecast series")


def load_forecasting():
    pointer = read_json(root() / "artifacts/task-05/active.json")
    run_id = pointer["run_id"]
    if Path(run_id).name != run_id:
        raise ValueError("Invalid Task 5 run identity")
    bundle = root() / "artifacts/task-05" / run_id
    if digest(bundle / "checksums.json") != pointer["checksums_sha256"]:
        raise ValueError("Task 5 checksum manifest does not match active pointer")
    return Forecasting(bundle)
