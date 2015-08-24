import os, sublime, sublime_plugin

class PowershellExecCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    extract_argument = lambda x: self.extract_argument(x, args)

    prompt = extract_argument("prompt")
    if prompt:
      on_done = lambda x: self.run_parameterized(x, args)
      self.window.show_input_panel(prompt, '', on_done, None, None)
      return False

    if "shell_cmd" in args:
      command = [extract_argument("shell_cmd")]
    elif "cmd" in args:
      command = args["cmd"]
    else:
      return False

    context = extract_argument("context")
    show_output = not extract_argument("no_output")
    script = os.path.join(sublime.packages_path(), "Sublemon", "powershell_exec.ps1")

    cmd = ["powershell.exe", "-ExecutionPolicy", "Unrestricted"]

    if not extract_argument("load_profile"):
      cmd.append("-NoProfile")

    cmd.extend(["-File", script])

    if context:
      cmd.extend(["-Context", sublime.expand_variables(context, self.window.extract_variables())])

    cmd.append("-Command")
    cmd.extend(command)

    args["cmd"] = cmd
    self.window.run_command("exec", args)

    if show_output:
      self.window.run_command("show_panel", {"panel": "output.exec"})

  def extract_argument(self, name, args):
    if name in args:
      result = args[name]
      del args[name]
      return result

  def run_parameterized(self, input_string, args):
    variables = self.window.extract_variables()
    input_string = sublime.expand_variables(input_string, variables)

    variables['args'] = input_string
    args['shell_cmd'] = sublime.expand_variables(self.extract_argument('param_cmd', args), variables)

    self.run(**args)
