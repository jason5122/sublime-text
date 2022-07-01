import sublime
import sublime_plugin


class CloseTerminusViewCommand(sublime_plugin.WindowCommand):
    """
    Close all terminus views in the current window that have the title
    provided.
    """
    def run(self, title):
        current = self.window.active_view()

        for view in self.window.views():
            if view.name() == title:
                view.run_command('terminus_close')

        self.window.focus_view(current)


class WindowFocusCommand(sublime_plugin.WindowCommand):
    """
    Store the current selected group of files and which file is active in that
    group, and later restore that selection.
    """
    group = None
    index = None

    def run(self, store):
        if store:
            view = self.window.active_view()
            self.group, self.index = self.window.get_view_index(view)
        else:
            if self.group is not None and self.index is not None:
                view = self.window.views_in_group(self.group)[self.index]
                self.window.focus_group(self.group)
                self.window.focus_view(view)
