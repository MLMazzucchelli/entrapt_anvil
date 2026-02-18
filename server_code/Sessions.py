import anvil.server

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
def miteosp_run(args, timeout=120, serialize_globally=True):
  return session_service.run_miteosp(
    args=args,
    timeout=timeout,
    serialize_globally=serialize_globally,
  )
