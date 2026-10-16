"""Lets scripts import the traffix package when run as  python scripts/<name>.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load KEY=value lines from the repo's .env (gitignored) without overriding real env vars.
_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.isfile(_env):
    with open(_env, encoding="utf-8") as f:
        for _line in f:
            _key, _sep, _value = _line.strip().partition("=")
            if _sep and not _key.startswith("#"):
                os.environ.setdefault(_key.strip(), _value.strip().strip('"'))
