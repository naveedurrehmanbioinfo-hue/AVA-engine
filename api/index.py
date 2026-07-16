"""Vercel serverless entry point — wraps the existing FastAPI app.

Locally the app/web split works because docker-compose mounts
./backend/app -> /code/app and ./web -> /code/web, making them siblings.
On Vercel there's no such mount, so we point AVA_WEB_DIR at the real
app/web directory before importing the app.
"""
import os
import sys

_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_APP_ROOT, "app", "backend")

sys.path.insert(0, _BACKEND_DIR)
os.environ.setdefault("AVA_WEB_DIR", os.path.join(_APP_ROOT, "app", "web"))

from app.main import app  # noqa: E402
