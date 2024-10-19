from ._anvil_designer import Initial_pageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import anvil.js
from .. import EntraPT
from ..Logout import Logout
from ..Settings import Settings
from ..Calculate_entrapment import Calculate_entrapment
from ..Project import Project
from .. import Error_handling



class Initial_page(Initial_pageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        anvil.users.login_with_form()
        anvil.server.call('ensure_user')
        EntraPT.session_ID = anvil.server.call('initialize_session')   
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)
        

    def sidebar_menu_1_clicked(self, clicked_item, file, **event_args):
      
      if clicked_item == "view_analyses":
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)

      elif clicked_item == "new_project":
        anvil.server.call('clear_project_in_EntraPTc', EntraPT.session_ID) 
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)

      elif clicked_item == "upload_project":
        anvil.server.call("overwrite_project_in_EntraPTc",EntraPT.session_ID, file.name, file)
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)
        
      elif clicked_item == "entrapment":
        self.content_panel.clear()
        self.content_panel.add_component(Calculate_entrapment(), index=0)
        
      elif clicked_item == "settings":
        modal = Settings()
        alert(modal, large=True, title = "SETTINGS", buttons = [], dismissible = True)


        
 



 




      