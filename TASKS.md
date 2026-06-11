# TASKS.md

## Project Roadmap

This roadmap prioritizes user-facing functionality, portfolio and resume value,
demonstrable features, and work that makes AI Support Toolkit feel like a
complete product.

### Completed Features

- [x] View Session History
- [x] Search Session History
- [x] Pagination
- [x] Statistics Dashboard

### P0 - Highest Priority

#### 1. Delete Session History

**Status: Implemented**

- [x] Add a Delete action to the session details page.
- [x] Require confirmation before deletion.
- [x] Delete the selected session from SQLite.
- [x] Redirect to session history with clear success or failure feedback.
- [x] Handle nonexistent session IDs safely.

#### 2. Export Session to PDF

**Status: Implemented and Verified**

- [x] Add an Export to PDF action to the session details page.
- [x] Include the session ID, timestamp, support mode, original issue, and AI
  response.
- [x] Produce a readable document with formatted headings, lists, and code
  blocks.
- [x] Use a meaningful download filename.
- [x] Block external and local resource resolution during PDF generation.
- [x] Verify generated PDF metadata, issue text, and response content.

#### 3. Print Session

**Status: Implemented**

- [x] Add a Print action to the session details page.
- [x] Create print-specific CSS that removes navigation and other controls.
- [x] Preserve readable response formatting and code blocks in print output.
- [x] Include useful session metadata on the printed page.

#### 4. Email Session

**Status: Implemented**

##### Implementation Notes

Add an **Email Session** action to current and saved session workflows. It
displays a form for up to ten comma- or semicolon-separated recipient addresses
and an optional subject override, then submits to a POST-only Flask route.

The email should contain a controlled plain-text and HTML summary and attach
the existing session PDF. Use Python's standard `smtplib` and
`email.message.EmailMessage`; no new dependency is recommended.

**Proposed files**

- `app.py`: Add SMTP configuration, shared PDF generation, validation, email
  sending, and fixed feedback handling.
- `templates/session.html`: Add the email form and success or failure feedback.
- `static/style.css`: Add minimal email form and feedback styling.
- `docs/MAINTAINER_GUIDE.md`: Document environment variable names without
  values.
- `requirements.txt`: No expected change.

**Proposed route**

```text
POST /session/<int:session_id>/email
```

Expected form fields:

- `recipient_email`: required.
- `email_subject`: optional.

Use Post/Redirect/Get so refreshing the session page does not resend the email.
Return the existing missing-session page with HTTP 404 for nonexistent IDs.

**Email content**

- Session ID.
- Timestamp.
- Support mode.
- Original issue.
- AI response summary.
- PDF attachment named `support-session-<id>.pdf`.

**PDF reuse**

Extract the existing in-memory PDF creation into a small helper such as
`generate_session_pdf(session)`. Both the PDF download route and email route
should call this helper so downloaded and attached PDFs remain identical. Keep
the existing resource blocking behavior.

**SMTP configuration**

Read configuration only from environment variables:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_USE_TLS
```

Recommended providers:

- Mailtrap Email Sandbox for development and portfolio demonstrations.
- SendGrid SMTP for a production-style hosted option.
- Amazon SES SMTP for an infrastructure-focused deployment.
- Microsoft 365 or Gmail SMTP for personal testing where authentication policy
  permits it.

Use a finite connection timeout and TLS by default. Do not log credentials or
show raw SMTP/provider errors to users.

**Validation and safety**

- [x] Require and validate up to ten recipient email addresses.
- [x] Reject newline characters in recipient and subject fields.
- [x] Apply reasonable length limits to recipient and subject.
- [x] Use a default subject:
  `AI Support Session #<id> - <support_mode>`.
- [x] Keep SMTP credentials exclusively in environment configuration.
- [x] Do not store recipients or send status in SQLite.
- [x] Stop sending if PDF generation fails.
- [x] Return fixed success, validation, configuration, and send-failure
  messages.
- [x] Do not expose exception text, provider responses, credentials, usernames,
  or host details.
- [x] Keep the email form excluded from browser printing.
- [ ] Add CSRF protection when practical for the email-sending form.

**Provider and delivery risks**

- Session content may contain sensitive infrastructure data.
- SMTP providers differ in TLS, authentication, sender verification, and port
  requirements.
- Successful SMTP handoff does not guarantee inbox delivery.
- Sending synchronously may make the request slow, but is acceptable for the
  initial small implementation.
