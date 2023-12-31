import os.path

import sublime
import sublime_plugin


class OpenPackageFileCommand(sublime_plugin.ApplicationCommand):
    def run(self, file):
        """
        :param file:
            A unicode string of the path to the file.
            Typically this will be in the form: "${packages}/PackageName/Package.sublime-settings"
        """

        if file is None:
            raise ValueError('No file argument was passed to edit_settings')

        base_path = file.replace('${packages}', 'res://Packages')
        is_resource = base_path.startswith('res://')
        file_name = os.path.basename(file)
        resource_exists = is_resource and base_path[6:] in sublime.find_resources(file_name)
        filesystem_exists = (not is_resource) and os.path.exists(base_path)

        if not resource_exists and not filesystem_exists:
            sublime.error_message('The settings file "' + base_path + '" could not be opened')
            return

        # If the user has previously opened the settings from the menu, locate and bring to front the respective window
        windows = sublime.windows()
        previous_settings_index = -1
        view_to_focus = None

        for window in windows:
            base_view = window.find_open_file(file.replace('${packages}', sublime.packages_path()))

            if window.get_view_index(base_view) != (-1, -1):
                previous_settings_index = windows.index(window)
                view_to_focus = base_view
                break

        if previous_settings_index > -1:
            settings_window = windows[previous_settings_index]
            settings_window.bring_to_front()
            settings_window.focus_view(view_to_focus)
        else:
            sublime.active_window().run_command('open_file', {'file': file})
