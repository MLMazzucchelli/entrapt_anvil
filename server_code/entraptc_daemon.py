import argparse
import json
import os
import socketserver
import sys
import tempfile
import threading
import time


RUNTIME_ROOT = os.environ.get(
  "ENTRAPTC_RUNTIME_ROOT",
  os.path.join(tempfile.gettempdir(), "entraptc_runtime"),
)
SESSION_IDLE_TIMEOUT_SECONDS = int(os.environ.get("ENTRAPTC_SESSION_IDLE_TIMEOUT_SECONDS", "1800"))

_SESSIONS = {}
_SESSIONS_LOCK = threading.RLock()


def _import_entraptc_class():
  def _import_direct():
    try:
      from miteos.entraptc.entraptc import EntraPTc
      return EntraPTc
    except Exception:
      from miteos.entraptc import EntraPTc
      return EntraPTc

  try:
    return _import_direct()
  except Exception:
    candidates = [
      os.environ.get("MITEOSP_SRC"),
      os.environ.get("MITEOSP_HOME"),
      os.path.abspath(os.path.join(os.getcwd(), "..", "MITEoSp")),
      os.path.abspath(os.path.join(os.getcwd(), "MITEoSp")),
      r"C:\Users\mmazzucc\Documents\GitHub\MITEoSp",
      r"C:\Users\mmazzucc\Documents\GitHub\MITEoSp\src",
    ]
    for path in candidates:
      if not path:
        continue
      for src_dir in (path, os.path.join(path, "src")):
        if os.path.isdir(src_dir) and src_dir not in sys.path:
          sys.path.insert(0, src_dir)
    return _import_direct()


def _run_dir(session_id):
  os.makedirs(RUNTIME_ROOT, exist_ok=True)
  run_dir = os.path.join(RUNTIME_ROOT, str(session_id))
  os.makedirs(run_dir, exist_ok=True)
  return run_dir


def _session_project_path(session_id):
  return os.path.join(_run_dir(session_id), "session_project.json")


def _new_ept():
  EntraPTc = _import_entraptc_class()
  return EntraPTc()


def _persist(ept, session_id):
  ept.prj.export_project("session_project", _run_dir(session_id))


def _load_if_present(ept, session_id):
  project_file = _session_project_path(session_id)
  if not os.path.isfile(project_file):
    return
  ept.clear_project()
  ept.prj.import_project(
    directory=os.path.dirname(project_file),
    name=os.path.basename(project_file),
    append=False,
    console=False,
  )


def _close_ept(ept):
  if ept is None:
    return
  for name in ("close", "shutdown", "stop"):
    fn = getattr(ept, name, None)
    if callable(fn):
      try:
        fn()
      except Exception:
        pass
      return


def _touch(session):
  session["last_access"] = time.time()


def _ensure_session(session_id):
  with _SESSIONS_LOCK:
    sess = _SESSIONS.get(session_id)
    if sess is None:
      ept = _new_ept()
      _load_if_present(ept, session_id)
      sess = {
        "ept": ept,
        "lock": threading.RLock(),
        "last_access": time.time(),
      }
      _SESSIONS[session_id] = sess
    _touch(sess)
    return sess


def _close_session(session_id):
  with _SESSIONS_LOCK:
    sess = _SESSIONS.pop(session_id, None)
  if not sess:
    return False
  with sess["lock"]:
    try:
      _persist(sess["ept"], session_id)
    except Exception:
      pass
    _close_ept(sess["ept"])
  return True


def _cleanup_idle():
  if SESSION_IDLE_TIMEOUT_SECONDS <= 0:
    return 0
  now = time.time()
  stale = []
  with _SESSIONS_LOCK:
    for sid, sess in list(_SESSIONS.items()):
      if now - float(sess.get("last_access", now)) >= SESSION_IDLE_TIMEOUT_SECONDS:
        stale.append(sid)
  for sid in stale:
    _close_session(sid)
  return len(stale)


