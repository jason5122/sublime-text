import sublime
import sublime_plugin


class CheckClosedEventHandler(sublime_plugin.EventListener):
    def on_pre_close(self, view):
        # Do nothing if the view that's about to close is a transient view.
        if view.sheet().is_transient():
            return
        if not view.window():
            return

        # Get the group number for this view
        group, _ = view.window().get_view_index(view)

        # If this is the last view in this group, destroy the pane. We defer
        # changing the layout until after the close event finishes since
        # changing the window layout while views are actively closing seems to
        # be a Very Bad Idea (tm)
        if len(view.window().views_in_group(group)) == 1:
            window = view.window()
            sublime.set_timeout(
                lambda: window.run_command("destroy_pane", {"direction": "self"})
            )
