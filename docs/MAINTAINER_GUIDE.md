# Maintainer Guide

## Purpose

This guide summarizes the repository conventions, runtime assumptions, and
verification expectations for contributors maintaining AI Support Toolkit.
Treat the existing application behavior and documented SQLite schema as the
source of truth.

## Project Map

- `app.py`: Flask application setup and all current route handlers.
- `database/db.py`: SQLite schema initialization and session queries.
- `services/openai_service.py`: OpenAI client setup, request handling, and
  Markdown-to-HTML conversion.
- `prompts/`: Shared response rules and support-mode prompt builders.
- `templates/`: Jinja templates for the main page, session details, statistics,
  and missing sessions.
- `static/style.css`: Shared application styling.
- `support_history.db`: Local SQLite database containing support sessions.
- `.env`: Local environment configuration. It currently defines
  `OPENAI_API_KEY`; never expose or commit its value.
- `venv/`: Local virtual environment; do not edit or treat as source.

## Runtime Assumptions

- Python is run from the project root because the database filename is a
  relative path.
- Dependencies are installed from `requirements.txt`.
- `OPENAI_API_KEY` is available through `.env` or the process environment.
- Email Session requires `SMTP_HOST`, `SMTP_PORT`, and `SMTP_FROM_EMAIL`.
  `SMTP_USE_TLS` is optional and defaults to `true`. `SMTP_USERNAME` and
  `SMTP_PASSWORD` are optional but must be provided together when
  authentication is required.
- Analysis uploads support `.txt`, `.log`, `.csv`, `.json`, and text-based
  `.pdf` files. Extraction is performed in memory: maximum 5 files, 2 MB per
  file, 5 MB combined, and 6 MB per request. Extracted text is limited to
  30,000 characters per file and 75,000 characters total. Accepted original
  files are stored as session attachments in SQLite.
- The application is intended for local/development use. `app.py` starts
  Flask's development server with debug mode disabled when run directly.
- The configured OpenAI model is `gpt-4.1-mini`.

## Common Commands

From the project root:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Container commands:

```powershell
docker build --tag ai-support-toolkit:latest .
docker run --env-file .env --publish 8000:8000 --mount source=ai-support-toolkit-data,target=/data ai-support-toolkit:latest
```

The default Flask development address is expected to be:

```text
http://127.0.0.1:5000
```

No automated test, lint, formatting, migration, packaging, or deployment
commands are currently defined in the repository.

## Change Guidelines

1. Keep changes narrowly scoped and preserve the current Flask/Jinja/SQLite
   design unless a task explicitly calls for an architectural change.
2. Do not edit `.env`, reveal credentials, or place secrets in documentation,
   logs, tests, or source code.
3. Do not modify or delete `support_history.db` unless a task explicitly
   requires a data change and includes a backup or migration plan.
4. Do not edit generated files under `__pycache__/` or dependencies under
   `venv/`.
5. Preserve the exact support-mode labels because they are stored in the
   database and used by filters and statistics:
   - `Azure`
   - `AWS`
   - `Terraform`
   - `Remote Access & VDI`
   - `General Infrastructure`
6. Use parameterized SQL for all values. The current database layer already
   follows this rule.
7. Escape user-provided content by default. Treat any use of Jinja's `safe`
   filter or generated HTML as a security-sensitive boundary.
8. Keep prompt behavior centralized in `prompts/`; shared output rules belong
   in `prompts/common_prompt_parts.py`.
9. Add focused tests when changing route behavior, database queries, prompt
    selection, or OpenAI error handling.
10. Persist only validated original uploads in `session_attachments`; do not
    store extracted prompt text separately.

## Verification Expectations

For documentation-only changes:

- Confirm only the intended Markdown files changed.
- Check links, paths, commands, and names against the repository.

For future application changes:

- Exercise the affected route with valid and invalid input.
- Confirm a successful analysis is stored and can be viewed.
- Confirm filtering, pagination, session lookup, and statistics still work
  when relevant.
- Avoid real OpenAI calls in automated tests; mock the service boundary.
- Verify database tests use a temporary database rather than
  `support_history.db`.

## Known Constraints

- All routes live in `app.py`.
- Database connections and the database path are repeated in
  `database/db.py`.
- OpenAI responses are converted to HTML and rendered with `safe`.
- Some API failure responses are also saved as sessions.
- Session navigation resolves the nearest lower and higher existing IDs.
- Search results are not paginated.
- The project does not currently include an automated test suite or CI
  workflow.

## Assumptions

- Existing rows in `support_history.db` are meaningful local data and should
  be preserved.
- Authentication and multi-user access are outside the current application
  scope.
- Public-internet production deployment is outside the current v1.0 scope.
- `TASKS.md`, `ARCHITECTURE.md`, and this guide should be updated when behavior
  or maintenance expectations change.
