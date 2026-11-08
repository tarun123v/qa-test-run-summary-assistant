# Test Run Summary Assistant

A small Python practice project that formats a readable summary from sample QA test-run data and fetches a sample post from JSONPlaceholder.

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

Expected output includes the QA summary and the title returned by the API:

```text
Test Run Summary Assistant
Run QA-104 is completed: 18 tests passed and 2 failed. Failing tests: test_login_timeout, test_cart_total.
Post title: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
```

## HTTP status codes and JSON response

In `api_client.py`, `fetch_post(1)` sends an HTTP request to JSONPlaceholder. The **HTTP status code** tells whether the server handled the request successfully. A code from 200 through 299 means success; for example, 404 means the requested post was not found. This function raises a clear error for an unsuccessful status.

The **JSON response** is the data the server sends back as JSON text. For a post, it contains fields such as `id`, `title`, and `body`. The program parses that JSON into a Python dictionary and returns only those three fields for the rest of the app to use.

To leave the virtual environment when you are done:

```powershell
deactivate
```
