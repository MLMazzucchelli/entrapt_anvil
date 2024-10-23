import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
from .Logout import Logout
from . import Loading
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

global session_ID
global current_analysis_ID
global current_analysis_label
session_ID = None

def close_current_EntraPTc_session():
  with Loading.Loading("Please wait while we terminate your session..."):
    try:
      anvil.server.call_s("close_current_EntraPTc_session")
      anvil.server.call_s("remove_orphan_sessions") #WARNING: In future this must be moved to a scheduled Task on server side
    except anvil.server.SessionExpiredError:
      alert("Session is expired")
    anvil.users.logout()
    open_form(Logout())
    return


def check_EntraPTc_session_is_active(session_ID):
  if not session_ID:
    alert("Connection with EntraPTc Server is not active")
    return


def send_command_to_EntraPTc_server(command, command_arguments=(), loading_bar_msg = ""):
  global session_ID
  if not session_ID:
      answer = alert("Connection with EntraPTc Server is not active.\nDo you want to start a new EntraPTc session?", buttons = [("Yes", "YES"),("No", "NO"),], dismissible = False)
      if answer == ("YES"):
        session_ID = anvil.server.call('initialize_session')
      else:
        alert("Unfortunately this command cannot de executed without an active EntraPTc session.")
        return -1

  if loading_bar_msg != "":
     with Loading.Loading('Please wait, %s...' %loading_bar_msg):
         return anvil.server.call_s(command, session_ID, *command_arguments)
  else:
    return anvil.server.call_s(command, session_ID, *command_arguments)
    
  
  
  