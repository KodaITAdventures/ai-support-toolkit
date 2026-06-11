# Security Notes

AI Support Toolkit is designed for local development and portfolio
demonstration. This document records important handling guidance and known
security gaps; it is not a production security certification.

## Sensitive Data

Issue descriptions and troubleshooting files may contain credentials,
hostnames, addresses, tokens, account identifiers, or internal configuration.
Sanitize content before submitting it.

Submitted issue text, generated responses, and accepted original uploads are
stored in the local SQLite database. Extracted prompt text is processed in
memory and is not stored separately.

## Secrets

Store OpenAI and SMTP credentials only in `.env` or process environment
variables. Never place real values in:

- `.env.example`
- Source code
- Documentation
- Screenshots
- Commit messages
- Logs or issue reports

The repository `.gitignore` excludes `.env` and local database files, but
ignore rules do not remove files that were already committed.

## Current Safeguards

- Parameterized SQLite values in the database layer.
- Upload count, size, extension, MIME, and basic content validation.
- In-memory upload processing.
- Encrypted and unreadable PDF rejection.
- Fixed user-facing email failure messages.
- SMTP configuration through environment variables.
- External and local PDF resource loading blocked during export.
- Recipient and email-subject validation.

## Known Gaps

- No authentication or authorization.
- No CSRF protection for state-changing forms.
- No rate limiting or abuse controls.
- AI-generated HTML is rendered as trusted stored HTML.
- No automated secret detection or redaction.
- No formal session retention, backup, or encryption policy.
- No security headers or production reverse-proxy configuration.
- Flask's development server is used when `app.py` is run directly; debug mode
  is disabled by default.
- Email and AI requests are synchronous external operations.

## Deployment Warning

Do not expose the current application directly to the public internet. A
production deployment would require, at minimum:

- Authentication and authorization
- CSRF protection
- Output sanitization
- Secure session and cookie configuration
- Rate limiting and request monitoring
- A hardened reverse proxy and TLS termination in front of Gunicorn
- TLS termination
- Secret management
- Logging that excludes submitted content and credentials
- Database backup, retention, and access controls
- Dependency and vulnerability maintenance

## Screenshot Safety

Screenshots intended for GitHub should use only invented demo content. Review
the entire frame before publishing, including browser chrome, visible session
history, email fields, filenames, and downloaded-file areas.
