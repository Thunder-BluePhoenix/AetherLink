"""
aetherlink/services/shell.py — Sandboxed shell interface

Wraps subprocess.run with:
  - Command allowlist enforcement (no raw input to shell)
  - Working directory pinned to a mapped project path
  - stdout/stderr capture
  - Execution timeout

Phase 2 implementation.
"""

# TODO (Phase 2): define ALLOWED_COMMANDS allowlist
# TODO (Phase 2): implement run_command(command, cwd, timeout) -> dict
