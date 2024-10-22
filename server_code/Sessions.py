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

@anvil.server.callable
def initialize_session(forceNewSession=False):
  # If the 
  global session_ID
  global console_text
  session_ID = set_session_ID()
  anvil.server.call('initialize_EntraPTc_session',session_ID)
  return session_ID


@anvil.server.callable
def set_session_ID():
  browser_session_ID = anvil.server.get_session_id() #Get the id of the current browser session of Anvil
  #Get the entrapt session of the user if it exists
  all_sessions = get_all_active_sessions()
  if len(all_sessions):
    #There is already at least one active entrapt session for the current browser window.
    session_ID = all_sessions[0]['entrapt_session_ID']
  else: #generate a new session
    session_ID = register_session_in_database(browser_session_ID)
  return session_ID
    
def register_session_in_database(browser_session_ID):
    #session_ID = str(uuid.uuid1())
    session_ID = anvil.users.get_user()['email']
    app_tables.sessions.add_row(user_email=anvil.users.get_user()['email'],
                                anvil_session_ID=browser_session_ID,
                                entrapt_session_ID=session_ID,
                                started= datetime.datetime.now(),
                                last_action= datetime.datetime.now(),
                                status = "active")

    return session_ID



def get_all_active_sessions():
  #Get all the active eosfit sessions of the current user
  rows = app_tables.sessions.search(q.all_of(
                                  user_email=anvil.users.get_user()['email'],
                                  status = "active"))
  return rows



def is_session_active():
  pass


def delete_session():
  pass