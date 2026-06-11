from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
    send_file
)
from email.message import EmailMessage
from html import escape
from html.parser import HTMLParser
from io import BytesIO
import os
import re
import smtplib
import sqlite3
import ssl
from dotenv import load_dotenv
from werkzeug.exceptions import RequestEntityTooLarge
from xhtml2pdf import pisa

from prompts.azure_prompt import get_azure_prompt
from prompts.aws_prompt import get_aws_prompt
from prompts.terraform_prompt import get_terraform_prompt
from prompts.vdi_prompt import get_vdi_prompt
from prompts.general_prompt import get_general_prompt
from services.openai_service import generate_ai_response
from services.file_upload_service import (
    build_analysis_input,
    process_uploads
)

from database.db import (
    initialize_database,
    save_session,
    get_session_by_id,
    get_adjacent_session_ids,
    delete_session,
    search_sessions,
    get_paginated_sessions,
    get_total_session_count,
    get_mode_count,
    get_session_attachments,
    get_session_attachment
)

load_dotenv()


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

initialize_database()

def block_pdf_resources(uri, rel):

    raise ValueError("External PDF resources are not allowed.")

def generate_session_pdf(session):

    html = render_template(
        "session_pdf.html",
        session=session
    )

    pdf_buffer = BytesIO()

    pdf_status = pisa.CreatePDF(
        html,
        dest=pdf_buffer,
        encoding="utf-8",
        link_callback=block_pdf_resources
    )

    if pdf_status.err:
        raise RuntimeError("PDF generation failed.")

    return pdf_buffer.getvalue()

class ResponseTextParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parts = []
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored_depth += 1
            return

        if self.ignored_depth:
            return

        if tag in {"br", "p", "div", "li", "h1", "h2", "h3", "h4", "pre"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignored_depth = max(0, self.ignored_depth - 1)
            return

        if self.ignored_depth:
            return

        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "pre"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignored_depth:
            self.parts.append(data)

    def get_text(self):
        lines = (line.strip() for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)

def get_response_text(response_html):

    parser = ResponseTextParser()
    parser.feed(response_html or "")
    return parser.get_text()

def is_valid_email_address(recipient):

    if (
        not recipient
        or len(recipient) > 254
        or "\r" in recipient
        or "\n" in recipient
        or "," in recipient
        or ";" in recipient
    ):
        return False

    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient) is not None

def parse_email_recipients(recipient_text):

    if not recipient_text or "\r" in recipient_text or "\n" in recipient_text:
        return []

    recipients = []

    for recipient in re.split(r"[;,]", recipient_text):
        recipient = recipient.strip()

        if not recipient:
            continue

        if recipient not in recipients:
            recipients.append(recipient)

    if (
        not recipients
        or len(recipients) > 10
        or any(not is_valid_email_address(recipient) for recipient in recipients)
    ):
        return []

    return recipients

@app.route("/session/<int:session_id>")
def view_session(session_id):

    session = get_session_by_id(session_id)

    if session is None:
        return render_template("session_not_found.html")

    previous_session_id, next_session_id = get_adjacent_session_ids(session_id)
    attachments = get_session_attachments(session_id)

    session_filter_mode = request.args.get("session_filter_mode", "")
    session_search_text = request.args.get("session_search_text", "")
    session_search_results = None

    if session_filter_mode or session_search_text:
        session_search_results = search_sessions(
            session_filter_mode,
            session_search_text
        )

    email_messages = {
        "success": ("Session emailed successfully.", "success"),
        "invalid": (
            "Enter up to 10 valid recipient email addresses.",
            "error"
        ),
        "config": (
            "Unable to email session. Please check the email configuration and try again.",
            "error"
        ),
        "error": ("Unable to email session. Please try again.", "error")
    }

    email_message, email_message_type = email_messages.get(
        request.args.get("email_status", ""),
        ("", "")
    )

    return render_template(
        "session.html",
        session=session,
        previous_session_id=previous_session_id,
        next_session_id=next_session_id,
        session_filter_mode=session_filter_mode,
        session_search_text=session_search_text,
        session_search_results=session_search_results,
        auto_print=request.args.get("print") == "1",
        auto_open_email=request.args.get("email") == "1",
        attachments=attachments,
        email_message=email_message,
        email_message_type=email_message_type
    )

@app.route(
    "/session/<int:session_id>/attachments/<int:attachment_id>/download"
)
def download_session_attachment(session_id, attachment_id):

    attachment = get_session_attachment(session_id, attachment_id)

    if attachment is None:
        return render_template("session_not_found.html"), 404

    return send_file(
        BytesIO(attachment[4]),
        mimetype=attachment[2],
        as_attachment=True,
        download_name=attachment[1]
    )

