"""
Based on:
https://github.com/jfcherng-sublime/ST-my-settings/blob/920668c2181aa6450e0a7930770fb2536c48526c/Packages/my_plugin_38/step_tab_cycle_command.py
"""

import sublime_plugin


class MoveTabCommand(sublime_plugin.WindowCommand):
    def run(self, steps: int) -> None:
        window = self.window

        if not (sheet := window.active_sheet()):
            return

        group_index, sheet_index = window.get_sheet_index(sheet)
        sheets = window.sheets_in_group(group_index)
        sheet_index_focus = (sheet_index + steps) % len(sheets)
        window.set_sheet_index(sheet, group_index, sheet_index_focus)
        window.focus_sheet(sheet)
