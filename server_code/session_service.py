import os
import uuid

import anvil.server
import anvil.users

from EntraPTcRuntime import manager as runtime_manager
from entraptc_daemon_client import request as daemon_request


SESSION_KEY = "entraptc_session_id"


def _call_if_registered(function_name, *args):
  try:
    return anvil.server.call(function_name, *args)
  except Exception as e:
    if "No server function matching" in str(e):
      return None
    raise


def ensure_user():
  user = anvil.users.get_user()
  if user is None:
    raise anvil.users.AuthenticationFailed("No logged in user")
  if user["groups"] is None:
    user["groups"] = "default"
  return user


def _get_session_id():
  return anvil.server.session.get(SESSION_KEY)


def _resolve_tutorial_project_path():
  explicit = os.environ.get("ENTRAPTC_TUTORIAL_PROJECT")
  candidates = [
    explicit,
    os.path.join(os.getcwd(), "datasets", "Test_project.json"),
    os.path.join(os.getcwd(), "entrapt_anvil", "datasets", "Test_project.json"),
  ]
  checked = []
  for path in candidates:
    if not path:
      continue
    abs_path = os.path.abspath(path)
    checked.append(abs_path)
    if os.path.isfile(abs_path):
      return abs_path
  raise FileNotFoundError("Tutorial project not found. Checked: " + "; ".join(checked))


def create_or_get_session(force_new=False):
  ensure_user()
  daemon_request("cleanup_idle")

  current = _get_session_id()
  if current and not force_new:
    daemon_request("touch_session", session_id=current)
    return current, False
  if current and force_new:
    close_current_session()

  session_id = str(uuid.uuid4())
  runtime_manager.create(session_id)
  daemon_request("create_session", session_id=session_id)
  _call_if_registered("initialize_EntraPTc_session", session_id)
  anvil.server.session[SESSION_KEY] = session_id
  return session_id, True


def get_current_session_id():
  daemon_request("cleanup_idle")
  session_id = _get_session_id()
  if not session_id:
    return -1
  daemon_request("touch_session", session_id=session_id)
  return session_id


def close_current_session():
  session_id = _get_session_id()
  if not session_id:
    return False
  try:
    _call_if_registered("delete_EntraPTc_sessions", [session_id])
  finally:
    try:
      daemon_request("close_session", session_id=session_id)
    except Exception:
      pass
    runtime_manager.close(session_id)
    anvil.server.session.pop(SESSION_KEY, None)
  return True


def remove_current_session_records():
  close_current_session()


def remove_orphan_sessions():
  # Legacy API retained. We no longer track remote table sessions here.
  sid = _get_session_id()
  if not sid:
    return {"closed_local_orphans": 0, "deleted_remote_orphans": 0}
  return {"closed_local_orphans": 0, "deleted_remote_orphans": 0}


def run_entraptc(args, timeout=120, serialize_globally=True):
  session_id = get_current_session_id()
  if session_id == -1:
    raise Exception("No active EntraPTc session")
  return runtime_manager.run(
    session_id,
    args,
    timeout=timeout,
    serialize_globally=serialize_globally,
  )


def dispatch_entraptc_command(command, command_arguments=()):
  session_id = get_current_session_id()
  if session_id == -1:
    raise Exception("No active EntraPTc session")

  args = tuple(command_arguments or ())
  if command == "run_entraptc":
    return runtime_manager.run(session_id, list(args))

  if command == "overwrite_project_in_EntraPTc":
    if len(args) < 2:
      raise Exception("overwrite_project_in_EntraPTc requires (filename, file)")
    filename, media_obj = args[0], args[1]
    run_dir = runtime_manager.get_run_dir(session_id)
    project_path = os.path.join(run_dir, str(filename))
    with open(project_path, "wb") as fp:
      fp.write(media_obj.get_bytes())
    return daemon_request(
      "dispatch",
      session_id=session_id,
      command=command,
      args=[str(filename), project_path],
    )

  return daemon_request(
    "dispatch",
    session_id=session_id,
    command=command,
    args=list(args),
  )


def get_list_analyses_for_tree(session_id):
  return daemon_request(
    "dispatch",
    session_id=session_id,
    command="get_list_analyses_for_tree",
    args=[],
  )


def get_list_analyses_for_view_data(session_id):
  return daemon_request(
    "dispatch",
    session_id=session_id,
    command="get_list_analyses_for_view_data",
    args=[],
  )


def load_tutorial_project():
  session_id = get_current_session_id()
  if session_id == -1:
    raise Exception("No active EntraPTc session")

  tutorial_path = _resolve_tutorial_project_path()
  return daemon_request(
    "dispatch",
    session_id=session_id,
    command="load_project_from_file",
    args=[tutorial_path],
  )


def get_HIsystem_properties(session_id, analysis_id):
  return daemon_request(
    "dispatch",
    session_id=session_id,
    command="get_HIsystem_properties",
    args=[analysis_id],
  )


def touch_current_session():
  session_id = _get_session_id()
  if not session_id:
    return {"active": False, "session_id": None}
  daemon_request("touch_session", session_id=session_id)
  return {"active": True, "session_id": session_id}


def cleanup_idle_sessions_now():
  return daemon_request("cleanup_idle")
