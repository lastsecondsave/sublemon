import os, sublime, sublime_plugin

class PowershellExecCommand(sublime_plugin.WindowCommand):

  def run(self, **args):
    if not "shell_cmd" in args or "cmd" in args:
      self.window.run_command("exec", args)

    script = os.path.join(sublime.packages_path(), "Sublemon PowerShell", "powershell_exec.ps1")
    command = args["shell_cmd"]

    args["cmd"] = ["powershell.exe",
        "-ExecutionPolicy", "Unrestricted", "-File", script, "-Command", command]
    del args["shell_cmd"]
    self.window.run_command("exec", args)
