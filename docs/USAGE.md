# Usage Guide

## Analyze an Issue

1. Start the application and open `http://127.0.0.1:5000`.
2. Select a support mode:
   - Azure
   - AWS
   - Terraform
   - Remote Access & VDI
   - General Infrastructure
3. Enter an issue description.
4. Optionally select up to five supported troubleshooting files.
5. Select **Analyze Issue**.

The analysis uses the issue description and any valid extracted file text. A
successful response is saved as a new session. The original issue, AI response,
and accepted original files are stored. Extracted prompt text is not stored as
a separate database field.

## File Uploads

Supported extensions:

- `.txt`
- `.log`
- `.csv`
- `.json`
- `.pdf`

Limits:

- Five files per analysis
- 2 MB per file
- 5 MB combined
- 6 MB total request
- 30,000 extracted characters per file
- 75,000 extracted characters total

Text beyond extraction limits is marked `[TRUNCATED]`. Unsupported, unreadable,
or encrypted files are skipped with a safe validation message. Analysis can
continue when at least one selected file is valid. PDF files must contain
extractable text; OCR and password-protected PDFs are not supported.

## Current Response Actions

After analysis, the home page displays the new session ID and provides:

- **Copy Response**
- **Export to PDF**
- **Print Session**
- **View Session**

Opening the saved session provides the complete session workflow.

## Session History

The home page displays recent sessions with pagination. Search supports:

- Support-mode filtering
- Original issue-text matching
- Combined mode and text filtering

Saved session pages also provide issue-text search and direct session-ID
navigation.

## Saved Session Actions

### Copy Response

Copies readable AI response text without copying navigation or action controls.
A brief status message reports success or failure.

### Print Session

Uses the browser print dialog. Print-specific styles omit navigation, search,
email, delete, and other interactive controls.

### Export to PDF

Downloads a PDF containing:

- Session ID
- Timestamp
- Support mode
- Original issue
- AI response

The filename follows `support-session-<id>.pdf`.

### Email Session

Enter up to ten recipient addresses separated by commas or semicolons and
optionally override the subject. The app sends one message with a plain-text
and HTML summary and the generated session PDF attached.

Email requires valid SMTP environment configuration. The interface displays
fixed success or failure messages and does not expose provider errors or
credentials.

### Delete Session

Deletes only the selected session after browser confirmation, then returns to
the main history page with status feedback.

### Uploaded Files

Validated original uploads appear on the saved session page with filename,
content type, size, and a download action. Deleting the session also deletes
its stored attachments.

## Statistics

The Statistics Dashboard shows the total saved-session count and counts for
each supported mode.

## Demo Data Guidance

Use invented or sanitized infrastructure examples. Do not enter:

- API keys or passwords
- Customer names or identifiers
- Private hostnames or addresses
- Production logs containing secrets
- Personal or regulated information
