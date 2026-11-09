QA_RUNS = [
    {
        "run_id": "QA-103",
        "status": "completed",
        "passed": 20,
        "failed": 0,
        "blocked": 0,
        "failing_tests": [],
        "blocked_tests": [],
    },
    {
        "run_id": "QA-104",
        "status": "completed",
        "passed": 16,
        "failed": 2,
        "blocked": 2,
        "failing_tests": ["test_login_timeout", "test_cart_total"],
        "blocked_tests": ["test_payment_gateway", "test_user_profile"],
    },
    {
        "run_id": "QA-105",
        "status": "completed",
        "passed": 18,
        "failed": 2,
        "blocked": 0,
        "failing_tests": ["test_checkout_total", "test_session_expiry"],
        "blocked_tests": [],
    },
]
