import datetime
import os
import smtplib
import socket
import ssl
import urllib.parse
import secrets
import hashlib
import hmac
from email.message import EmailMessage

import anvil.server
import anvil.users
from anvil.tables import app_tables


RESET_TOKEN_LIFETIME_HOURS = 1


def _utcnow():
  return datetime.datetime.now(datetime.timezone.utc)


def _hash_token(token):
  return hashlib.sha256((token or "").encode("utf-8")).hexdigest()


def _get_user_by_email(email):
  return app_tables.users.get(email=email)


def _build_reset_link(base_url, email, token):
  parsed = urllib.parse.urlsplit(base_url or "")
  path = parsed.path or "/"
  current_query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
  query = [(k, v) for k, v in current_query if k not in ("reset_email", "reset_token")]
  query.extend([
    ("reset_email", email),
    ("reset_token", token),
  ])
  return urllib.parse.urlunsplit((
    parsed.scheme or "http",
    parsed.netloc or "localhost",
    path,
    urllib.parse.urlencode(query),
    "",
  ))


def _smtp_settings():
  host = os.environ.get("ENTRAPT_SMTP_HOST", "").strip()
  port = int(os.environ.get("ENTRAPT_SMTP_PORT", "587").strip())
  username = os.environ.get("ENTRAPT_SMTP_USERNAME", "").strip()
  password = os.environ.get("ENTRAPT_SMTP_PASSWORD", "")
  sender = os.environ.get("ENTRAPT_SMTP_FROM", username).strip()
  use_ssl = os.environ.get("ENTRAPT_SMTP_USE_SSL", "false").strip().lower() == "true"
  use_tls = os.environ.get("ENTRAPT_SMTP_USE_TLS", "true").strip().lower() == "true"

  if not host:
    raise RuntimeError("Password reset email is not configured. Set ENTRAPT_SMTP_HOST.")
  if not sender:
    raise RuntimeError("Password reset email is not configured. Set ENTRAPT_SMTP_FROM or ENTRAPT_SMTP_USERNAME.")

  return {
    "host": host,
    "port": port,
    "username": username,
    "password": password,
    "sender": sender,
    "use_ssl": use_ssl,
    "use_tls": use_tls,
  }


def _send_reset_email(recipient, reset_link):
  settings = _smtp_settings()
  print(
    "[password-reset] SMTP send attempt:",
    {
      "host": settings["host"],
      "port": settings["port"],
      "sender": settings["sender"],
      "recipient": recipient,
      "use_ssl": settings["use_ssl"],
      "use_tls": settings["use_tls"],
    },
  )

  message = EmailMessage()
  message["Subject"] = "Reset your EntraPT password"
  message["From"] = settings["sender"]
  message["To"] = recipient
  message.set_content(
    "A password reset was requested for your EntraPT account.\n\n"
    f"Open this link to continue:\n{reset_link}\n\n"
    f"This link expires in {RESET_TOKEN_LIFETIME_HOURS} hour(s).\n"
    "If you did not request this reset, you can ignore this email."
  )

  if settings["use_ssl"]:
    with smtplib.SMTP_SSL(
      settings["host"],
      settings["port"],
      context=ssl.create_default_context(),
      timeout=20,
    ) as smtp:
      if settings["username"]:
        smtp.login(settings["username"], settings["password"])
      smtp.send_message(message)
    return

  with smtplib.SMTP(settings["host"], settings["port"], timeout=20) as smtp:
    if settings["use_tls"]:
      smtp.starttls(context=ssl.create_default_context())
    if settings["username"]:
      smtp.login(settings["username"], settings["password"])
    smtp.send_message(message)


def _delete_existing_tokens(email):
  for row in app_tables.password_resets.search(email=email):
    row.delete()


def test_password_reset_smtp(recipient):
  normalized_email = (recipient or "").strip().lower()
  if not normalized_email:
    raise ValueError("Email address is required.")
  test_link = _build_reset_link("http://localhost", normalized_email, "test-token")
  _send_reset_email(normalized_email, test_link)
  return {"sent": True, "recipient": normalized_email}


def request_password_reset(email, reset_base_url):
  normalized_email = (email or "").strip().lower()
  if not normalized_email:
    raise ValueError("Email address is required.")

  user = _get_user_by_email(normalized_email)
  if user is None:
    return {"sent": False}

  token = secrets.token_urlsafe(32)
  now = _utcnow()
  expires_at = now + datetime.timedelta(hours=RESET_TOKEN_LIFETIME_HOURS)

  _delete_existing_tokens(normalized_email)
  app_tables.password_resets.add_row(
    email=normalized_email,
    token_hash=_hash_token(token),
    requested_at=now,
    expires_at=expires_at,
    used_at=None,
  )

  reset_link = _build_reset_link(reset_base_url, normalized_email, token)
  _send_reset_email(normalized_email, reset_link)
  return {"sent": True}


def _get_valid_reset_row(email, token):
  normalized_email = (email or "").strip().lower()
  token_hash = _hash_token(token)
  now = _utcnow()

  for row in app_tables.password_resets.search(email=normalized_email):
    stored_hash = row["token_hash"] or ""
    if not hmac.compare_digest(stored_hash, token_hash):
      continue
    if row["used_at"] is not None:
      return None
    expires_at = row["expires_at"]
    if expires_at is None or expires_at < now:
      return None
    return row
  return None


def login_user_for_password_reset(email, token):
  reset_row = _get_valid_reset_row(email, token)
  if reset_row is None:
    raise ValueError("This password reset link is invalid or has expired.")

  user = _get_user_by_email(email)
  if user is None:
    raise ValueError("No user account matches this reset request.")

  anvil.users.force_login(user, remember=False)
  return {"ok": True, "email": email}


def consume_password_reset_token(email, token):
  reset_row = _get_valid_reset_row(email, token)
  if reset_row is None:
    raise ValueError("This password reset link is invalid or has expired.")
  reset_row["used_at"] = _utcnow()
  return {"ok": True}
