from ._anvil_designer import Reset_passwordTemplate
from anvil import *
import anvil.js
import anvil.server
import anvil.users


class Reset_password(Reset_passwordTemplate):
  def __init__(self, email="", token="", **properties):
    self._email = (email or "").strip().lower()
    self._token = token or ""
    self.init_components(**properties)
    self._clear_reset_query()
    self._prepare_reset()

  def _clear_reset_query(self):
    try:
      location = anvil.js.window.location
      clean_url = f"{location.origin}{location.pathname}"
      anvil.js.window.history.replaceState({}, "", clean_url)
    except Exception:
      pass

  def _prepare_reset(self):
    if not self._email or not self._token:
      self.status_label.text = "This password reset link is incomplete."
      self.status_label.foreground = "theme:Error"
      self.reset_password_button.enabled = False
      return

    try:
      anvil.server.call_s("login_user_for_password_reset", self._email, self._token)
    except Exception as exc:
      self.status_label.text = str(exc)
      self.status_label.foreground = "theme:Error"
      self.reset_password_button.enabled = False
      return

    self.status_label.text = f"Reset link accepted for {self._email}."
    self.status_label.foreground = ""
    self.reset_password_button.enabled = True

  def reset_password_button_click(self, **event_args):
    if anvil.users.get_user() is None:
      alert("Your reset session is not active anymore. Request a new reset email.")
      open_form("Login")
      return

    try:
      anvil.users.change_password_with_form(require_old_password=False)
      anvil.server.call_s("consume_password_reset_token", self._email, self._token)
    except Exception as exc:
      alert(str(exc))
      return

    alert("Your password has been updated.")
    open_form("Initial_page", authenticated=True)

  def back_to_login_link_click(self, **event_args):
    anvil.users.logout()
    open_form("Login")
