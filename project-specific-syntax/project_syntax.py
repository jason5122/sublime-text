import json
import os.path
import re
import sublime
import sublime_plugin


class ProjectSpecificSyntax(sublime_plugin.EventListener):
    def on_load(self, view):
        self._ensure_project_specific_syntax(view)

    def _ensure_project_specific_syntax(self, view):
        filename = view.file_name()
        if not filename:
            return

        syntax = self._get_project_specific_syntax(view, filename)
        if syntax:
            view.assign_syntax(f"scope:{syntax}")

    def _get_project_specific_syntax(self, view, filename):
        project_data = _resolve_window(view).project_data()

        if not project_data:
            return None

        syntax_settings = project_data.get('syntax_override', {})

        for regex, syntax in syntax_settings.items():
            if re.search(regex, filename):
                return syntax

        return None


def _resolve_window(view):
    window = view.window()

    if window:
        return window

    return sublime.active_window()
