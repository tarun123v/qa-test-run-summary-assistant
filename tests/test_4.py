from main import summarize_test_run


def test_summarize_test_run_with_zero_tests_avoids_division_by_zero():
    zero_test_run = {
        "run_id": "QA-000",
        "status": "not_started",
        "passed": 0,
        "failed": 0,
        "blocked": 0,
        "failing_tests": [],
        "blocked_tests": [],
    }

    summary = summarize_test_run(zero_test_run)

    assert "Pass rate: N/A (no tests executed)." in summary
