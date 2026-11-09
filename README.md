# Test Run Summary Assistant

A small Python practice project that summarizes synthetic QA test runs and fetches a sample post from JSONPlaceholder.

## Project files

- `main.py` demonstrates known, unknown, and blank run IDs; it summarizes a found run, displays lookup errors, and demonstrates the API call.
- `qa_data.py` stores three invented QA runs: an all-passing run, a run with failures, and a run with failures and blocked tests.
- `qa_tools.py` validates and normalizes a run ID, returns an isolated copy of the matching synthetic run, and raises `LookupError` when no run matches. It only reads data; it cannot change status, delete results, or trigger reruns.
- `api_client.py` fetches a post and returns its ID, title, and body.

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

When it is active, PowerShell shows `(.venv)` at the start of the prompt. This project uses Python's standard library, so no packages need to be installed.

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
## Missing QA run behavior

`get_test_run(run_id)` raises `LookupError` with a message such as `No QA test run found for ID QA-999.` when the ID is valid but no synthetic run matches it. Callers such as `main.py` catch the error and display its message. Invalid input uses `TypeError` for a non-string and `ValueError` for an empty or whitespace-only string.

## HTTP status codes and JSON response

In `api_client.py`, `fetch_post(1)` sends an HTTP request to JSONPlaceholder. The **HTTP status code** tells whether the server handled the request successfully. A code from 200 through 299 means success; for example, 404 means the requested post was not found. The function raises a clear error for an unsuccessful status.

The **JSON response** is the data the server sends back as JSON text. For a post, it contains fields such as `id`, `title`, and `body`. The program parses that JSON into a Python dictionary and returns only those three fields for the rest of the app to use.

To leave the virtual environment when you are done:

```powershell
deactivate
```

