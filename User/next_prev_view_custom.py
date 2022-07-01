# Moves to the next/previous view, even across panes

import sublime
import sublime_plugin


class NextViewCustomCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window

        try:
            index = window.views().index(window.active_view())
        except ValueError as e:
            return

        # keeps index within list range
        num_views = len(window.views())
        next_index = (((index + 1) % num_views) + num_views) % num_views
        window.focus_view(window.views()[next_index])


class PrevViewCustomCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window

        try:
            index = window.views().index(window.active_view())
        except ValueError as e:
            return

        # keeps index within list range
        num_views = len(window.views())
        prev_index = (((index - 1) % num_views) + num_views) % num_views
        window.focus_view(window.views()[prev_index])
