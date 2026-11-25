from unittest.mock import Mock

from qa_tools import get_test_run
from tool_safety import (
    create_tool_result,
    extract_requested_run_ids,
    unsupported_qa_prompt_words,
)


def test_malformed_tool_arguments_do_not_call_run_lookup():
    lookup = Mock()

    result = create_tool_result(
        function_name="get_test_run",
        raw_arguments='{"run_id": "QA-104"',  # Missing the closing brace.
        requested_run_ids={"QA-104"},
        available_functions={"get_test_run": lookup},
    )

    assert result["ok"] is False
    assert result["error"] == "invalid_arguments"
    assert result["message"] == "Tool arguments were not valid JSON"
    lookup.assert_not_called()


def test_unknown_run_returns_controlled_not_found_result():
    result = create_tool_result(
        function_name="get_test_run",
        raw_arguments={"run_id": "QA-999"},
        requested_run_ids={"QA-999"},
        available_functions={"get_test_run": get_test_run},
    )

    assert result == {
        "ok": False,
        "error": "run_not_found",
        "message": "No QA test run found for ID QA-999.",
    }
    assert "run" not in result


def test_lookup_exception_returns_bounded_error_and_safe_log(caplog):
    def failing_lookup(run_id):
        raise RuntimeError("sensitive-token=do-not-log")

    result = create_tool_result(
        function_name="get_test_run",
        raw_arguments={"run_id": "QA-104"},
        requested_run_ids={"QA-104"},
        available_functions={"get_test_run": failing_lookup},
    )

    assert result == {
        "ok": False,
        "error": "lookup_failed",
        "message": "The QA test run could not be retrieved.",
    }
    assert len(result["message"]) <= 100
    assert "get_test_run" in caplog.text
    assert "QA-104" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "sensitive-token" not in caplog.text
    assert "Traceback" not in caplog.text


def test_multiple_requested_run_ids_allow_each_matching_tool_call():
    result = create_tool_result(
        function_name="get_test_run",
        raw_arguments={"run_id": "QA-105"},
        requested_run_ids={"QA-104", "QA-105"},
        available_functions={"get_test_run": get_test_run},
    )

    assert result["ok"] is True
    assert result["run"]["run_id"] == "QA-105"


def test_extracts_each_unique_run_id_from_a_multi_run_prompt():
    run_ids = extract_requested_run_ids(
        "Can you summarize QA-104 and QA-105, including QA-104 again?"
    )

    assert run_ids == ["QA-104", "QA-105"]


def test_mixed_qa_and_unrelated_prompt_is_flagged():
    unsupported_words = unsupported_qa_prompt_words(
        "Can you write a summary of QA-104 and how to reverse string in python?"
    )

    assert unsupported_words == ["python", "reverse", "string"]
