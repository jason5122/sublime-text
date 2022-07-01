import sublime
import sublime_plugin

class ClearConsoleCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        scrollback = s.get("console_max_history_lines")
        s.set("console_max_history_lines", 1)
        print("")
        s.set("console_max_history_lines", scrollback)
