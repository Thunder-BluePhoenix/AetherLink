# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licenses is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licenses for the specific language governing permissions and
# limitations under the Licenses.

"""
AetherLinkService.py — Windows Service wrapper (Phase 5)

Registers AetherLink as a persistent Windows Service that:
  - Starts automatically on boot (set via install_service.ps1)
  - Runs uvicorn in a subprocess (isolated, audio-device-safe)
  - Captures all uvicorn output into a rotating log file
  - Recovers on failure via sc.exe recovery policy

Usage (run as Administrator):
    python AetherLinkService.py install    # register
    python AetherLinkService.py start      # start immediately
    python AetherLinkService.py stop       # stop
    python AetherLinkService.py remove     # unregister

Or use scripts/install_service.ps1 for a one-shot setup.
"""

import logging
import os
import subprocess
import sys
import threading
from logging.handlers import RotatingFileHandler

import servicemanager
import win32event
import win32service
import win32serviceutil

# ---------------------------------------------------------------------------
# Paths — all absolute so SYSTEM account resolves them correctly
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR  = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "aetherlink.log")
RUN_PY   = os.path.join(BASE_DIR, "run.py")

os.makedirs(LOG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Logging — RotatingFileHandler shared by service events + uvicorn output
# ---------------------------------------------------------------------------

def _setup_logging() -> None:
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def _pipe_reader(pipe, log_fn) -> None:
    """Read lines from a subprocess pipe and forward to the logger."""
    try:
        for raw in iter(pipe.readline, b""):
            log_fn(raw.decode(errors="replace").rstrip())
    finally:
        pipe.close()


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class AetherLinkService(win32serviceutil.ServiceFramework):
    _svc_name_         = "AetherLink"
    _svc_display_name_ = "AetherLink Agent"
    _svc_description_  = (
        "AetherLink voice-controlled PC agent — "
        "FastAPI server on port 58008, managed by Alexa + Lambda."
    )

    def __init__(self, args):
        super().__init__(args)
        self._stop_event = win32event.CreateEvent(None, 0, 0, None)
        self._proc: subprocess.Popen | None = None
        _setup_logging()

    # ------------------------------------------------------------------
    # Service control
    # ------------------------------------------------------------------

    def SvcStop(self) -> None:
        logging.info("Stop signal received — shutting down uvicorn.")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self._stop_event)
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logging.warning("Uvicorn did not exit cleanly — killing.")
                self._proc.kill()

    def SvcDoRun(self) -> None:
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        logging.info("=" * 60)
        logging.info("AetherLink service starting.")
        logging.info(f"BASE_DIR : {BASE_DIR}")
        logging.info(f"Python   : {sys.executable}")
        logging.info(f"run.py   : {RUN_PY}")

        self._proc = subprocess.Popen(
            [sys.executable, RUN_PY],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logging.info(f"Uvicorn started (PID {self._proc.pid}).")

        # Forward uvicorn stdout/stderr into the rotating log
        threading.Thread(
            target=_pipe_reader,
            args=(self._proc.stdout, logging.info),
            daemon=True,
        ).start()
        threading.Thread(
            target=_pipe_reader,
            args=(self._proc.stderr, logging.warning),
            daemon=True,
        ).start()

        # Block until stop event or process exits unexpectedly
        while True:
            rc = win32event.WaitForSingleObject(self._stop_event, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                break
            if self._proc.poll() is not None:
                logging.error(
                    f"Uvicorn exited unexpectedly "
                    f"(returncode={self._proc.returncode}). Stopping service."
                )
                break

        logging.info("AetherLink service stopped.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Invoked by the SCM — hand control to the dispatcher
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AetherLinkService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # CLI: install / start / stop / remove
        win32serviceutil.HandleCommandLine(AetherLinkService)
