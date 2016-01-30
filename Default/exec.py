import sublime_plugin

class ExecCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        self.window.run_command("chimney", args)
