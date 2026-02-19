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
    self._all_columns = list(self.data_grid_analyses.columns)
    
    #self.apply_visible_columns(['full_label', 'host_name'])#Choose columns to display

    # Any code you write here will run before the form opens.
    self.update_project_data_grid()

  def apply_visible_columns(self, column_keys=None):
    if not column_keys:
      self.data_grid_analyses.columns = list(self._all_columns)
      return

    allowed = set([str(k) for k in column_keys])
    allowed.add("column_1")  # Always keep the action button column.
    filtered = [col for col in self._all_columns if str(col.get("data_key")) in allowed]
    self.data_grid_analyses.columns = filtered


  def update_project_data_grid(self):
    results = EntraPT.send_command_to_entraptc('get_list_analyses_for_view_data')
    if results == -1:
       return
    self.repeating_panel_1.items = [self._format_analysis_row(row) for row in results]

  def _format_analysis_row(self, row):
    if isinstance(row, dict):
      item = dict(row)
    else:
      item = row

    try:
      self._set_combined_value(item, "Pinc_eos", "Pinc_eos_esd")
      self._set_combined_value(item, "Pinc_stress", "Pinc_stress_esd")
    except Exception:
      pass
    return item

  def _to_3dp(self, value):
    try:
      return f"{float(value):.3f}"
    except Exception:
      return str(value)

  def _set_combined_value(self, item, value_key, esd_key):
    if isinstance(item, dict):
      value = item.get(value_key, "")
      esd = item.get(esd_key, "")
    else:
      value = getattr(item, value_key, "")
      esd = getattr(item, esd_key, "")

    if value in (None, ""):
      formatted = ""
    elif esd in (None, ""):
      formatted = self._to_3dp(value)
    else:
      formatted = f"{self._to_3dp(value)}({self._to_3dp(esd)})"

    if isinstance(item, dict):
      item[value_key] = formatted
    else:
      setattr(item, value_key, formatted)


        
