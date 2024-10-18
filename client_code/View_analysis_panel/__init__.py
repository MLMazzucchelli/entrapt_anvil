from ._anvil_designer import View_analysis_panelTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..View_HIsystem_properties import View_HIsystem_properties


class View_analysis_panel(View_analysis_panelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.HIsystem_properties_button_click()
    
  def HIsystem_properties_button_click(self, **event_args):
    self.content_panel_view_analysis.clear()
    self.content_panel_view_analysis.add_component(View_HIsystem_properties(), index=0)

