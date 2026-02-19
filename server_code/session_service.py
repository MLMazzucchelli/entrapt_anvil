import uuid
import os
import sys

import anvil.server
import anvil.users

from EntraPTcRuntime import manager as runtime_manager


SESSION_KEY = "entraptc_session_id"
_ENTRAPTC_BY_SESSION = {}


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


def _new_entraptc_instance():
  def _import_entraptc():
    # Prefer direct module import to avoid broken package __init__ aliases.
    try:
      from miteos.entraptc.entraptc import EntraPTc
      return EntraPTc
    except Exception:
      from miteos.entraptc import EntraPTc
      return EntraPTc

  try:
    EntraPTc = _import_entraptc()
  except Exception:
    # Development fallback: try common local source locations.
    raw_candidates = [
      os.environ.get("MITEOSP_SRC"),
      os.environ.get("MITEOSP_HOME"),
      os.path.abspath(os.path.join(os.getcwd(), "..", "MITEoSp")),
      os.path.abspath(os.path.join(os.getcwd(), "MITEoSp")),
      r"C:\Users\mmazzucc\Documents\GitHub\MITEoSp",
      r"C:\Users\mmazzucc\Documents\GitHub\MITEoSp\src",
    ]
    candidate_src_dirs = []
    for path in raw_candidates:
      if not path:
        continue
      candidate_src_dirs.append(path)
      candidate_src_dirs.append(os.path.join(path, "src"))

    for src_dir in candidate_src_dirs:
      if os.path.isdir(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    try:
      EntraPTc = _import_entraptc()
    except Exception as exc:
      path_hint = "; ".join([p for p in candidate_src_dirs if os.path.isdir(p)][:6])
      exc_msg = str(exc)
      if "entrAptc" in exc_msg and "No module named" in exc_msg:
        raise Exception(
          "Cannot import EntraPTc because MITEoSp has an internal import typo: "
          "`entrAptc` should be `entraptc` in MITEoSp __init__.py files. "
          "Fix MITEoSp imports, then restart app-server."
        ) from exc
      raise Exception(
        "Cannot import EntraPTc. Set MITEOSP_SRC (or MITEOSP_HOME) to your MITEoSp path and restart app-server. "
        f"Checked paths: {path_hint}. Python executable: {sys.executable}. Root error: {exc_msg}"
      ) from exc
  return EntraPTc()


def _get_entraptc(session_id):
  ept = _ENTRAPTC_BY_SESSION.get(session_id)
  if ept is None:
    ept = _new_entraptc_instance()
    _load_project_from_session_storage(ept, session_id)
    _ENTRAPTC_BY_SESSION[session_id] = ept
  return ept


def _session_project_path(session_id):
  run_dir = runtime_manager.get_run_dir(session_id)
  return os.path.join(run_dir, "session_project.json")


def _persist_project_to_session_storage(ept, session_id):
  run_dir = runtime_manager.get_run_dir(session_id)
  ept.prj.export_project("session_project", run_dir)


def _load_project_from_session_storage(ept, session_id):
  project_file = _session_project_path(session_id)
  if not os.path.isfile(project_file):
    return
  ept.clear_project()
  ept.prj.import_project(directory=os.path.dirname(project_file), name=os.path.basename(project_file), append=False, console=False)


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
  raise FileNotFoundError(
    "Tutorial project not found. Checked: " + "; ".join(checked)
  )


def create_or_get_session(force_new=False):
  ensure_user()
  current = _get_session_id()
  if current and not force_new:
    return current, False
  if current and force_new:
    close_current_session()

  session_id = str(uuid.uuid4())
  runtime_manager.create(session_id)
  # Lazy init: EntraPTc instance is created on first command that needs it.
  _call_if_registered("initialize_EntraPTc_session", session_id)
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
    _ENTRAPTC_BY_SESSION.pop(session_id, None)
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
    _ENTRAPTC_BY_SESSION.pop(sid, None)
    runtime_manager.close(sid)
    anvil.server.session.pop(SESSION_KEY, None)
    return {"closed_local_orphans": 1, "deleted_remote_orphans": 0}
  return {
    "closed_local_orphans": 0,
    "deleted_remote_orphans": 0,
  }


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

  return anvil.server.call(command, session_id, *args)


def get_list_analyses_for_tree(session_id):
  ept = _get_entraptc(session_id)
  analyses = ept.prj.list_analyses()
  tree = []
  for row in analyses:
    analysis_id = row.get("ID")
    label = row.get("label") or str(analysis_id)
    tree.append(
      {
        "title": label,
        "key": str(analysis_id),
      }
    )
  return tree


def get_list_analyses_for_view_data(session_id):
  ept = _get_entraptc(session_id)
  out = ept.prj.list_analyses(
    ID=True,
    HI_phases=True,
    strain=True,
    stress=True,
    notes=False,
    pinc_eos=True,
    pinc_stress=True,
  )
  print(out)
  return out


def load_tutorial_project():
  session_id = get_current_session_id()
  if session_id == -1:
    raise Exception("No active EntraPTc session")

  ept = _get_entraptc(session_id)
  tutorial_path = _resolve_tutorial_project_path()
  directory = os.path.dirname(tutorial_path)
  filename = os.path.basename(tutorial_path)

  ept.clear_project()
  ept.prj.import_project(directory=directory, name=filename, append=False, console=False)
  _persist_project_to_session_storage(ept, session_id)
  return {
    "path": tutorial_path,
    "analyses_count": len(ept.prj.list_analyses()),
  }


def get_HIsystem_properties(session_id, analysis_id):
  ept = _get_entraptc(session_id)
  analyses = ept.prj.get_analyses_by_ID(str(analysis_id))
  if not analyses:
    return "Analysis not found in current project."

  analysis = analyses[0]
  hi = analysis.HI_system
  if hi is None:
    return "HI system is not available for this analysis."

  try:
    text = hi.summary(console=False, print_output=False, output=True)
    return text if text else "No HI system summary available."
  except Exception as exc:
    return f"Cannot render HI system summary: {exc}"
