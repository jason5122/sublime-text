# https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/sublime_ide.md
# https://chromium.googlesource.com/chromium/llvm-project/cfe/tools/clang-format/+/refs/heads/main/clang-format-sublime.py

from typing import Optional, Tuple

import sublime
import sublime_plugin
import subprocess
import json

binary = 'clang-format'


class ClangFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        settings = view.settings()

        encoding = view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        tab_size = settings.get('tab_size')
        use_spaces = settings.get('translate_tabs_to_spaces')

        scope = view.syntax().scope
        language, filename = get_language_from_scope(scope)
        if not language and not filename:
            print(f"clang-format: no language found for {scope}")
            return

        command = [binary]
        command.extend(['-assume-filename', filename])
        style = {
            "Language": language,
            "IndentWidth": tab_size,
            "TabWidth": tab_size,
            # "BasedOnStyle": "Google",
            "ColumnLimit": 79,  # TODO: evaluate if this is hacky or not
            # Custom options
            "AllowShortBlocksOnASingleLine": "Empty",
            "AllowShortFunctionsOnASingleLine": "Empty",
            "AllowShortIfStatementsOnASingleLine": "AllIfsAndElse",
            "AllowShortLoopsOnASingleLine": True,
            # "InsertBraces": True,
            "SpacesBeforeTrailingComments": 2,
            "AccessModifierOffset": -tab_size,
            "PointerAlignment": "Left",
            "AlignTrailingComments": True,
        }
        if not use_spaces:
            style['UseTab'] = 'ForIndentation'
        if style:
            command.extend(['-style', json.dumps(style)])

        old_viewport_position = view.viewport_position()
        old_cursor = None
        for region in view.sel():
            if region.empty():
                old_cursor = region
            else:
                command.extend(
                    [
                        '-offset',
                        str(region.begin()),
                        '-length',
                        str(region.size()),
                    ]
                )

        if old_cursor is not None:
            command.extend(['-cursor', str(old_cursor.begin())])

        buf = view.substr(sublime.Region(0, view.size()))
        if not buf:
            return

        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        output, error = p.communicate(buf.encode(encoding))
        if error:
            print(error)
            return

        output = output.decode(encoding)
        if old_cursor is not None:
            output_info, _, output = output.partition('\n')
            output_info = json.loads(output_info)
        view.replace(edit, sublime.Region(0, view.size()), output)

        view.sel().clear()
        if old_cursor is not None:
            new_cursor = sublime.Region(output_info['Cursor'])
            view.sel().add(new_cursor)


def get_language_from_scope(scope) -> Tuple[Optional[str], Optional[str]]:
    if scope == 'source.c++':
        return ('Cpp', 'file.cpp')
    elif scope == 'source.c':
        return ('Cpp', 'file.c')
    elif scope == 'source.java':
        return ('Java', 'file.java')
    elif scope == 'source.objc':
        return ('ObjC', 'file.m')
    elif scope == 'source.objc++':
        return ('ObjC', 'file.mm')
    elif scope == 'source.glsl':
        return ('Cpp', 'file.glsl')
    else:
        return (None, None)  # no language found
