from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Logout import Logout
from .. import EntraPT, Loading
from ..Project import Project


class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def log_out_click(self, **event_args):
        EntraPT.logout_and_close_session()
        self.raise_event("x-close-alert", value=42)   

  def load_tutorial_project_button_click(self, **event_args):
      results = anvil.server.call_s("load_tutorial_project")
      if not results:
        self.raise_event("x-close-alert", value=42)
        return
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(Project(), index=0)
      self.raise_event("x-close-alert", value=42)
      
      
