import json
import os
import socket
import subprocess
import sys
import time


HOST = os.environ.get("ENTRAPTC_DAEMON_HOST", "127.0.0.1")
PORT = int(os.environ.get("ENTRAPTC_DAEMON_PORT", "8765"))


def _daemon_script_path():
  file_here = globals().get("__file__")
  candidates = []
  if file_here:
    here = os.path.dirname(os.path.abspath(file_here))
    candidates.append(os.path.join(here, "entraptc_daemon.py"))

  cwd = os.path.abspath(os.getcwd())
  candidates.extend([
    os.path.join(cwd, "server_code", "entraptc_daemon.py"),
    os.path.join(cwd, "entrapt_anvil", "server_code", "entraptc_daemon.py"),
  ])

  for path in candidates:
    if os.path.isfile(path):
      return path
  raise FileNotFoundError("Cannot locate entraptc_daemon.py")


def _send(payload, timeout=30):
  with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
    data = (json.dumps(payload) + "\n").encode("utf-8")
    sock.sendall(data)
    fileobj = sock.makefile("rb")
    line = fileobj.readline()
    if not line:
      raise Exception("No response from EntraPTc daemon")
    response = json.loads(line.decode("utf-8"))
    if not response.get("ok"):
      raise Exception(response.get("error", "Unknown daemon error"))
    return response.get("result")


def _start_daemon():
  cmd = [sys.executable, _daemon_script_path(), "--host", HOST, "--port", str(PORT)]
  kwargs = {
    "stdin": subprocess.DEVNULL,
    "stdout": subprocess.DEVNULL,
    "stderr": subprocess.DEVNULL,
    "close_fds": True,
  }
  if os.name == "nt":
    kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
  subprocess.Popen(cmd, **kwargs)


def ensure_daemon():
  try:
    _send({"op": "ping"}, timeout=2)
    return
  except Exception:
    pass

  _start_daemon()
  deadline = time.time() + 8.0
  last_error = None
  while time.time() < deadline:
    try:
      _send({"op": "ping"}, timeout=2)
      return
    except Exception as exc:
      last_error = exc
      time.sleep(0.2)
  raise Exception(f"Cannot start EntraPTc daemon on {HOST}:{PORT}: {last_error}")


def request(op, **kwargs):
  ensure_daemon()
  payload = {"op": op}
  payload.update(kwargs)
  return _send(payload)
