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


class Project(ProjectTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def file_loader_change(self, file, **event_args):
      """This method is called when a new file is loaded into this FileLoader"""
      if self.file_loader.file.length > 1024*1024: #check the size before the file is uploaded
          raise Exception("The uploaded project file is too large") 
      else:
          filename = anvil.server.call("put_project_in_table",file)
          
      self.file_loader.clear()
      anvil.server.call("overwrite_project_in_EntraPTc",EntraPT.session_ID, filename, file)
      get_open_form().tree_refresh()

  def new_project_click(self, **event_args):
      """This method is called when the button is clicked"""
      anvil.server.call('clear_project_in_EntraPTc', EntraPT.session_ID)      
      get_open_form().tree_refresh()