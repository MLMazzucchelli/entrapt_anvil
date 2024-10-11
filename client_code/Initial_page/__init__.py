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
from ..Project import Project
from ..Calculate_entrapment import Calculate_entrapment
class Initial_page(Initial_pageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        anvil.users.login_with_form()
        anvil.server.call('ensure_user')
        EntraPT.session_ID = anvil.server.call('initialize_session')        
        self.tree_show()
        


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

    def toggle_button_click(self, **event_args):
        # Get the Fancytree instance and toggle the selection for Node2
        tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)
        tree = jQuery(tree_dom_node).fancytree("getTree")
        node = tree.getNodeByKey("Node2")
        if node:
            node.toggleSelected()

    def get_selected_items_click(self, **event_args):  
        alert(self.get_analyses_IDs_from_tree())


    def get_analyses_IDs_from_tree(self):
      tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)
      tree = jQuery(tree_dom_node).fancytree("getTree")
      # Get all selected nodes
      selected_nodes = tree.getSelectedNodes()
      # Print the key of selected analyses
      selected_keys = [node.key for node in selected_nodes]
      return selected_keys

    def upload_project_click(self, **event_args):
      """This method is called when the button is clicked"""
      anvil.server.call('put_project_in_table')

    def file_loader_change(self, file, **event_args):
      """This method is called when a new file is loaded into this FileLoader"""
      if self.file_loader.file.length > 1024*1024: #check the size before the file is uploaded
          raise Exception("The uploaded project file is too large") 
      else:
          filename = anvil.server.call("put_project_in_table",file)
          
      self.file_loader.clear()
      anvil.server.call("overwrite_project_in_EntraPTc",EntraPT.session_ID, filename, file)
      self.tree_refresh()

    def button_1_click(self, **event_args):
      """This method is called when the button is clicked"""
      anvil.server.call('clear_project_in_EntraPTc', EntraPT.session_ID)      
      self.tree_refresh()

    def log_out_click(self, **event_args):
     anvil.users.logout()
     open_form(Logout())

    def Project_tab_button_click(self, **event_args):
      """This method is called when the button is clicked"""
      self.content_panel.clear()
      self.activate_project_page()

    def activate_project_page(self):
      self.content_panel.clear()
      self.content_panel.add_component(Project(), index=0)

    def calculate_entrapment_tab_button_click(self, **event_args):
      """This method is called when the button is clicked"""
      self.content_panel.clear()
      self.content_panel.add_component(Calculate_entrapment(), index=0)

      