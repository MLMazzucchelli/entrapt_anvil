import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import os
import datetime

@anvil.server.callable
def put_project_in_table(file):
  #Add user files to database
  _, extension = os.path.splitext(file.name)
  if extension in ['.ept']:
    app_tables.files.add_row(filename=file.name, author=anvil.users.get_user(),  file=file, type=extension, created=datetime.datetime.now())
    return file.name
  else:
    raise Exception("Cannot upload files this extension")  


@anvil.server.callable
def get_tutorial_project():
  search = app_tables.files.search(q.all_of(filename="tutorial_project"))
  row = search[0]
  file = row["file"]
  return file
  

def get_file(filename):
  search = app_tables.files.search(q.all_of(author=anvil.users.get_user(),filename=filename))
  row = search[0]
  print(row['filename'])
  file = row["file"]
  return row["filename"], file
    