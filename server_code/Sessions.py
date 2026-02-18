import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
#import plotly.graph_objects as go
from anvil.tables import app_tables
import anvil.server
#import anvil.plotly_templates
import subprocess
import time
import uuid 
import pandas as pd
import threading
import os
import datetime

@anvil.server.callable
def ensure_user():
  user = anvil.users.get_user()
  if user is None:
    raise anvil.users.AuthenticationFailed('No logged in user')
  if user["groups"] is None: #ensure that the user is at least in the default group
    user["groups"] = "default"
  return user 
