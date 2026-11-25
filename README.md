# Test Run Summary Assistant

- Python learning project for summarizing locally stored synthetic QA test runs.
- Connects an Ollama model to the read-only `get_test_run` tool for run-specific questions.
- Validates run IDs and tool arguments, and handles unsupported prompts and lookup failures.
- Includes pytest coverage and an HTTP client example using JSONPlaceholder.

## Project files

- `AIPythonFunctionCall.py` is the Ollama-powered QA assistant example. It checks the request and local run IDs, provides the `get_test_run` tool, handles tool results, and asks the model for a final answer.
- `tool_safety.py` extracts run IDs, limits prompts to supported QA wording, validates model-generated tool arguments, checks requested IDs, and returns controlled lookup results and errors.
- `qa_data.py` stores four invented QA runs: `QA-103`, `QA-104`, `QA-105`, and `QA-123`.
- `qa_tools.py` validates and normalizes a run ID, returns an isolated copy of a matching record, and raises `LookupError` when no record matches. It only reads local data.
- `main.py` demonstrates known, unknown, and blank IDs, summarizes a run, and calls the sample HTTP client.
- `api_client.py` fetches a JSONPlaceholder post with a timeout, checks the response, and returns only its ID, title, and body.
- `singleCall.py` demonstrates an Ollama tool call using a small, fixed sample-temperature dictionary; it does not fetch live weather.
- `local_model_check.py` sends a simple readiness prompt to the locally installed `llama3.2:latest` model.
- `tests/` contains pytest checks for QA lookup and summary behavior, mocked HTTP responses, and tool argument/error handling.
- `.env.example` shows the Ollama model and thinking settings to copy into your private `.env` file. `.gitignore` keeps `.env`, virtual environments, caches, and other generated files out of version control.
- `package.json` and `package-lock.json` are Node.js dependency files; the Python application does not use them.
- `pytest-report.html` is a generated pytest report, not application source code.

## Requirements

- Python 3.10 or later
- PowerShell (the commands below are for Windows)
- An internet connection to fetch the sample post

## Set up the project

Open PowerShell in the project folder and create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

When it is active, PowerShell shows `(.venv)` at the start of the prompt. The application code uses Python's standard library, so it needs no runtime packages.

## Run the program

From the project folder, with the virtual environment active, run:

```powershell
python main.py
```

Expected output includes the three lookup cases and the API response:

```text
Test Run Summary Assistant

Checking known ID 'QA-104':
Run QA-104 is completed: 16 tests passed, 2 failed, and 2 blocked. Pass rate: 88.9%. Failing tests: test_login_timeout, test_cart_total. Blocked tests: test_payment_gateway, test_user_profile.

Checking unknown ID 'QA-107':
No QA test run found for ID QA-107.

Checking blank input '':
run_id must not be empty

Post id: 1
Post title: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
Post body: quia et suscipit
suscipit recusandae consequuntur expedita et cum
reprehenderit molestiae ut ut quas totam
nostrum rerum est autem sunt rem eveniet architecto
```

The pass rate is calculated as `passed / (passed + failed) * 100`; blocked tests are excluded because they were not executed. If no tests were executed, the summary displays `N/A` instead of dividing by zero.


## Read-only QA tool

`get_test_run(run_id)` only looks up and returns a copy of a synthetic run. It does not change run status, delete results, or trigger reruns. Because it returns a copy, edits to the returned dictionary or its test-name lists do not change the original records in `qa_data.py`.
## Running the tests

The tests use `pytest`. Install it in the active virtual environment and run the test suite with:

```powershell
python -m pip install pytest
python -m pytest
```

## Missing QA run behavior

`get_test_run(run_id)` raises `LookupError` with a message such as `No QA test run found for ID QA-999.` when the ID is valid but no synthetic run matches it. Callers such as `main.py` catch the error and display its message. Invalid input uses `TypeError` for a non-string and `ValueError` for an empty or whitespace-only string.

## Agent tool evaluation cases

Use these cases to check the QA run assistant's expected behavior. The app checks that every run ID exists in `qa_data.py` before sending a request to Ollama. Its prompt-scope gate uses a small allowlist of QA-related words, so unsupported wording is rejected; add terms deliberately when expanding the assistant's supported QA questions. Malformed arguments and lookup exceptions are simulated in unit tests because they are tool failure cases, not ordinary user prompts.

| Case | Prompt or test input | Expected behavior |
|---|---|---|
| Known run | `Summarize QA test run QA-104.` | The app finds QA-104, sends the request with the `get_test_run` tool, and summarizes only the returned run data. |
| Multiple known runs | `Can you write a summary of QA-104 and QA-105?` | The app confirms both IDs exist; each tool call is checked against the requested IDs and the final answer uses both records. |
| Unknown run | `Summarize QA test run QA-999.` | The app reports that QA-999 is absent from `qa_data.py` and stops before contacting Ollama. |
| One known and one unknown run | `Summarize QA-104 and QA-999.` | The app reports QA-999 as missing, removes it from the prompt sent to Ollama, and summarizes QA-104. |
| Blank/missing ID | `Summarize the QA test run.` | The app asks for a run ID and stops before contacting Ollama. |
| Unrelated question | `What is the capital of France?` | The app explains that it only handles QA test-run questions and stops before contacting Ollama. |
| Mixed QA and unrelated question | `Summarize QA-104 and explain how to reverse a string in Python.` | The prompt-scope gate rejects the unrelated terms and stops before contacting Ollama. |
| Malformed tool arguments | Simulate malformed JSON such as `{"run_id": "QA-104"` (missing the closing brace). | The tool handler returns `invalid_arguments`; the lookup function is not called. |
| Tool exception | Simulate `get_test_run` raising `RuntimeError` for QA-104. | The handler returns the bounded message `The QA test run could not be retrieved.` and logs only the function name, run ID, and exception type. It does not expose the exception text or traceback. |

The malformed-arguments and tool-exception cases are covered by `tests/test_tool_safety.py`.

## Ollama settings for singleCall.py

`singleCall.py` reads `OLLAMA_MODEL` and `OLLAMA_THINK` from the project's `.env` file. Set the model to an installed Ollama tag such as `qwen3:latest`, and set thinking to `true` or `false`. The script validates both values and uses them in each chat call. The local `.env` file is ignored by Git; `.env.example` is a safe template.

Install the `.env` loader in the project's virtual environment and run the example:

```powershell
.\.venv\Scripts\python.exe -m pip install python-dotenv
ollama pull qwen3:latest
.\.venv\Scripts\python.exe singleCall.py
```

## HTTP status codes and JSON response

In `api_client.py`, `fetch_post(1)` sends an HTTP request to JSONPlaceholder. The **HTTP status code** tells whether the server handled the request successfully. A code from 200 through 299 means success; for example, 404 means the requested post was not found. The function raises a clear error for an unsuccessful status.

The **JSON response** is the data the server sends back as JSON text. For a post, it contains fields such as `id`, `title`, and `body`. The program parses that JSON into a Python dictionary and returns only those three fields for the rest of the app to use.

To leave the virtual environment when you are done:

```powershell
deactivate
```



