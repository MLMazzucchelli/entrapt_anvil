import anvil.server
import anvil.users
from anvil import alert, open_form

from . import Loading
from .Logout import Logout


current_analysis_ID = None
current_analysis_label = None



def start_session(force_new=False):
  return anvil.server.call_s("session_start", force_new)


def session_is_active():
  status = anvil.server.call_s("session_status")
  return bool(status.get("active"))


def close_session():
  return anvil.server.call_s("session_close")


def logout_and_close_session():
  with Loading.Loading("Please wait while we terminate your session..."):
    try:
      close_session()
    except anvil.server.SessionExpiredError:
      alert("Session is expired")
    anvil.users.logout()
    open_form(Logout())


def send_command_to_entraptc(command, command_arguments=(), loading_bar_msg=""):
  if not session_is_active():
    answer = alert(
      "Connection with EntraPTc server is not active.\nDo you want to start a new EntraPTc session?",
      buttons=[("Yes", "YES"), ("No", "NO")],
      dismissible=False,
    )
    if answer == "YES":
      start_session(force_new=False)
    else:
      alert("This command cannot be executed without an active EntraPTc session.")
      return -1

  if loading_bar_msg:
    with Loading.Loading("Please wait, %s..." % loading_bar_msg):
      return anvil.server.call_s("entraptc_call", command, command_arguments)
  return anvil.server.call_s("entraptc_call", command, command_arguments)


def run_entraptc(args, loading_bar_msg="", timeout=120, serialize_globally=True):
  if loading_bar_msg:
    with Loading.Loading("Please wait, %s..." % loading_bar_msg):
      return anvil.server.call_s("entraptc_run", tuple(args), timeout, serialize_globally)
  return anvil.server.call_s("entraptc_run", tuple(args), timeout, serialize_globally)

