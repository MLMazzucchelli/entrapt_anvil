import os
import shutil
import subprocess
import tempfile

try:
  from filelock import FileLock
except Exception:
  FileLock = None


def _env_bool(name, default=True):
  value = os.environ.get(name)
  if value is None:
    return default
  return value.strip().lower() in ("1", "true", "yes", "y", "on")


ENTRAPTC_BIN = os.environ.get("ENTRAPTC_BIN", "entraptc")
RUNTIME_ROOT = os.environ.get(
  "ENTRAPTC_RUNTIME_ROOT",
  os.path.join(tempfile.gettempdir(), "entraptc_runtime"),
)
GLOBAL_LOCK_PATH = os.environ.get(
  "ENTRAPTC_GLOBAL_LOCK_PATH",
  os.path.join(RUNTIME_ROOT, "global.lock"),
)
SERIALIZE_GLOBALLY_DEFAULT = _env_bool("ENTRAPTC_SERIALIZE_GLOBALLY", True)


class RuntimeManager:
  def _ensure_root(self):
    os.makedirs(RUNTIME_ROOT, exist_ok=True)

  def _run_dir(self, session_id):
    self._ensure_root()
    return os.path.join(RUNTIME_ROOT, str(session_id))

  def _session_lock_path(self, session_id):
    self._ensure_root()
    return os.path.join(RUNTIME_ROOT, f"{session_id}.lock")

  def create(self, session_id):
    run_dir = self._run_dir(session_id)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

  def get_run_dir(self, session_id):
    return self.create(session_id)

  def close(self, session_id):
    run_dir = self._run_dir(session_id)
    shutil.rmtree(run_dir, ignore_errors=True)

  def run(self, session_id, args, timeout=120, serialize_globally=True):
    run_dir = self.create(session_id)
    cmd = [ENTRAPTC_BIN, *list(args or [])]
    serialize = SERIALIZE_GLOBALLY_DEFAULT if serialize_globally is None else serialize_globally

    def _execute():
      return subprocess.run(
        cmd,
        cwd=run_dir,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
      )

    if FileLock is not None:
      if serialize:
        with FileLock(GLOBAL_LOCK_PATH):
          with FileLock(self._session_lock_path(session_id)):
            completed = _execute()
      else:
        with FileLock(self._session_lock_path(session_id)):
          completed = _execute()
    else:
      completed = _execute()

    return {
      "stdout": completed.stdout,
      "stderr": completed.stderr,
      "returncode": completed.returncode,
      "run_dir": run_dir,
    }


manager = RuntimeManager()
