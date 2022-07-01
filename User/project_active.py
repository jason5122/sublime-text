import sublime_plugin

class ProjectActiveEventListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key != "project_active":
            return None

        project_name = view.window().project_data()
        
        if project_name:
            return True
        else:
            return False
