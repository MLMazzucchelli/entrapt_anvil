import uuid

import anvil.server
import anvil.users

from MITEoSpRuntime import manager as runtime_manager


SESSION_KEY = "entrapt_session_id"


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


def create_or_get_session(force_new=False):
  ensure_user()
  current = _get_session_id()
  if current and not force_new:
    return current, False
  if current and force_new:
    close_current_session()

  session_id = str(uuid.uuid4())
  runtime_manager.create(session_id)
  try:
    _call_if_registered("initialize_EntraPTc_session", session_id)
  except Exception:
    runtime_manager.close(session_id)
    raise
  anvil.server.session[SESSION_KEY] = session_id
  return session_id, True


def get_current_session_id():
  session_id = _get_session_id()
  if not session_id:
    return -1
  return session_id


def close_current_session():
  session_id = _get_session_id()
  if not session_id:
    return False
  try:
    _call_if_registered("delete_EntraPTc_sessions", [session_id])
  finally:
    runtime_manager.close(session_id)
    anvil.server.session.pop(SESSION_KEY, None)
  return True


def remove_current_session_records():
  close_current_session()


def remove_orphan_sessions():
  # Legacy API retained. Without a shared sessions table we only validate this browser session.
  sid = _get_session_id()
  if not sid:
    return {"closed_local_orphans": 0, "deleted_remote_orphans": 0}
  remote = _call_if_registered("get_names_of_all_active_sessions")
  if remote is None:
    return {"closed_local_orphans": 0, "deleted_remote_orphans": 0}
  remote_active = set(remote or [])
  if sid not in remote_active:
    runtime_manager.close(sid)
    anvil.server.session.pop(SESSION_KEY, None)
    return {"closed_local_orphans": 1, "deleted_remote_orphans": 0}
  return {
    "closed_local_orphans": 0,
    "deleted_remote_orphans": 0,
  }


def run_miteosp(args, timeout=120, serialize_globally=True):
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
  if command == "run_miteosp":
    return runtime_manager.run(session_id, list(args))

  return anvil.server.call(command, session_id, *args)
