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

    load_profile = self.get_argument("load_profile", args)
    context = self.get_argument("context", args)

    script = os.path.join(sublime.packages_path(), "Sublemon", "powershell_exec.ps1")

    cmd = ["powershell.exe", "-ExecutionPolicy", "Unrestricted"]

    if not load_profile:
      cmd.append("-NoProfile")

    cmd.extend(["-File", script])

    if context:
      cmd.extend(["-Context", sublime.expand_variables(context, self.window.extract_variables())])

    cmd.append("-Command")
    cmd.extend(command)

    args["cmd"] = cmd
    self.window.run_command("exec", args)

  def get_argument(self, name, args):
    result = None
    if name in args:
      result = args[name]
      del args[name]
    return result