@app.route("/session/<int:session_id>/pdf")
def export_session_pdf(session_id):

    session = get_session_by_id(session_id)

    if session is None:
        return render_template("session_not_found.html"), 404

    try:
        response = make_response(generate_session_pdf(session))
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'attachment; filename="support-session-{session_id}.pdf"'
        )

        return response

    except Exception:
        return "Unable to export this session to PDF. Please try again.", 500

@app.route("/session/<int:session_id>/email", methods=["POST"])
def email_session(session_id):

    session = get_session_by_id(session_id)

    if session is None:
        return render_template("session_not_found.html"), 404

    recipient_text = request.form.get("recipient_email", "").strip()
    recipients = parse_email_recipients(recipient_text)
    subject = request.form.get("email_subject", "").strip()

    if (
        not recipients
        or len(subject) > 200
        or "\r" in subject
        or "\n" in subject
    ):
        return redirect(url_for(
            "view_session",
            session_id=session_id,
            email_status="invalid"
        ))

    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port_text = os.getenv("SMTP_PORT", "").strip()
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "").strip()
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower()

    try:
        smtp_port = int(smtp_port_text)
    except ValueError:
        smtp_port = 0

    if (
        not smtp_host
        or not 1 <= smtp_port <= 65535
        or not is_valid_email_address(smtp_from_email)
        or smtp_use_tls not in {"true", "false"}
        or bool(smtp_username) != bool(smtp_password)
    ):
        return redirect(url_for(
            "view_session",
            session_id=session_id,
            email_status="config"
        ))

    email_subject = subject or (
        f"AI Support Session #{session_id} - {session[2]}"
    )
    response_text = get_response_text(session[4])
    plain_body = (
        f"Support Session #{session_id}\n"
        f"Created: {session[1]}\n"
        f"Support Mode: {session[2]}\n\n"
        f"Issue\n{session[3]}\n\n"
        f"AI Response\n{response_text}\n"
    )
    html_body = (
        "<h1>Support Session #"
        f"{session_id}</h1>"
        f"<p><strong>Created:</strong> {escape(session[1])}<br>"
        f"<strong>Support Mode:</strong> {escape(session[2])}</p>"
        f"<h2>Issue</h2><p>{escape(session[3])}</p>"
        f"<h2>AI Response</h2><pre>{escape(response_text)}</pre>"
    )

    try:
        pdf_bytes = generate_session_pdf(session)

        message = EmailMessage()
        message["From"] = smtp_from_email
        message["To"] = ", ".join(recipients)
        message["Subject"] = email_subject
        message.set_content(plain_body)
        message.add_alternative(html_body, subtype="html")
        message.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=f"support-session-{session_id}.pdf"
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=10
        ) as smtp:
            if smtp_use_tls == "true":
                smtp.starttls(context=ssl.create_default_context())

            if smtp_username:
                smtp.login(smtp_username, smtp_password)

            smtp.send_message(message)

    except Exception:
        return redirect(url_for(
            "view_session",
            session_id=session_id,
            email_status="error"
        ))

    return redirect(url_for(
        "view_session",
        session_id=session_id,
        email_status="success"
    ))

@app.route("/session/<int:session_id>/delete", methods=["POST"])
def delete_session_route(session_id):

    try:
        deleted = delete_session(session_id)
    except sqlite3.Error:
        return redirect(url_for("home", delete_status="error"))

    if not deleted:
        return redirect(url_for("home", delete_status="not_found"))

    return redirect(url_for("home", delete_status="success"))

@app.route("/session-search", methods=["POST"])
def session_search():

    session_id = request.form["session_id"]

    return redirect(f"/session/{session_id}")

@app.route("/stats")
def stats():

    total_sessions = get_total_session_count()

    azure_count = get_mode_count("Azure")
    aws_count = get_mode_count("AWS")
    terraform_count = get_mode_count("Terraform")
    vdi_count = get_mode_count("Remote Access & VDI")
    general_count = get_mode_count("General Infrastructure")

    return render_template(
        "stats.html",
        total_sessions=total_sessions,
        azure_count=azure_count,
        aws_count=aws_count,
        terraform_count=terraform_count,
        vdi_count=vdi_count,
        general_count=general_count
    )


