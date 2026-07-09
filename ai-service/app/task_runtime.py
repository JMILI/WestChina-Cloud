"""Runtime state for cancellable AI tasks."""
from __future__ import annotations

import multiprocessing
import threading
from typing import Dict, Optional

_lock = threading.Lock()
_cancel_events: Dict[str, threading.Event] = {}
_fusion_processes: Dict[str, multiprocessing.Process] = {}


def register_task(task_id: str | None) -> Optional[threading.Event]:
    if not task_id:
        return None
    with _lock:
        event = _cancel_events.get(task_id)
        if event is None:
            event = threading.Event()
            _cancel_events[task_id] = event
        return event


def unregister_task(task_id: str | None) -> None:
    if not task_id:
        return
    with _lock:
        _cancel_events.pop(task_id, None)
        _fusion_processes.pop(task_id, None)


def is_task_cancelled(task_id: str | None) -> bool:
    if not task_id:
        return False
    with _lock:
        event = _cancel_events.get(task_id)
        return bool(event and event.is_set())


def cancel_task(task_id: str | None) -> bool:
    if not task_id:
        return False
    with _lock:
        event = _cancel_events.get(task_id)
        if event is None:
            event = threading.Event()
            _cancel_events[task_id] = event
        event.set()
        proc = _fusion_processes.pop(task_id, None)
    if proc is not None and proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=2)
    return True


def register_fusion_process(task_id: str | None, proc: multiprocessing.Process) -> None:
    if not task_id:
        return
    with _lock:
        _fusion_processes[task_id] = proc


def unregister_fusion_process(task_id: str | None, proc: multiprocessing.Process | None = None) -> None:
    if not task_id:
        return
    with _lock:
        current = _fusion_processes.get(task_id)
        if proc is None or current is proc:
            _fusion_processes.pop(task_id, None)
