from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.js
import anvil.server
import anvil.users


class Login(LoginTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self._signup_mode = False
    self._set_mode(False)

  def _set_mode(self, signup_mode):
    self._signup_mode = bool(signup_mode)
    self.label_title.text = "Create account" if self._signup_mode else "Sign in"
    self.primary_action.text = "Create account" if self._signup_mode else "Sign in"
    self.password_confirm.visible = self._signup_mode
    self.label_password_confirm.visible = self._signup_mode
    self.link_toggle_mode.text = "Already have an account? Sign in" if self._signup_mode else "Need an account? Sign up"
    self.link_forgot_password.visible = not self._signup_mode
    self._clear_password_boxes()

  def _clear_password_boxes(self):
    self.password.text = ""
    self.password_confirm.text = ""

  def primary_action_click(self, **event_args):
    email = (self.email.text or "").strip()
    password = self.password.text or ""
    remember = bool(self.check_box_remember.checked)

    if not email:
      alert("Enter your email address.")
      return
    if not password:
      alert("Enter your password.")
      return

    try:
      if self._signup_mode:
        confirm_password = self.password_confirm.text or ""
        if password != confirm_password:
          alert("The passwords do not match.")
          return
        anvil.users.signup_with_email(email, password, remember=remember)
      else:
        anvil.users.login_with_email(email, password, remember=remember)
    except anvil.users.UserExists:
      alert("An account with this email address already exists.")
      return
    except anvil.users.AuthenticationFailed:
      alert("The email address or password is incorrect.")
      return
    except Exception as exc:
      alert(str(exc))
      return

    open_form("Initial_page", authenticated=True)

  def link_toggle_mode_click(self, **event_args):
    self._set_mode(not self._signup_mode)

  def link_forgot_password_click(self, **event_args):
    email = (self.email.text or "").strip()
    if not email:
      alert("Enter your email address first, then request a password reset.")
      return

    try:
      location = anvil.js.window.location
      reset_base_url = f"{location.origin}{location.pathname}"
      anvil.server.call_s("request_password_reset", email, reset_base_url)
    except Exception as exc:
      alert(str(exc))
      return

    alert("If this email address is registered, a password reset email has been sent.")

  def button_test_smtp_click(self, **event_args):
    email = (self.email.text or "").strip()
    if not email:
      alert("Enter an email address first.")
      return

    try:
      result = anvil.server.call_s("test_password_reset_smtp", email)
    except Exception as exc:
      alert(f"SMTP test failed:\n{exc}")
      return

    alert(f"SMTP test succeeded for {result.get('recipient', email)}.")
