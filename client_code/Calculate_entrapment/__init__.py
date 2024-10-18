from ._anvil_designer import Calculate_entrapmentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import jQuery
from .. import EntraPT


class Calculate_entrapment(Calculate_entrapmentTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
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

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    IDs = get_open_form().get_analyses_IDs_from_tree()
    anvil.server.call("calculate_entrapment", EntraPT.session_ID, IDs, 300, 1200, 100)
