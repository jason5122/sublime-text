import sublime
import sublime_plugin
import os
import sys
import subprocess
import locale


class NotFoundError(Exception):
    pass


installed_dir, _ = __name__.split('.')


def get_setting(key, default=None):
    settings = sublime.load_settings('Terminal.sublime-settings')
    os_specific_settings = {}
    if os.name == 'nt':
        os_specific_settings = sublime.load_settings('Terminal (Windows).sublime-settings')
    elif sys.platform == 'darwin':
        os_specific_settings = sublime.load_settings('Terminal (OSX).sublime-settings')
    else:
        os_specific_settings = sublime.load_settings('Terminal (Linux).sublime-settings')
    return os_specific_settings.get(key, settings.get(key, default))


class TerminalSelector:
    default = None

    @staticmethod
    def get(terminal_key):
        package_dir = os.path.join(sublime.packages_path(), installed_dir)
        terminal = get_setting(terminal_key)
        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(package_dir, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0o755)
            return terminal

        if TerminalSelector.default:
            return TerminalSelector.default

        default = None

        if sys.platform == 'darwin':
            default = os.path.join(package_dir, 'Terminal.sh')
            if not os.access(default, os.X_OK):
                os.chmod(default, 0o755)

        TerminalSelector.default = default
        return default


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
            sublime.error_message('Terminal: No place to open terminal to')
            return False

    def run_terminal(self, dir_, terminal, parameters):
        try:
            if not dir_:
                raise NotFoundError(
                    'The file open in the selected view has ' + 'not yet been saved'
                )
            for k, v in enumerate(parameters):
                parameters[k] = v.replace('%CWD%', dir_)
            args = [TerminalSelector.get(terminal)]
            args.extend(parameters)

            encoding = locale.getpreferredencoding(do_setlocale=True)
            cwd = dir_

            # Copy over environment settings onto parent environment
            env_setting = get_setting('env', {})
            env = os.environ.copy()
            for k in env_setting:
                if env_setting[k] is None:
                    env.pop(k, None)
                else:
                    env[k] = env_setting[k]

            # Run our process
            subprocess.Popen(args, cwd=cwd, env=env)

        except OSError as exception:
            print(str(exception))
            sublime.error_message(
                'Terminal: The terminal ' + TerminalSelector.get() + ' was not found'
            )
        except Exception as exception:
            sublime.error_message('Terminal: ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[], parameters=None, terminal=None):
        path = self.get_path(paths)
        if not path:
            return

        if terminal is None:
            terminal = 'terminal'

        if parameters is None:
            parameters = get_setting('parameters', [])

        if os.path.isfile(path):
            path = os.path.dirname(path)

        self.run_terminal(path, terminal, parameters)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand, TerminalCommand):
    def run(self, paths=[], parameters=None):
        path = self.get_path(paths)
        if not path:
            return

        command = OpenTerminalCommand(self.window)
        command.run(self.window.folders(), parameters=parameters)
