import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
from .Logout import Logout
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


def close_current_EntraPTc_session():
    try:
      anvil.server.call_s("close_current_EntraPTc_session")
    except anvil.server.SessionExpiredError:
      alert("Session is expired")
    anvil.users.logout()
    open_form(Logout())
    return
