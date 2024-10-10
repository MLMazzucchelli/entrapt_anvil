from ._anvil_designer import Form1Template
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

global entrapt_session_ID

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        anvil.users.login_with_form()
        anvil.server.call('ensure_user')
        entrapt_session_ID = anvil.server.call('initialize_session')
        self.tree_data = anvil.server.call('get_list_analyses_for_tree', entrapt_session_ID)
        self.tree_show()
        


    def tree_show(self, **event_args):
        # Get the DOM node for the Anvil spacer component where you want to initialize the Fancytree
        tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)

        # Initialize the Fancytree on the DOM node using jQuery
        jQuery(tree_dom_node).fancytree({
            "checkbox": True,
            "selectMode": 3,
            "source": self.tree_data,
            "activate": lambda event, data: self.update_status_label(data.node)
        })
        
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
        # Get the Fancytree instance
        tree_dom_node = anvil.js.get_dom_node(self.tree_spacer)
        tree = jQuery(tree_dom_node).fancytree("getTree")
        
        # Get all selected nodes
        selected_nodes = tree.getSelectedNodes()
        
        # Print the titles of selected nodes
        selected_titles = [node.title for node in selected_nodes]
        alert(selected_titles)
