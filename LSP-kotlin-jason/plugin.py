import os
import re
import hashlib
import zipfile
from urllib.parse import urlparse, unquote

import sublime

from typing import Callable, Optional, Tuple

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin
from LSP.plugin.core.protocol import DocumentUri


_JAR_SPLIT = re.compile(r"!(?:/|\\)")
_TEXT_EXTS = {".kt", ".kts", ".java", ".txt", ".md", ".properties", ".xml", ".gradle", ".groovy"}


def _syntax_for_path(inner_path: str) -> str:
    lower = inner_path.lower()
    if lower.endswith((".kt", ".kts")):
        return "Packages/Kotlin/Kotlin.tmLanguage"
    if lower.endswith(".java"):
        return "Packages/Java/Java.sublime-syntax"
    return "Packages/Text/Plain text.tmLanguage"


def _cache_dir() -> str:
    base = sublime.cache_path()
    path = os.path.join(base, "KotlinJason", "jar")
    os.makedirs(path, exist_ok=True)
    return path


def _safe_cache_key(jar_path: str, inner_path: str) -> str:
    try:
        st = os.stat(jar_path)
        mtime_ns = getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000))
        size = st.st_size
    except OSError:
        mtime_ns = 0
        size = 0
    h = hashlib.sha256("{}\n{}\n{}\n{}".format(jar_path, inner_path, mtime_ns, size).encode("utf-8")).hexdigest()
    return h


def _parse_jar_uri(uri: str) -> Optional[Tuple[str, str]]:
    """
    Supports:
      jar:///Users/me/x-sources.jar!/a/b/C.kt
      jar://Users/me/x-sources.jar!/a/b/C.kt
      jar:file:///Users/me/x.jar!/a/b/C.kt
    Returns (jar_path_on_disk, inner_path_in_jar)
    """
    if not uri.startswith("jar:"):
        return None

    rest = uri[len("jar:") :]

    # jar:file:///... style
    if rest.startswith("file:"):
        rest = rest[len("file:") :]

    # Parse as a file URL by prefixing file:
    parsed = urlparse("file:" + rest)
    full_path = unquote(parsed.path)

    parts = _JAR_SPLIT.split(full_path, maxsplit=1)
    if len(parts) != 2:
        return None
    jar_path, inner_path = parts[0], parts[1]
    inner_path = inner_path.replace("\\", "/")

    if not jar_path.lower().endswith((".jar", ".zip")):
        return None

    return jar_path, inner_path


def _read_jar_entry_text(jar_path: str, inner_path: str) -> str:
    with zipfile.ZipFile(jar_path, "r") as zf:
        data = zf.read(inner_path)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


class KotlinJason(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "kotlin-jason"

    def on_open_uri_async(self, uri: DocumentUri, callback: Callable[[str, str, str], None]) -> bool:
        parsed = _parse_jar_uri(uri)
        if not parsed:
            return False

        jar_path, inner_path = parsed

        _, ext = os.path.splitext(inner_path.lower())
        if ext and ext not in _TEXT_EXTS:
            return False

        try:
            key = _safe_cache_key(jar_path, inner_path)
            cache_path = os.path.join(_cache_dir(), key + os.path.splitext(inner_path)[1])

            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            else:
                text = _read_jar_entry_text(jar_path, inner_path)
                with open(cache_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(text)

            display_name = "{}!/{}".format(os.path.basename(jar_path), inner_path)
            callback(display_name, text, _syntax_for_path(inner_path))
            return True

        except KeyError:
            callback("ERROR", "Entry not found in jar: {}".format(inner_path), "Packages/Text/Plain text.tmLanguage")
            return True
        except (OSError, zipfile.BadZipFile, RuntimeError) as e:
            callback("ERROR", "{}: {}".format(type(e).__name__, e), "Packages/Text/Plain text.tmLanguage")
            return True


def plugin_loaded() -> None:
    register_plugin(KotlinJason)


def plugin_unloaded() -> None:
    unregister_plugin(KotlinJason)
