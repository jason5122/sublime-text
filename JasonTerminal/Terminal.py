import sublime
import sublime_plugin
import os
import sys
import subprocess


installed_dir, _ = __name__.split(".")


def get_setting(key: str, default=None):
    settings = sublime.load_settings("Terminal.sublime-settings")
    os_specific_settings = dict()
    if os.name == "nt":
        os_specific_settings = sublime.load_settings("Terminal (Windows).sublime-settings")
    elif sys.platform == "darwin":
        os_specific_settings = sublime.load_settings("Terminal (OSX).sublime-settings")
    else:
        os_specific_settings = sublime.load_settings("Terminal (Linux).sublime-settings")
    return os_specific_settings.get(key, settings.get(key, default))


class TerminalCommand:
    def get_path(self, paths):
        if paths:
            return paths[0]
        # DEV: On ST3, there is always an active view.
        #   Be sure to check that it's a file with a path (not temporary view)
        elif self.window.active_view() and self.window.active_view().file_name():
            return self.window.active_view().file_name()
        elif self.window.folders():
            return self.window.folders()[0]
        else:
            return False

    def run_terminal(self, cwd: str):
        # Substitute current working directory in the command.
        cmd = get_setting("cmd")
        cmd = [arg.replace("%CWD%", cwd) for arg in cmd]

        # Copy over environment overrides onto parent environment.
        env = os.environ.copy()
        env_overrides = get_setting("env", {})
        for k in env_overrides:
            if env_overrides[k] is None:
                env.pop(k, None)
            else:
                env[k] = env_overrides[k]

        subprocess.Popen(cmd, cwd=cwd, env=env)


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[]):
        path = self.get_path(paths)
        if not path:
            sublime.error_message("Terminal: No place to open terminal to")
            return

        if os.path.isfile(path):
            path = os.path.dirname(path)

        self.run_terminal(path)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[]):
        path = self.get_path(paths)
        if not path:
            return

        command = OpenTerminalCommand(self.window)
        command.run(self.window.folders())