def _cmd_get_tree(ept):
  out = []
  for row in ept.prj.list_analyses():
    analysis_id = row.get("ID")
    label = row.get("label") or str(analysis_id)
    out.append({"title": label, "key": str(analysis_id)})
  return out


def _cmd_get_view_data(ept):
  return ept.prj.list_analyses(
    ID=True,
    HI_phases=False,
    HI_names=True,
    strain=True,
    stress=True,
    notes=False,
    pinc_eos=True,
    pinc_stress=True,
  )


def _cmd_get_hi_properties(ept, analysis_id):
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


def _dispatch(session_id, command, args):
  sess = _ensure_session(session_id)
  with sess["lock"]:
    ept = sess["ept"]

    if command == "get_list_analyses_for_tree":
      return _cmd_get_tree(ept)
    if command == "get_list_analyses_for_view_data":
      return _cmd_get_view_data(ept)
    if command == "get_HIsystem_properties":
      if not args:
        raise Exception("get_HIsystem_properties requires analysis_id")
      return _cmd_get_hi_properties(ept, args[0])
    if command == "clear_project_in_EntraPTc":
      ept.clear_project()
      _persist(ept, session_id)
      return True
    if command == "overwrite_project_in_EntraPTc":
      if len(args) < 2:
        raise Exception("overwrite_project_in_EntraPTc requires (filename, project_path)")
      project_path = str(args[1])
      ept.clear_project()
      ept.prj.import_project(
        directory=os.path.dirname(project_path),
        name=os.path.basename(project_path),
        append=False,
        console=False,
      )
      _persist(ept, session_id)
      return {"path": project_path, "analyses_count": len(ept.prj.list_analyses())}
    if command == "load_project_from_file":
      if not args:
        raise Exception("load_project_from_file requires path")
      project_path = str(args[0])
      ept.clear_project()
      ept.prj.import_project(
        directory=os.path.dirname(project_path),
        name=os.path.basename(project_path),
        append=False,
        console=False,
      )
      _persist(ept, session_id)
      return {"path": project_path, "analyses_count": len(ept.prj.list_analyses())}

    method = getattr(ept, command, None)
    if not callable(method):
      raise Exception(f"Unknown command: {command}")
    result = method(*list(args or []))
    try:
      _persist(ept, session_id)
    except Exception:
      pass
    return result


def _handle_request(req):
  op = req.get("op")
  if op == "ping":
    return {"status": "ok"}
  if op == "create_session":
    session_id = str(req["session_id"])
    _ensure_session(session_id)
    return {"session_id": session_id}
  if op == "close_session":
    return {"closed": _close_session(str(req["session_id"]))}
  if op == "touch_session":
    session_id = str(req["session_id"])
    sess = _ensure_session(session_id)
    _touch(sess)
    return {"session_id": session_id}
  if op == "cleanup_idle":
    return {"closed_idle_sessions": _cleanup_idle(), "timeout_seconds": SESSION_IDLE_TIMEOUT_SECONDS}
  if op == "dispatch":
    return _dispatch(str(req["session_id"]), str(req["command"]), list(req.get("args", [])))
  raise Exception(f"Unknown op: {op}")


class _Handler(socketserver.StreamRequestHandler):
  def handle(self):
    raw = self.rfile.readline()
    if not raw:
      return
    try:
      req = json.loads(raw.decode("utf-8"))
      result = _handle_request(req)
      payload = {"ok": True, "result": result}
    except Exception as exc:
      payload = {"ok": False, "error": str(exc)}
    self.wfile.write((json.dumps(payload) + "\n").encode("utf-8"))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--host", default="127.0.0.1")
  parser.add_argument("--port", type=int, default=int(os.environ.get("ENTRAPTC_DAEMON_PORT", "8765")))
  args = parser.parse_args()

  server = socketserver.ThreadingTCPServer((args.host, args.port), _Handler)
  server.daemon_threads = True
  server.allow_reuse_address = True
  with server:
    server.serve_forever()


if __name__ == "__main__":
  main()
