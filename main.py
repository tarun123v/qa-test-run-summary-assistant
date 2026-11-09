from api_client import fetch_post
from qa_tools import get_test_run


def summarize_test_run(run):
    summary = (
        f"Run {run['run_id']} is {run['status']}: "
        f"{run['passed']} tests passed, {run['failed']} failed, and {run['blocked']} blocked."
    )

    # Blocked tests were not executed, so calculate the pass rate over passed + failed.
    total_executed = run["passed"] + run["failed"]
    if total_executed > 0:
        pass_rate = run["passed"] / total_executed * 100
        summary += f" Pass rate: {pass_rate:.1f}%."
    else:
        summary += " Pass rate: N/A (no tests executed)."

    failing_tests = run["failing_tests"]
    if failing_tests:
        summary += " Failing tests: " + ", ".join(failing_tests) + "."
    else:
        summary += " There are no failing tests."

    blocked_tests = run["blocked_tests"]
    if blocked_tests:
        summary += " Blocked tests: " + ", ".join(blocked_tests) + "."
    else:
        summary += " There are no blocked tests."

    return summary


def main():
    print("Test Run Summary Assistant")

    lookup_examples = [
        ("known ID", "QA-104"),
        ("unknown ID", "QA-107"),
        ("blank input", ""),
    ]

    for description, run_id in lookup_examples:
        print(f"\nChecking {description} {run_id!r}:")
        try:
            run = get_test_run(run_id)
        except (LookupError, TypeError, ValueError) as error:
            print(error)
        else:
            print(summarize_test_run(run))

    post = fetch_post(1)
    print(f"\nPost id: {post['id']}")
    print(f"Post title: {post['title']}")
    print(f"Post body: {post['body']}")


if __name__ == "__main__":
    main()
