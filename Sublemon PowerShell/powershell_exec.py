import os, sublime, sublime_plugin

class PowershellExecCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    if "shell_cmd" in args:
      command = [args["shell_cmd"]]
      del args["shell_cmd"]
    elif "cmd" in args:
      command = args["cmd"]
    else:
      return False

    load_profile = False
    if "load_profile" in args:
      load_profile = args["load_profile"]
      del args["load_profile"]

    script = os.path.join(sublime.packages_path(), "Sublemon PowerShell", "powershell_exec.ps1")

    cmd = ["powershell.exe"]
    if not load_profile:
      cmd.append("-NoProfile")
    cmd.extend(["-ExecutionPolicy", "Unrestricted", "-File", script, "-Command"])
    cmd.extend(command)

    args["cmd"] = cmd
    self.window.run_command("exec", args)
