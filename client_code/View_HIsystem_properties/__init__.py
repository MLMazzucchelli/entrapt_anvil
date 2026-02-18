from ._anvil_designer import View_HIsystem_propertiesTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import EntraPT


class View_HIsystem_properties(View_HIsystem_propertiesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.HIsystem_properties_text.text = EntraPT.send_command_to_EntraPTc_server(
      "get_HIsystem_properties",
      (EntraPT.current_analysis_ID,)
    )
