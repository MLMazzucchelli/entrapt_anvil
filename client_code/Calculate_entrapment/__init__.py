from ._anvil_designer import Calculate_entrapmentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import EntraPT


class Calculate_entrapment(Calculate_entrapmentTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    IDs = get_open_form().get_analyses_IDs_from_tree()
    anvil.server.call("calculate_entrapment", EntraPT.session_ID, IDs, 300, 1200, 100)
