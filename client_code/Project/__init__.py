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
  UNSORTABLE_KEYS = {"residual_strain", "residual_stress"}
  UNSORTABLE_TITLES = {"residual strain", "residual stress"}

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self._all_columns = list(self.data_grid_analyses.columns)
    self._ensure_column_widths()
    self._rows = []
    self._sort_key = None
    self._sort_desc = False
    self._column_title_by_key = {}
    self._available_column_keys = []
    self._visible_column_keys = []
    self._setup_sort_controls()
    self._setup_column_controls()
    
    #self.apply_visible_columns(['full_label', 'host_name'])#Choose columns to display

    # Any code you write here will run before the form opens.
    self.update_project_data_grid()

  def _ensure_column_widths(self):
    width_by_key = {
      "column_1": 124,
      "full_label": 260,
      "host_name": 220,
      "inclusion_name": 220,
      "residual_strain": 200,
      "Pinc_eos": 150,
      "Pinc_stress": 150,
      "residual_stress": 200,
    }
    updated = []
    for col in self._all_columns:
      c = dict(col)
      key = str(c.get("data_key", ""))
      c["expand"] = False
      c["width"] = width_by_key.get(key, c.get("width") or 200)
      updated.append(c)
    self._all_columns = updated
    self.data_grid_analyses.columns = list(self._all_columns)

  def apply_visible_columns(self, column_keys=None):
    if not column_keys:
      self._visible_column_keys = list(self._available_column_keys)
    else:
      asked = [str(k) for k in column_keys]
      self._visible_column_keys = [k for k in self._available_column_keys if k in asked]
      if not self._visible_column_keys:
        self._visible_column_keys = list(self._available_column_keys)

    allowed = set(self._visible_column_keys)
    allowed.add("column_1")  # Always keep the action button column.
    filtered = [col for col in self._all_columns if str(col.get("data_key", "")) in allowed]
    self.data_grid_analyses.columns = filtered
    self._refresh_visible_column_dropdown_items()

  def _setup_sort_controls(self):
    sortable = []
    for col in self._all_columns:
      key = str(col.get("data_key", "")).strip()
      title = str(col.get("title", key)).strip()
      if self._is_unsortable_column(key, title):
        continue
      sortable.append((title, key))

    self.drop_down_sort_column.items = sortable
    if sortable:
      self.drop_down_sort_column.selected_value = sortable[0][1]
      self._sort_key = sortable[0][1]
    self.check_box_sort_desc.checked = False
    self._sort_desc = False

  def _setup_column_controls(self):
    self._available_column_keys = []
    self._column_title_by_key = {}
    for col in self._all_columns:
      key = str(col.get("data_key", "")).strip()
      if key == "column_1":
        continue
      title = str(col.get("title", key)).strip()
      self._available_column_keys.append(key)
      self._column_title_by_key[key] = title

    self._visible_column_keys = list(self._available_column_keys)
    self._refresh_visible_column_dropdown_items()
    self.drop_down_visible_column.selected_value = "__noop__"

  def drop_down_visible_column_change(self, **event_args):
    selected = str(self.drop_down_visible_column.selected_value or "").strip()
    if not selected or selected == "__noop__":
      return
    if selected == "__all__":
      self.apply_visible_columns(None)
      self.drop_down_visible_column.selected_value = "__noop__"
      return

    visible = set(self._visible_column_keys)
    if selected in visible:
      if len(visible) > 1:
        visible.remove(selected)
    else:
      visible.add(selected)

    ordered = [k for k in self._available_column_keys if k in visible]
    self.apply_visible_columns(ordered)
    self.drop_down_visible_column.selected_value = "__noop__"

  def _refresh_visible_column_dropdown_items(self):
    visible = set(self._visible_column_keys)
    items = [("Select column...", "__noop__"), ("All columns", "__all__")]
    for key in self._available_column_keys:
      title = self._column_title_by_key.get(key, key)
      prefix = "[x] " if key in visible else "[ ] "
      items.append((prefix + title, key))
    self.drop_down_visible_column.items = items


  def update_project_data_grid(self):
    results = EntraPT.send_command_to_entraptc('get_list_analyses_for_view_data')
    if results == -1:
       return
    self._rows = [self._format_analysis_row(row) for row in results]
    self._apply_sort()

  def _apply_sort(self):
    items = list(self._rows)
    if self._sort_key and self._sort_key not in self.UNSORTABLE_KEYS:
      items = sorted(items, key=lambda row: self._sort_value(row, self._sort_key), reverse=self._sort_desc)
    self.repeating_panel_1.items = items

  def _sort_value(self, row, key):
    value = row.get(key, "") if isinstance(row, dict) else getattr(row, key, "")
    if value is None:
      return (2, "")
    text = str(value).strip()
    if text == "":
      return (2, "")
    numeric_text = text.split("(", 1)[0].strip()
    try:
      return (0, float(numeric_text))
    except Exception:
      return (1, text.lower())

  def data_grid_analyses_header_click(self, **event_args):
    # Kept for compatibility if header_click exists in some runtimes.
    pass

  def drop_down_sort_column_change(self, **event_args):
    selected = str(self.drop_down_sort_column.selected_value or "").strip()
    if selected in self.UNSORTABLE_KEYS:
      return
    self._sort_key = selected
    self._apply_sort()

  def check_box_sort_desc_change(self, **event_args):
    self._sort_desc = bool(self.check_box_sort_desc.checked)
    self._apply_sort()

  def _is_unsortable_column(self, key, title):
    key_n = str(key or "").strip().lower()
    title_n = str(title or "").strip().lower()
    return key_n == "column_1" or key_n in self.UNSORTABLE_KEYS or title_n in self.UNSORTABLE_TITLES

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


        
