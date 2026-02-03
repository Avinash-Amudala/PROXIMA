"""Vercel entrypoint for the PROXIMA FastAPI application.

This file exposes a top-level `app` variable so that Vercel's FastAPI
integration can automatically detect and serve the API.

It simply imports the existing FastAPI app from `proxima.api.main`, while
making sure the `src/` directory is on `sys.path` when running in
serverless environments where the project is not installed as a package.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `src/` is on the Python path so `proxima` can be imported
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import the FastAPI application instance used everywhere else
from proxima.api.main import app  # noqa: E402,F401

