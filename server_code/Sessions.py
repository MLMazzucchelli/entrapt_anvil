import anvil.server
import os
import sys

import session_service


@anvil.server.callable
def ensure_user():
  return session_service.ensure_user()


@anvil.server.callable
def session_start(force_new=False):
  session_id, _created = session_service.create_or_get_session(force_new=force_new)
  return session_id


@anvil.server.callable
def session_status():
  session_id = session_service.get_current_session_id()
  return {
    "active": session_id != -1,
    "session_id": None if session_id == -1 else session_id,
  }


@anvil.server.callable
def session_close():
  return session_service.close_current_session()


@anvil.server.callable
def entraptc_call(command, command_arguments=()):
  return session_service.dispatch_entraptc_command(command, command_arguments)


@anvil.server.callable
def entraptc_run(args, timeout=120, serialize_globally=True):
  return session_service.run_entraptc(
    args=args,
    timeout=timeout,
    serialize_globally=serialize_globally,
  )


@anvil.server.callable
def get_list_analyses_for_tree(session_id):
  return session_service.get_list_analyses_for_tree(session_id)


@anvil.server.callable
def get_list_analyses_for_view_data(session_id):
  return session_service.get_list_analyses_for_view_data(session_id)


@anvil.server.callable
def load_tutorial_project():
  return session_service.load_tutorial_project()


@anvil.server.callable
def get_HIsystem_properties(session_id, analysis_id):
  return session_service.get_HIsystem_properties(session_id, analysis_id)


@anvil.server.callable
def debug_entraptc_environment():
  info = {
    "python_executable": sys.executable,
    "cwd": os.getcwd(),
    "MITEOSP_SRC": os.environ.get("MITEOSP_SRC"),
    "MITEOSP_HOME": os.environ.get("MITEOSP_HOME"),
    "sys_path_head": sys.path[:10],
  }
  try:
    try:
      from miteos.entraptc.entraptc import EntraPTc
    except Exception:
      from miteos.entraptc import EntraPTc
    info["import_ok"] = True
    info["entraptc_class"] = str(EntraPTc)
  except Exception as exc:
    info["import_ok"] = False
    info["import_error"] = str(exc)
  return info
