from ._anvil_designer import Session_timeoutTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Logout import Logout
global ttot

class Session_timeout(Session_timeoutTemplate):
  def __init__(self, **properties):
    global ttot
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.timer_session_timeout_popup.interval = 1
    ttot = 120 #Total time for countdown. At zero seconds the sessions is closed
    self.timer_session_timeout_popup.set_event_handler("tick", self.timer_session_timeout_popup_tick)
    self.timer_session_timeout_popup_tick()

  def timer_session_timeout_popup_tick(self, **event_args):
    global ttot
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    ttot -= 1
    self.session_timeout_message.text = "The current session will be terminated in " + str(ttot) + " seconds"
    if ttot < 1:        
      ttot = 1
      anvil.server.call_s("close_current_EntraPTc_session")
      anvil.users.logout()
      open_form(Logout())
      self.raise_event("x-close-alert", value=42) 
      self.timer_session_timeout_popup.interval = 0
      return


