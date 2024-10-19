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

# This code displays an Anvil alert, rather than
# the default red box, when an error occurs.

def error_handler(err):
  alert(str(err), title="An error has occurred")

set_default_error_handling(error_handler)

class Project(ProjectTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.update_project_data_grid()


  def update_project_data_grid(self):
      self.repeating_panel_1.items = anvil.server.call('get_list_analyses_for_view_data', EntraPT.session_ID)


 
    
