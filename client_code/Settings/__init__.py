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
from ..Project import Project


class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    def log_out_click(self, **event_args):
     anvil.users.logout()
     open_form(Logout())

  def project_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_panel_settings.clear()
    self.content_panel_settings.add_component(Project(), index=0)

  def log_out_click(self, **event_args):
    self.content_panel_settings.clear()
    self.content_panel_settings.add_component(Project(), index=0)



