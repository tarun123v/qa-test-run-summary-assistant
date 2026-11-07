# Test Run Summary Assistant

A small Python practice project that formats a readable summary from sample QA test-run data.

## Requirements

- Python 3.10 or later
- PowerShell (the commands below are for Windows)

## Set up the project

Open PowerShell in the project folder and create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

When it is active, PowerShell shows `(.venv)` at the start of the prompt. This project currently uses only Python's standard library, so no packages need to be installed.

## Run the program

From the project folder, with the virtual environment active, run:

```powershell
python main.py
```

Expected output:

```text
Test Run Summary Assistant
Run QA-104 is completed: 18 tests passed and 2 failed. Failing tests: test_login_timeout, test_cart_total.
```

To leave the virtual environment when you are done:

```powershell
deactivate
```
