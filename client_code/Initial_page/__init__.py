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
from anvil.js.window import jQuery
from .. import EntraPT
from ..Logout import Logout
from ..Settings import Settings
from ..Calculate_entrapment import Calculate_entrapment
from ..Project import Project


class Initial_page(Initial_pageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        anvil.users.login_with_form()
        anvil.server.call('ensure_user')
        EntraPT.session_ID = anvil.server.call('initialize_session')   
        self.project_tab_button_click()
        #self.tree_show()
        


    def tree_show(self, **event_args):
        # Get the data
        self.tree_data = anvil.server.call('get_list_analyses_for_tree', EntraPT.session_ID)
        # Get the DOM node for the Anvil spacer component where you want to initialize the Fancytree
        tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)   
        # Set the width of the tree DOM node using jQuery
        jQuery(tree_dom_node).css({
            "width": "300px",  # Fixed width
            "overflow": "auto"  # Add scroll if content overflows
        })

        # Initialize the Fancytree on the DOM node using jQuery
        jQuery(tree_dom_node).fancytree({
            "checkbox": True,
            "selectMode": 3,
            "source": self.tree_data,
            "activate": lambda event, data: self.update_status_label(data.node)
        })


    def tree_refresh(self):
        # Refresh the tree with new data in project
        self.tree_data = anvil.server.call('get_list_analyses_for_tree', EntraPT.session_ID)
        tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)
        tree = jQuery(tree_dom_node).fancytree("getTree")
        tree.reload(self.tree_data)

        
    def update_status_label(self, node):
        # Update the status label with the activated node
        self.status_label.text = f"Activate: {node.title}"
        self.tree_spacer.height = 300

    def get_analyses_IDs_from_tree(self):
      tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)
      tree = jQuery(tree_dom_node).fancytree("getTree")
      # Get all selected nodes
      selected_nodes = tree.getSelectedNodes()
      # Print the key of selected analyses
      selected_keys = [node.key for node in selected_nodes]
      alert(selected_keys)
      return selected_keys

    def calculate_entrapment_tab_button_click(self, **event_args):
      """This method is called when the button is clicked"""
      self.content_panel.clear()
      self.content_panel.add_component(Calculate_entrapment(), index=0)


    def settings_button_click(self, **event_args):
      modal = Settings()
      alert(modal, large=True, title = "SETTINGS", buttons = [], dismissible = True)

    def project_tab_button_click(self, **event_args):
      self.content_panel.clear()
      self.content_panel.add_component(Project(), index=0)

    def sidebar_menu_clicked(self, clicked_item, **event_args):
      #if clicked_item == "ciao"
        pass

    def sidebar_menu_1_clicked(self, clicked_item, **event_args):
      if clicked_item == "view_analyses":
        self.content_panel.clear()
        self.content_panel.add_component(Project(), index=0)

      elif clicked_item == "new_project":
        anvil.server.call('clear_project_in_EntraPTc', EntraPT.session_ID)  

      elif cliked_item == "upload_project":
        self.file_loader_change()
        
      elif clicked_item == "entrapment":
        self.content_panel.clear()
        self.content_panel.add_component(Calculate_entrapment(), index=0)
        
      elif clicked_item == "settings":
        modal = Settings()
        alert(modal, large=True, title = "SETTINGS", buttons = [], dismissible = True)

    def file_loader_change(self, file, **event_args):
      anvil.server.call("overwrite_project_in_EntraPTc",EntraPT.session_ID, file.name, file)
      self.file_loader.clear()
      get_open_form().tree_refresh()
      self.update_project_data_grid()


        
 



 




      