from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import EntraPT
from ...View_analysis_panel import View_analysis_panel

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def view_selected_analysis_button_click(self, **event_args):
    EntraPT.current_analysis_ID     = self.item['ID']
    EntraPT.current_analysis_label  = self.item['full_label']
    modal = View_analysis_panel()
    alert(modal, large=True, title = "Analysis: " + EntraPT.current_analysis_label , buttons = [], dismissible = True)

