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

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
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

  session_ID = set_session_ID(forceNewSession=forceNewSession)
  # except:
  #   raise Exception("Exceeded the maximum number of sessions for the current user")      
  # else:  
  #   #Initialize a session. If an eosfit session already exist for this browser session, use it.
  #   #If multiple Eosfit sessions are active, get the first eosfit session associated to the current browser session.
  #   #console_text = anvil.server.call('initialize_session',session_ID, selected_version)
  #   a=2


@anvil.server.callable
def set_session_ID(forceNewSession=False):
  print(anvil.users.get_user())
  #if forceNewSession=False, a new session will be create even if one is already active in the browser  
  browser_session_ID = anvil.server.get_session_id() #Get the id of the current browser session for Anvil
  #Get only the eosfit sessions that are associated to the current browser session
  sessions_in_browser = get_active_sessions_in_current_browser_session(browser_session_ID)
  #Get all the eosfit session of the user
  all_sessions = get_all_active_sessions()
  if len(sessions_in_browser) and not forceNewSession:
    #There is already at least one active entrapt session for the current browser window.
    #Get the first entrapt session associated to the current browser session.
    session_ID = sessions_in_browser[0]['eosfit_session_ID']
  elif  len(all_sessions)>=5:
    #The user has exceeded the number of available sessions.
    raise Exception("Exceeded the maximum number of sessions for the current user")  
  else: #generate a new session
    session_ID = register_session_in_database(browser_session_ID)
    
  


def register_session_in_database(browser_session_ID):
    session_ID = str(uuid.uuid1())
    app_tables.sessions.add_row(user_email=anvil.users.get_user()['email'],
                                anvil_session_ID=browser_session_ID,
                                entrapt_session_ID=session_ID,
                                started= datetime.datetime.now(),
                                last_action= datetime.datetime.now(),
                                status = "active")

    return session_ID


def get_active_sessions_in_current_browser_session(browser_session):
  #Get the entrapt sessions of the current user in the current browser
  rows = app_tables.sessions.search(q.all_of(
                                  user_email=anvil.users.get_user()['email'],
                                  anvil_session_ID=browser_session,
                                  status = "active"))
  return rows


def get_all_active_sessions():
  #Get all the active eosfit sessions of the current user
  rows = app_tables.sessions.search(q.all_of(
                                  user_email=anvil.users.get_user()['email'],
                                  status = "active"))
  return rows
