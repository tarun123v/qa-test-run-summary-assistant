from copy import deepcopy

from qa_data import QA_RUNS


def get_test_run(run_id: str) -> dict[str, object]:
    """Return an isolated copy of a matching run; never modify stored QA data."""
    if not isinstance(run_id, str):
        raise TypeError("run_id must be a string")

    wanted_id = run_id.strip().upper()
    if not wanted_id:
        raise ValueError("run_id must not be empty")

    for run in QA_RUNS:
        if run["run_id"] == wanted_id:
            return deepcopy(run)

    raise LookupError(f"No QA test run found for ID {wanted_id}.")
