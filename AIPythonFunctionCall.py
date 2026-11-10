import json
import os
from pathlib import Path

from dotenv import load_dotenv
from ollama import chat

from qa_tools import get_test_run


load_dotenv(Path(__file__).with_name(".env"))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "").strip()
think_setting = os.getenv("OLLAMA_THINK", "").strip().lower()

if not MODEL_NAME:
    raise ValueError("OLLAMA_MODEL is missing or empty in .env")
if think_setting not in {"true", "false"}:
    raise ValueError("OLLAMA_THINK is missing or invalid in .env; use true or false")

THINK = think_setting == "true"


# These instructions are sent to the model as its system message.
SYSTEM_PROMPT = (
    "You are a QA test-run assistant. For any question about a specific test "
    "run, use the get_test_run tool to retrieve the run's facts. Base your "
    "answer only on the data returned by that tool. Never guess or invent run "
    "IDs, statuses, counts, test names, or other run details. If the tool "
    "cannot find a run, say that it was not found. If the requested detail is "
    "not present in the returned data, say that the data does not include it."
)

# Start each conversation with the assistant instructions.
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


# This schema tells Ollama what the tool does and what input it accepts.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_test_run",
            "description": (
                "Look up one QA test run by its run ID and return that run's "
                "stored details. This tool is read-only: it does not change "
                "the run or its results. If no run matches, the lookup raises "
                "a LookupError."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The ID of the QA test run to retrieve.",
                    }
                },
                "required": ["run_id"],
                "additionalProperties": False,
            },
        },
    }
]

# The application will use this mapping to run the requested Python function.
available_functions = {"get_test_run": get_test_run}


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


# Send a user request and the tool definition to the model.
user_request = "Summarize QA test run QA-108."
messages.append({"role": "user", "content": user_request})

response = chat(
    model=MODEL_NAME,
    messages=messages,
    tools=tools,
    think=THINK,
)

# Inspect whether the model answered normally or asked us to run the tool.
if response.message.tool_calls:
    print("The model requested a tool call:")
    # Keep the assistant's tool request in the conversation before tool replies.
    messages.append(response.message)

    for call in response.message.tool_calls:
        print(f"  Function: {call.function.name}")
        if call.function.name not in available_functions:
            tool_result = {
                "ok": False,
                "error": "unknown_tool",
                "message": "The requested function is not available.",
            }
        else:
            try:
                run_id = parse_and_validate_run_id(call.function.arguments)
            except ValueError as error:
                tool_result = {
                    "ok": False,
                    "error": "invalid_arguments",
                    "message": str(error),
                }
            else:
                try:
                    run = available_functions[call.function.name](run_id=run_id)
                except LookupError:
                    tool_result = {
                        "ok": False,
                        "error": "run_not_found",
                        "message": f"No QA test run found for ID {run_id}.",
                    }
                except (TypeError, ValueError):
                    tool_result = {
                        "ok": False,
                        "error": "invalid_run_id",
                        "message": "The run ID could not be used.",
                    }
                except Exception:
                    tool_result = {
                        "ok": False,
                        "error": "lookup_failed",
                        "message": "The QA test run could not be retrieved.",
                    }
                else:
                    # Only send the fields needed to answer common QA questions.
                    allowed_fields = (
                        "run_id",
                        "status",
                        "passed",
                        "failed",
                        "blocked",
                        "failing_tests",
                        "blocked_tests",
                    )
                    tool_result = {
                        "ok": True,
                        "run": {
                            field: run[field]
                            for field in allowed_fields
                            if field in run
                        },
                    }

        # Keep the tool response compact and avoid exposing exception details.
        tool_result_json = json.dumps(tool_result)
        print(f"  Controlled tool result: {tool_result_json}")
        messages.append(
            {
                "role": "tool",
                "tool_name": call.function.name,
                "content": tool_result_json,
            }
        )

    # Send the tool response(s) back so the model can write its final answer.
    final_response = chat(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        think=THINK,
    )
    print("Final answer:")
    print(final_response.message.content)
else:
    print("The model returned a normal answer:")
    print(response.message.content)
