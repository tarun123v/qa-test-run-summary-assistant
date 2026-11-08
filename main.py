from api_client import fetch_post


sample_run = {
    "run_id": "QA-104",
    "status": "completed",
    "passed": 16,
    "failed": 2,
    "blocked": 2,
    "failing_tests": ["test_login_timeout", "test_cart_total"],
     "blocked_tests": ["test_payment_gateway", "test_user_profile"]
}


def format_summary(run):
    summary = (
        f"Run {run['run_id']} is {run['status']}: "
        f"{run['passed']} tests passed, {run['failed']} failed, and {run['blocked']} blocked."
    )

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
    print(format_summary(sample_run))

    post = fetch_post(1)
    print(f"Post id: {post['id']}")
    print(f"Post title: {post['title']}")
    print(f"Post body: {post['body']}")
   


if __name__ == "__main__":
    main()
