from qa_tools import get_test_run


def test_get_test_run_returns_expected_data_for_known_id():
    run = get_test_run("QA-104")

    assert run["run_id"] == "QA-104"
    assert run["passed"] == 16
    assert run["failed"] == 2
    assert run["blocked"] == 2
