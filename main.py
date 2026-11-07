sample_run = {
    "run_id": "QA-104",
    "status": "completed",
    "passed": 18,
    "failed": 2,
    "failing_tests": ["test_login_timeout", "test_cart_total"],
}


def format_summary(run):
    summary = (
        f"Run {run['run_id']} is {run['status']}: "
        f"{run['passed']} tests passed and {run['failed']} failed."
    )

    failing_tests = run["failing_tests"]
    if failing_tests:
        summary += " Failing tests: " + ", ".join(failing_tests) + "."
    else:
        summary += " There are no failing tests."

    return summary


def main():
    print("Test Run Summary Assistant")
    print(format_summary(sample_run))


if __name__ == "__main__":
    main()
