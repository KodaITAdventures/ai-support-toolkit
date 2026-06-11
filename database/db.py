import sqlite3
from datetime import datetime


def initialize_database():

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            support_mode TEXT,
            prompt TEXT,
            response TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_data BLOB NOT NULL,
            FOREIGN KEY (session_id) REFERENCES support_history(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_session_attachments_session_id
        ON session_attachments (session_id)
    """)

    conn.commit()
    conn.close()

def save_session(
    support_mode,
    prompt,
    response,
    attachments=None
):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO support_history (
            timestamp,
            support_mode,
            prompt,
            response
        )
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        support_mode,
        prompt,
        response
    ))

    session_id = cursor.lastrowid

    if attachments:
        cursor.executemany("""
            INSERT INTO session_attachments (
                session_id,
                filename,
                mime_type,
                file_size,
                file_data
            )
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                session_id,
                attachment["filename"],
                attachment["mime_type"],
                attachment["file_size"],
                attachment["data"]
            )
            for attachment in attachments
        ])

    conn.commit()

    conn.close()

    return session_id

def get_session_by_id(session_id):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM support_history
        WHERE id = ?
    """, (session_id,))

    session = cursor.fetchone()

    conn.close()

    return session

def get_adjacent_session_ids(session_id):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(id)
        FROM support_history
        WHERE id < ?
    """, (session_id,))

    previous_session_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MIN(id)
        FROM support_history
        WHERE id > ?
    """, (session_id,))

    next_session_id = cursor.fetchone()[0]

    conn.close()

    return previous_session_id, next_session_id

def delete_session(session_id):

    conn = sqlite3.connect("support_history.db")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM session_attachments
            WHERE session_id = ?
        """, (session_id,))

        cursor.execute("""
            DELETE FROM support_history
            WHERE id = ?
        """, (session_id,))

        deleted = cursor.rowcount == 1

        conn.commit()

        return deleted
    finally:
        conn.close()

def get_session_attachments(session_id):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            filename,
            mime_type,
            file_size
        FROM session_attachments
        WHERE session_id = ?
        ORDER BY id
    """, (session_id,))

    attachments = cursor.fetchall()

    conn.close()

    return attachments

def get_session_attachment(session_id, attachment_id):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            filename,
            mime_type,
            file_size,
            file_data
        FROM session_attachments
        WHERE session_id = ?
        AND id = ?
    """, (
        session_id,
        attachment_id
    ))

    attachment = cursor.fetchone()

    conn.close()

    return attachment

def search_sessions(mode, search_text):

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    if mode and search_text:

        cursor.execute("""
            SELECT *
            FROM support_history
            WHERE support_mode = ?
            AND prompt LIKE ?
            ORDER BY id DESC
        """, (
            mode,
            f"%{search_text}%"
        ))

    elif mode:

        cursor.execute("""
            SELECT *
            FROM support_history
            WHERE support_mode = ?
            ORDER BY id DESC
        """, (mode,))

    elif search_text:

        cursor.execute("""
            SELECT *
            FROM support_history
            WHERE prompt LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search_text}%",
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM support_history
            ORDER BY id DESC
        """)

    sessions = cursor.fetchall()

    conn.close()

    return sessions

def get_paginated_sessions(page=1, per_page=10):

    offset = (page - 1) * per_page

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            support_mode,
            prompt
        FROM support_history
        ORDER BY id DESC
        LIMIT ?
        OFFSET ?
    """, (
        per_page,
        offset
    ))

    sessions = cursor.fetchall()

    conn.close()

    return sessions

def get_total_session_count():

    conn = sqlite3.connect("support_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_history
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count

def get_mode_count(mode):

    conn = sqlite3.connect("support_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_history
        WHERE support_mode = ?
    """, (mode,))

    count = cursor.fetchone()[0]

    conn.close()

    return count
