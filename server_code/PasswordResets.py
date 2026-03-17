import anvil.server
import traceback

import password_reset_service


def _run_with_traceback(label, fn, *args):
  try:
    return fn(*args)
  except Exception as exc:
    print(f"[password-reset] {label} failed: {exc}")
    traceback.print_exc()
    raise Exception(f"{label} failed: {exc}")


@anvil.server.callable
def request_password_reset(email, reset_base_url):
  return _run_with_traceback("request_password_reset", password_reset_service.request_password_reset, email, reset_base_url)


@anvil.server.callable
def login_user_for_password_reset(email, token):
  return _run_with_traceback("login_user_for_password_reset", password_reset_service.login_user_for_password_reset, email, token)


@anvil.server.callable
def consume_password_reset_token(email, token):
  return _run_with_traceback("consume_password_reset_token", password_reset_service.consume_password_reset_token, email, token)


@anvil.server.callable
def test_password_reset_smtp(recipient):
  return _run_with_traceback("test_password_reset_smtp", password_reset_service.test_password_reset_smtp, recipient)
