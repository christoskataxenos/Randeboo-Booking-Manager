"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξενό Χρήστο

=============================================================================
ΑΡΧΕΙΟ: email_service.py
ΣΚΟΠΟΣ: Ασύγχρονη και μεμονωμένη αποστολή υπενθυμίσεων email μέσω SMTP.
=============================================================================
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import logging
import datetime

import database

# Ρυθμίσεις καταγραφής (Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_ics_content(date_str: str, start_time: str, duration_minutes: int, summary: str) -> str | None:
    """
    Δημιουργεί το περιεχόμενο ενός αρχείου .ics (iCalendar) συμβατό με Google Calendar & Outlook.
    """
    try:
        # Αναμενόμενο format εισόδου: DD/MM/YYYY HH:MM
        dt_start = datetime.datetime.strptime(f"{date_str} {start_time}", "%d/%m/%Y %H:%M")
        dt_end = dt_start + datetime.timedelta(minutes=int(duration_minutes))

        fmt = "%Y%m%dT%H%M%S"
        dt_start_str = dt_start.strftime(fmt)
        dt_end_str = dt_end.strftime(fmt)

        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//RandeBoo//NONSGML v1.0//EN
BEGIN:VEVENT
DTSTART:{dt_start_str}
DTEND:{dt_end_str}
SUMMARY:{summary}
DESCRIPTION:Υπενθύμιση Ραντεβού από RandeBoo
END:VEVENT
END:VCALENDAR"""
        return ics
    except Exception as e:
        logging.error(f"Σφάλμα δημιουργίας ICS: {e}")
        return None


def _get_smtp_server(settings: dict, context: ssl.SSLContext):
    """συνάρτηση για τη δημιουργία και σύνδεση στον SMTP server."""
    smtp_server = settings.get("smtp_server", "smtp.gmail.com")
    smtp_port = int(settings.get("smtp_port", 587))
    sender_email = settings.get("email_user")
    sender_password = settings.get("email_password")

    if not sender_email or not sender_password:
        return None, None

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        return server, sender_email
    except Exception as e:
        logging.error(f"SMTP Connection Error: {e}")
        return None, None


def _format_email_body(template: str, appt: dict, settings: dict, date_str: str) -> str:
    """Αντικαθιστά τα placeholders στο template με πραγματικά δεδομένα."""
    body = template.replace("{customer_name}", appt.get("customer_name", "Αγαπητέ Πελάτη"))
    body = body.replace("{appt_date}", date_str)
    body = body.replace("{start_time}", appt.get("start_time", ""))
    body = body.replace("{company_name}", settings.get("company_name", "RandeBoo"))
    body = body.replace("{phone}", settings.get("phone", ""))
    return body


def _attach_ics_file(msg: MIMEMultipart, date_str: str, appt: dict, company_name: str) -> None:
    """Δημιουργεί και επισυνάπτει το αρχείο .ics στο email."""
    summary = f"Ραντεβού - {company_name}"
    duration = appt.get("duration", 30)
    ics_text = generate_ics_content(date_str, appt.get("start_time"), duration, summary)
    
    if ics_text:
        attachment_part = MIMEBase("text", "calendar", method="REQUEST")
        attachment_part.set_payload(ics_text.encode("utf-8"))
        encoders.encode_base64(attachment_part)
        attachment_part.add_header("Content-Disposition", 'attachment; filename="appointment.ics"')
        msg.attach(attachment_part)

def send_single_reminder_async(appt: dict) -> None:
    """
    Ασύγχρονη κλήση για αποστολή υπενθύμισης σε έναν συγκεκριμένο πελάτη.
    """
    thread = threading.Thread(target=_send_single_reminder_worker, args=(appt,))
    thread.daemon = True
    thread.start()


def _send_single_reminder_worker(appt: dict):
    """
    Αποστολή μεμονωμένου email.
    """
    db_conn = None
    try:
        settings = database.get_business_settings()
        company_name = settings.get("company_name", "RandeBoo")
        
        # Επαγγελματικό προεπιλεγμένο πρότυπο στα Ελληνικά
        default_template = (
            "Αγαπητέ/ή {customer_name},\n\n"
            "Σας υπενθυμίζουμε το προγραμματισμένο ραντεβού σας με την επιχείρηση {company_name} "
            "στις {appt_date} και ώρα {start_time}.\n\n"
            "Σε περίπτωση που επιθυμείτε να ακυρώσετε ή να αλλάξετε το ραντεβού σας, "
            "παρακαλούμε επικοινωνήστε μαζί μας στο τηλέφωνο {phone}.\n\n"
            "Ευχαριστούμε,\n"
            "{company_name}"
        )
        template = settings.get("email_body_template", default_template)
        if not template or not template.strip():
            template = default_template
            
        should_attach = settings.get("add_to_calendar") == "1"

        cust_email = appt.get("customer_email")
        if not cust_email:
            customer = database.get_customer_by_email(appt.get("email", ""))
            if customer:
                cust_email = customer.get("email")

        if not cust_email:
            return

        context = ssl.create_default_context()
        server, sender_email = _get_smtp_server(settings, context)
        if not server:
            return

        with server:
            raw_date = appt.get("appt_date", "")
            if "-" in raw_date:
                d_parts = raw_date.split("-")
                date_str = f"{d_parts[2]}/{d_parts[1]}/{d_parts[0]}" if len(d_parts) == 3 else raw_date
            else:
                date_str = raw_date

            body = _format_email_body(template, appt, settings, date_str)
            msg = MIMEMultipart()
            msg["From"] = f"{company_name} <{sender_email}>"
            msg["To"] = cust_email
            msg["Subject"] = f"Υπενθύμιση Ραντεβού - {company_name}"
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if should_attach:
                _attach_ics_file(msg, date_str, appt, company_name)

            server.send_message(msg)
            db_conn = database.get_connection()
            db_conn.execute("UPDATE APPOINTMENTS SET reminder_sent = 1 WHERE appointment_id = ?", (appt["appointment_id"],))
            db_conn.commit()
            logging.info(f"Εστάλη μεμονωμένη υπενθύμιση στο: {cust_email}")

    except Exception as e:
        logging.error(f"Αποτυχία κατά την αποστολή μεμονωμένου email: {e}")
    finally:
        if db_conn:
            db_conn.close()
