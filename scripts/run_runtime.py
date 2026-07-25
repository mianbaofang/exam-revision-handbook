from __future__ import annotations

import argparse
import subprocess
import sys

from _runtime import (
    ensure_runtime,
    print_json,
    runtime_python,
)


SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Pass commands and exit codes through to the isolated packaged engine."
RUNTIME_NETWORK_POLICY_HOSTS = (
    "https://www.aqa.org.uk",
    "https://www.oxfordaqa.com",
    "https://qualifications.pearson.com",
    "https://www.cambridgeinternational.org",
    "https://apcentral.collegeboard.org",
    "https://apstudents.collegeboard.org",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a packaged intl-exam-guide command after a -- delimiter."
    )
    parser.add_argument("runtime_args", nargs=argparse.REMAINDER)
    parsed = parser.parse_args(sys.argv[1:] if argv is None else argv)
    args = list(parsed.runtime_args)
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        print_json({"ok": False, "error": "missing runtime command after --"})
        return 2
    try:
        lock, root = ensure_runtime()
        command = [str(runtime_python(root)), "-m", str(lock["engine"]["module"]), *args]
        return subprocess.run(command, check=False).returncode
    except (OSError, RuntimeError, ValueError) as exc:
        print_json({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
