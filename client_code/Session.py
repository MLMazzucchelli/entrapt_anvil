import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

try:
  anvil.server.call("foo")
except anvil.server.SessionExpiredError:
  anvil.server.reset_session()
  # This will work now, but with a blank session
  anvil.server.call("foo")