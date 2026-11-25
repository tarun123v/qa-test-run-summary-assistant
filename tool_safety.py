import json
import logging
import re
from collections.abc import Callable, Collection


logger = logging.getLogger(__name__)

RUN_ID_PATTERN = re.compile(r"\bQA-\d+\b", flags=re.IGNORECASE)
QA_PROMPT_WORDS = {
    "a", "an", "and", "are", "be", "between", "can", "completed", "count",
    "counts", "details", "did", "do", "failed", "fail", "failing", "failure",
    "failures", "for", "give", "has", "have", "how", "in", "is", "list", "me",
    "many", "of", "on", "or", "passed", "pass", "passing", "please", "rate",
    "result", "results", "run", "runs", "show", "status", "summary", "summaries",
    "summarize", "test", "tests", "the", "their", "tell", "to", "what", "which",
    "were", "with", "write", "you",
}
QA_INTENT_WORDS = {
    "count", "counts", "details", "failed", "fail", "failing", "failure", "failures",
    "passed", "pass", "passing", "rate", "result", "results", "run", "runs", "status",
    "summary", "summaries", "summarize", "test", "tests",
}


def extract_requested_run_ids(text: str) -> list[str]:
    """Return unique QA-NNN run IDs from the user's request, preserving order."""
    return list(dict.fromkeys(match.upper() for match in RUN_ID_PATTERN.findall(text)))


def remove_run_ids(text: str, run_ids_to_remove: Collection[str]) -> str:
    """Remove unavailable IDs and their list connectors from a prompt."""
    for run_id in run_ids_to_remove:
        match = re.search(rf"\b{re.escape(run_id)}\b", text, flags=re.IGNORECASE)
        if match is None:
            continue

        before = text[:match.start()]
        after = text[match.end():]
        if RUN_ID_PATTERN.search(before):
            before = re.sub(r"\s*(?:and|,)\s*$", "", before, flags=re.IGNORECASE)
        else:
            after = re.sub(r"^\s*(?:and|,)\s*", "", after, flags=re.IGNORECASE)
        text = before + after

    text = re.sub(r"\s+([?.!,])", r"\1", text)
    text = re.sub(r",\s*(?=[?.!]|$)", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def unsupported_qa_prompt_words(text: str) -> list[str]:
    """List words outside the supported QA-run question vocabulary."""
    without_ids = RUN_ID_PATTERN.sub(" ", text)
    words = re.findall(r"[a-z]+", without_ids.lower())
    unsupported = sorted(set(words) - QA_PROMPT_WORDS)
    if not unsupported and not any(word in QA_INTENT_WORDS for word in words):
        return ["a QA run question"]
    return unsupported


def parse_and_validate_run_id(raw_arguments: object) -> str:
    """Parse model arguments and return a non-empty, validated run ID."""
    if isinstance(raw_arguments, str):
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as error:
            raise ValueError("Tool arguments were not valid JSON") from error
    else:
        # The Ollama Python SDK may already provide parsed arguments as a dict.
        arguments = raw_arguments

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object")
    if set(arguments) != {"run_id"}:
        raise ValueError("Tool arguments must contain only run_id")

    run_id = arguments["run_id"]
    if not isinstance(run_id, str):
        raise ValueError("run_id must be a string")

    run_id = run_id.strip()
    if not run_id:
        raise ValueError("run_id must not be empty")

    return run_id


def create_tool_result(
    function_name: str,
    raw_arguments: object,
    requested_run_ids: Collection[str],
    available_functions: dict[str, Callable[..., dict[str, object]]],
) -> dict[str, object]:
    """Validate and run a tool request, returning a small controlled result."""
    if function_name not in available_functions:
        return {
            "ok": False,
            "error": "unknown_tool",
            "message": "The requested function is not available.",
        }

    try:
        run_id = parse_and_validate_run_id(raw_arguments)
    except ValueError as error:
        return {
            "ok": False,
            "error": "invalid_arguments",
            "message": str(error),
        }

    allowed_requested_ids = {requested_id.upper() for requested_id in requested_run_ids}
    if run_id.upper() not in allowed_requested_ids:
        return {
            "ok": False,
            "error": "run_id_mismatch",
            "message": "The requested run ID did not match the user's question.",
        }

    lookup = available_functions[function_name]
    try:
        run = lookup(run_id=run_id)
    except LookupError:
        return {
            "ok": False,
            "error": "run_not_found",
            "message": f"No QA test run found for ID {run_id}.",
        }
    except (TypeError, ValueError):
        return {
            "ok": False,
            "error": "invalid_run_id",
            "message": "The run ID could not be used.",
        }
    except Exception as error:
        logger.error(
            "Tool lookup failed: function=%s run_id=%s error_type=%s",
            function_name,
            run_id,
            type(error).__name__,
        )
        return {
            "ok": False,
            "error": "lookup_failed",
            "message": "The QA test run could not be retrieved.",
        }

    allowed_fields = (
        "run_id",
        "status",
        "passed",
        "failed",
        "blocked",
        "failing_tests",
        "blocked_tests",
    )
    return {
        "ok": True,
        "run": {
            field: run[field]
            for field in allowed_fields
            if field in run
        },
    }
