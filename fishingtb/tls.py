"""Portable certificate trust for Python installations without a macOS CA bundle."""

import ssl
import certifi


def verified_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())
