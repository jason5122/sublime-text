import sublime
import sublime_plugin


def plugin_unloaded():
    for window in sublime.windows():
        for view in window.views():
            view.run_command("clear_scopes")
            view.erase_phantoms("scopes")


def _display_scope(view):
    if not hasattr(_display_scope, "buffer_table"):
        _display_scope.buffer_table = {}

    # Obtain the phantom set used for this view
    buff_id = view.buffer_id()
    phantoms = _display_scope.buffer_table.get(buff_id, None)
    if phantoms is None:
        phantoms = sublime.PhantomSet(view, "scopes")
        _display_scope.buffer_table[buff_id] = phantoms

    scope_text = view.scope_name(view.sel()[0].b)
    # phantom_region = sublime.Region(view.line(view.size()).a)
    phantom_region = sublime.Region(view.line(view.sel()[0]).a)

    phantoms.update([
        sublime.Phantom(
            phantom_region,
            """
                <body id="scope_line">
                    <style>
                        div.scope {{
                            border-top: 0.1rem solid color(var(--greenish))
                        }}
                    </style>
                    <div class="scope">{scope}</span>
                </body>
            """.format(scope=scope_text.replace(" ", "<br>")),
            sublime.LAYOUT_BELOW
            )
        ])


class ScopeInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, initial):
        self.initial = initial.strip()

    def placeholder(self):
        return "scope selector"

    def initial_text(self):
        return self.initial


class ViewScopesCommand(sublime_plugin.TextCommand):
    last_scope=""

    def run(self, edit, scope):
        self.last_scope = scope

        matches = self.view.find_by_selector(scope)
        if matches:
            self.view.add_regions("scope_matches", matches, scope,
                                  "dot", sublime.DRAW_NO_FILL)
        else:
            self.view.run_command("clear_scopes")
            sublime.status_message("No matching scopes found")

    def input(self, args):
        if args.get("scope", None) is None:
            return ScopeInputHandler(self.last_scope)

    def input_description(self):
        return "View scopes matching:"


class ClearScopesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_regions("scope_matches")


class ToggleScopeDisplayCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        display = not self.view.settings().get("_display_scopes", False)
        self.view.settings().set("_display_scopes", display)

        if display:
            _display_scope(self.view)
        else:
            self.view.erase_phantoms("scopes")


class ScopeDisplayListener(sublime_plugin.EventListener):
    buffer_table = {}

    def on_selection_modified(self, view):
        if (view.settings().get("is_widget", False) or
            view.settings().get("_display_scopes", False) == False):
            return

        _display_scope(view)
