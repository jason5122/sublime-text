import sublime_plugin


class ToggleSideBarMovingFocus(sublime_plugin.WindowCommand):
    def run(self):
        if self.window.is_sidebar_visible():
            self.window.focus_group(self.window.active_group())
            self.window.set_sidebar_visible(False)
        else:
            self.window.set_sidebar_visible(True)
            self.window.run_command("focus_side_bar")