- Post/Redirect/Get prevents refresh resends but does not prevent repeated
  submissions.
- Stored AI response HTML should not be inserted into email without controlled
  rendering or sanitization.

#### 5. Copy Response Button

**Status: Implemented**

- [x] Add a Copy Response button to the current response and session details
  views.
- [x] Copy readable response text rather than page controls or unrelated
  content.
- [x] Show brief success or failure feedback.
- [x] Support browsers where the Clipboard API is unavailable or denied.

### P1 - Medium Priority

#### 6. File Upload Support

**Status: Implemented**

- [x] Allow up to five files in one analysis request.
- [x] Support `.txt`, `.log`, `.csv`, `.json`, and text-based `.pdf` files.
- [x] Enforce 2 MB per-file, 5 MB combined, and 6 MB request limits.
- [x] Extract and normalize readable text entirely in memory.
- [x] Truncate extracted text at 30,000 characters per file and 75,000
  characters total with `[TRUNCATED]` markers.
- [x] Reject binary text files and encrypted or unreadable PDFs.
- [x] Include valid file text in the prompt with filename boundaries and
  untrusted-content instructions.
- [x] Show selected, accepted, skipped, and truncated file information.
- [x] Save only the original issue text and AI response to SQLite.
- [x] Save validated original uploads with the session for later download.

### P2 - Low Priority

#### 7. Docker

- [x] Add a production-oriented `Dockerfile`.
- [x] Add a `.dockerignore` that excludes `.env`, `venv/`, caches, and local
  development artifacts.
- [x] Document environment variables, port mapping, and startup commands.
- [x] Define how the SQLite database is persisted with a mounted volume.
- [x] Run the application through a production WSGI server rather than Flask's
  debug server.
- [x] Build and run the image on a machine with Docker installed.

## Recommended Delivery Order

1. Delete Session History
2. Copy Response Button
3. Print Session
4. Export Session to PDF
5. Email Session
6. File Upload Support
7. Docker

This order starts with a missing history-management capability, then delivers
two quick and highly visible session actions. PDF export builds on print-ready
presentation, while email follows once a reusable session export format is
clear.

## Technical Debt

- [ ] Make the SQLite database path explicit and independent of the process
  working directory.
- [x] Consolidate duplicate total-session count functions.
- [x] Remove unused database functions or connect them to active features.
- [x] Remove obsolete debug `print()` calls.
- [ ] Normalize prompt formatting, including the duplicated `Focus on:` line in
  the AWS prompt.
- [ ] Define support-mode labels in one shared location.
- [ ] Validate pagination inputs and define behavior for invalid page numbers.
- [x] Navigate to the nearest existing previous or next session instead of
  assuming adjacent IDs exist.
- [ ] Paginate filtered search results if result volume makes it necessary.
- [ ] Return HTTP 404 for missing session pages.
- [x] Add GitHub-ready project documentation, an environment template, and
  appropriate repository ignore rules.
- [ ] Add focused automated tests when needed to implement or protect roadmap
  features.

## Security Improvements

- [ ] Sanitize AI-generated HTML before rendering it with Jinja's `safe`
  filter.
- [ ] Escape user-visible error content and keep detailed exceptions in
  server-side logs.
- [ ] Validate `support_mode` against the supported mode allowlist.
- [ ] Decide whether failed OpenAI calls should be stored as sessions.
- [ ] Add CSRF protection before introducing destructive or email-sending
  forms.
- [x] Apply upload type, size, filename, and content validation for supported
  troubleshooting file uploads.
- [ ] Add retention and deletion guidance for prompts, responses, and uploaded
  logs that may contain sensitive infrastructure data.
- [ ] Keep OpenAI and email provider credentials out of source code, logs,
  rendered pages, and exported files.

## Future Refactoring

These items are intentionally below the product roadmap. Undertake them only
when they are required by a planned feature or when current structure becomes a
clear delivery obstacle.

- [ ] Consider moving route handlers into Flask blueprints under `routes/`.
- [ ] Consider introducing an application factory and test configuration.
- [ ] Consider centralizing database connection lifecycle management.
- [ ] Consider separating OpenAI success results from typed service failures.
- [ ] Consider storing Markdown rather than rendered HTML if export channels
  need a shared source format.
- [ ] Consider extracting reusable session presentation logic for web, print,
  PDF, and email output.
