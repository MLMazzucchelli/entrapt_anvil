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
from .. import EntraPT, Error_handling, Loading
from ..Logout import Logout
from ..Settings import Settings
from ..Calculate_entrapment import Calculate_entrapment
from ..Project import Project
from ..Session_timeout import Session_timeout
from ..Home import Home




class Initial_page(Initial_pageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        authenticated = bool(properties.get("authenticated"))

        reset_request = self._get_reset_request()
        if reset_request is not None:
          open_form("Reset_password", **reset_request)
          return

        # Any code you write here will run before the form opens.
        if not authenticated:
          open_form("Login")
          return
        anvil.server.call_s('ensure_user')
        try:
          EntraPT.start_session(force_new=False)
        except Exception:
          # Keep login usable even if the EntraPTc backend is not ready yet.
          pass
        self.content_panel.clear()
        self.content_panel.add_component(Home(), index=0)
      
        #self.sidebar_menu.set_event_handler("clicked", self.restrcted_menu_bar_access(""))
        
        

    def sidebar_menu_clicked(self, file, **event_args):
      clicked_item = self.sidebar_menu.selected_item

      if clicked_item == "home":
        self.content_panel.clear()
        self.content_panel.add_component(Home(), index=0)
      
      if clicked_item == "view_analyses":
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)

      elif clicked_item == "new_project":
        result = EntraPT.send_command_to_entraptc("clear_project_in_EntraPTc")
        if result == -1:
          return
        # self.content_panel.clear()
        # self.content_panel.add_component(Project(), index=0)

      elif clicked_item == "upload_project":
        func_arg = (file.name, file)
        result = EntraPT.send_command_to_entraptc("overwrite_project_in_EntraPTc", func_arg, "while we import your project")
        if result == -1:
          return
        # self.content_panel.clear()
        # self.content_panel.add_component(Project(), index=0)
        
      elif clicked_item == "entrapment":
        self.content_panel.clear()
        self.content_panel.add_component(Calculate_entrapment(), index=0)
        
      elif clicked_item == "settings":
        modal = Settings()
        alert(modal, large=True, title = "SETTINGS", buttons = [], dismissible = True)

    def timer_to_close_EntraPTc_session_tick(self, **event_args):
      try:
        anvil.server.call_s("session_touch")
      except Exception:
        pass
      modal = Session_timeout()
      results = alert(modal, large=True, buttons = [("Yes", "YES"),("No", "NO"),], dismissible = False)
      if results == ("YES"):
        pass
      elif results == ("NO"):
        EntraPT.logout_and_close_session()
        self.raise_event("x-close-alert", value=42)    


    def restrcted_menu_bar_access(self, clicked_item, **event_args):
      if clicked_item == "settings":
        modal = Settings()
        alert(modal, large=True, title = "SETTINGS", buttons = [], dismissible = True)

    def _get_reset_request(self):
      try:
        search = str(anvil.js.window.location.search or "")
      except Exception:
        return None

      if search.startswith("?"):
        search = search[1:]

      params = {}
      for item in search.split("&"):
        if not item or "=" not in item:
          continue
        key, value = item.split("=", 1)
        try:
          key = str(anvil.js.window.decodeURIComponent(key.replace("+", " ")))
          value = str(anvil.js.window.decodeURIComponent(value.replace("+", " ")))
        except Exception:
          continue
        params[key] = value

      email = params.get("reset_email", "")
      token = params.get("reset_token", "")
      if not email or not token:
        return None
      return {"email": email, "token": token}
        


        
 



 




      
