from ._anvil_designer import ProjectTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import EntraPT
from .. import Error_handling

# This code displays an Anvil alert, rather than
# the default red box, when an error occurs.



class Project(ProjectTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.update_project_data_grid()


  def update_project_data_grid(self):
    results = EntraPT.send_command_to_EntraPTc_server('get_list_analyses_for_view_data')
    if results == -1:
      return
    self.repeating_panel_1.items = results

    
