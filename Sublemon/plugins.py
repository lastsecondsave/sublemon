import sublime, sublime_plugin

class ExecPowershellCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        if "shell_cmd" in args:
            if "cmd" not in args:
                args["cmd"] = ["powershell.exe",
                        "-Command", "sublbuild;" + args["shell_cmd"]]
            del args["shell_cmd"]
        self.window.run_command("exec", args)