@app.route("/", methods=["GET", "POST"])
def home():

    response = ""
    selected_mode = "Azure"
    log_text_value = ""
    saved_session_id = None
    accepted_uploads = []
    stored_uploads = []
    upload_errors = []
    delete_status = request.args.get("delete_status", "")

    delete_messages = {
        "success": ("Session deleted successfully.", "success"),
        "not_found": ("Session could not be deleted because it no longer exists.", "error"),
        "error": ("Session could not be deleted. Please try again.", "error")
    }

    delete_message, delete_message_type = delete_messages.get(
        delete_status,
        ("", "")
    )

    page = request.args.get("page", 1, type=int)

    per_page = 10

    recent_sessions = get_paginated_sessions(
    page,
    per_page
    )

    total_sessions = get_total_session_count()

    total_pages = (
    total_sessions + per_page - 1
    ) // per_page

    filter_mode = ""

    if request.method == "POST":

        if "filter_mode" in request.form:

            filter_mode = request.form["filter_mode"]
            search_text = request.form.get ("search_text", "")

            recent_sessions = search_sessions(
                filter_mode,
                search_text
            )

            return render_template(
                "index.html",
                response="",
                selected_mode="Azure",
                log_text_value="",
                recent_sessions=recent_sessions,
                filter_mode=filter_mode,
                search_text = search_text,
                page=page,
                total_pages=total_pages,
                delete_message=delete_message,
                delete_message_type=delete_message_type,
                saved_session_id=saved_session_id,
                accepted_uploads=accepted_uploads,
                upload_errors=upload_errors
            )

        log_text = request.form.get("log_text", "")
        support_mode = request.form["support_mode"]

        selected_mode = support_mode
        log_text_value = log_text

        if not log_text.strip():    
            response = """
            <div class='error-box'>
                Please enter an issue description before submitting.
            </div>
            """
            
            return render_template(
                "index.html",
                response=response,
                selected_mode=selected_mode,
                log_text_value=log_text_value,
                recent_sessions=recent_sessions,
                page=page,
                total_pages=total_pages,
                delete_message=delete_message,
                delete_message_type=delete_message_type,
                saved_session_id=saved_session_id,
                accepted_uploads=accepted_uploads,
                upload_errors=upload_errors
            )

        upload_result = process_uploads(
            request.files.getlist("support_files")
        )
        accepted_uploads = upload_result.accepted_file_details
        stored_uploads = upload_result.stored_files
        upload_errors = upload_result.errors

        if upload_result.had_files and not upload_result.accepted_files:
            return render_template(
                "index.html",
                response="",
                selected_mode=selected_mode,
                log_text_value=log_text_value,
                recent_sessions=recent_sessions,
                filter_mode="",
                search_text="",
                page=page,
                total_pages=total_pages,
                delete_message=delete_message,
                delete_message_type=delete_message_type,
                saved_session_id=saved_session_id,
                accepted_uploads=accepted_uploads,
                upload_errors=upload_errors
            )

        analysis_input = build_analysis_input(
            log_text,
            upload_result.prompt_text
        )

        if support_mode == "Azure":
            prompt = get_azure_prompt(analysis_input)

        elif support_mode == "AWS":
            prompt = get_aws_prompt(analysis_input)

        elif support_mode == "Terraform":
            prompt = get_terraform_prompt(analysis_input)

        elif support_mode == "Remote Access & VDI":
            prompt = get_vdi_prompt(analysis_input)

        else:
            prompt = get_general_prompt(analysis_input)


        response = generate_ai_response(prompt)

        saved_session_id = save_session(
            support_mode,
            log_text,
            response,
            stored_uploads
        )

    recent_sessions = get_paginated_sessions(
        page,
        per_page
    )

    return render_template(
        "index.html",
        response=response,
        selected_mode=selected_mode,
        log_text_value=log_text_value,
        recent_sessions = recent_sessions,
        filter_mode="",
        search_text="",
        page=page,
        total_pages=total_pages,
        delete_message=delete_message,
        delete_message_type=delete_message_type,
        saved_session_id=saved_session_id,
        accepted_uploads=accepted_uploads,
        upload_errors=upload_errors
    )

@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(error):

    page = 1
    per_page = 10
    recent_sessions = get_paginated_sessions(page, per_page)
    total_sessions = get_total_session_count()
    total_pages = (total_sessions + per_page - 1) // per_page

    return render_template(
        "index.html",
        response="",
        selected_mode="Azure",
        log_text_value="",
        recent_sessions=recent_sessions,
        filter_mode="",
        search_text="",
        page=page,
        total_pages=total_pages,
        delete_message="",
        delete_message_type="",
        saved_session_id=None,
        accepted_uploads=[],
        upload_errors=["The request exceeds the 6 MB upload limit."]
    ), 413


if __name__ == "__main__":
    app.run(debug=False)
