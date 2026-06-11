# Screenshot Capture Guide

The PNG files in this directory were captured from a local application instance
using an isolated SQLite database populated with invented demo sessions. The
capture process did not call OpenAI, send email, or read the project's local
session database.

README gallery images:

```text
main-dashboard.png
session-history.png
session-detail.png
statistics-dashboard.png
multi-file-upload-example.png
email-session.png
```

## Capture Setup

1. Activate the project virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Configure a local `.env` without exposing its values.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000`.
6. Use a clean desktop browser window around 1440 by 1000 pixels.
7. Hide bookmarks, notifications, unrelated tabs, downloads, and personal
   browser-profile details where practical.
8. Use only invented or sanitized demo content.

Do not submit a new AI request solely for screenshots. Prefer an isolated demo
database or an existing sanitized session.

## Sample Azure Issue

Use this only after approval for an OpenAI API call, or use an existing saved
demo response representing the same scenario:

```text
Azure MFA NPS Extension authentication is failing.

Environment:
- Windows Server 2022 NPS
- Azure MFA NPS Extension
- On-prem Active Directory
- VPN authentication through RADIUS

Symptoms:
- User enters correct credentials
- VPN client reports authentication failure
- NTRadPing returns Access-Reject
- Azure MFA portal shows no MFA prompts
- NPS logs show Access-Challenge
```

## Screenshot Checklist

### `main-dashboard.png`

- Show the title, support-mode selector, issue field, upload panel, Analyze
  button, and Statistics Dashboard link.
- Keep issue and search fields free of personal or customer data.

### `session-history.png`

- Show search controls and multiple sanitized history cards.
- Keep issue text invented and suitable for public demonstration.

### `session-detail.png`

- Show sanitized session metadata, issue text, response heading, navigation,
  search, and session actions.
- Avoid framing the email recipient field with a real address.

### `statistics-dashboard.png`

- Show the dashboard heading and all mode-count cards.
- Session counts may reflect local demo data but must not reveal content.

### `multi-file-upload-example.png`

- Show multiple invented attachment names and their download actions.
- Do not upload or display real logs.

### `email-session.png`

- Show recipient guidance, optional subject, and the start of the sanitized
  response.
- Leave recipients empty and never display a real email address.

## Review Before Publishing

- Confirm there are no credentials or `.env` values.
- Confirm there is no customer or personal information.
- Confirm no private hostnames, addresses, usernames, or local filesystem paths
  are visible.
- Confirm every screenshot represents implemented behavior.
- Confirm screenshots use the exact expected filenames.
