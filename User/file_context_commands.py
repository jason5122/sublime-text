import sublime
import sublime_plugin


class RenameFileContextCommand(sublime_plugin.TextCommand):
    def run(self, edit, group, index):
        window = self.view.window()
        window.focus_group(group)
        window.focus_view(window.views_in_group(group)[index])
        window.run_command(
            "show_overlay",
            {"overlay": "command_palette", "command": "rename_file"},
        )

    def is_enabled(self, group, index):
        window = self.view.window()
        new_view = window.views_in_group(group)[index]

        return new_view.file_name() is not None


class DeleteFileContextCommand(sublime_plugin.TextCommand):
    def run(self, edit, group, index):
        window = self.view.window()
        new_view = window.views_in_group(group)[index]

        window.focus_group(group)
        window.focus_view(new_view)

        window.run_command(
            "delete_file",
            {"files": [new_view.file_name()], "prompt": True},
        )

    def is_enabled(self, group, index):
        window = self.view.window()
        new_view = window.views_in_group(group)[index]

        return new_view.file_name() is not None
