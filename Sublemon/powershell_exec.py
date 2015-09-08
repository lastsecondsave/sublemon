import os, sublime, sublime_plugin

class SimpleExecCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    prompt = self.extract_argument("prompt", args, expand=True)
    if prompt:
      on_done = lambda x: self.run_parameterized(x, args)
      self.window.show_input_panel(prompt, '', on_done, None, None)
      return False

    show_output = not self.extract_argument("no_output", args)

    self.mutate_arguments(args)

    self.window.run_command("exec", args)
    if show_output:
      self.window.run_command("show_panel", {"panel": "output.exec"})

  def extract_argument(self, name, args, expand=False):
    if not name in args:
      return None

    result = args[name]
    del args[name]

    if expand:
      result = sublime.expand_variables(result, self.window.extract_variables())
    return result

  def mutate_arguments(self, args):
    """Transfers custom arguments to basic ones.

    After executing 'args' shouldn't have anything custom.
    """
    pass

  def run_parameterized(self, input_string, args):
    """Called if enter was pressed in input panel.

    Will toggle normal build combining 'shell_cmd' argument from predefined
    'param_cmd' argument and input string. The latter will replace '$args'
    placeholder in the former.

    input_string: contains line from input panel.
    args: dictionary with arguments passed to parameterized build variant.
    """
    variables = self.window.extract_variables()
    input_string = sublime.expand_variables(input_string, variables)

    variables['args'] = input_string
    args['shell_cmd'] = sublime.expand_variables(self.extract_argument('param_cmd', args), variables)

    self.run(**args)

class PowershellExecCommand(SimpleExecCommand):
  def mutate_arguments(self, args):
    if "shell_cmd" in args:
      command = [self.extract_argument("shell_cmd", args)]
    elif "cmd" in args:
      command = args["cmd"]
    else:
      return

    context = self.extract_argument("context", args, expand=True)
    script = os.path.join(sublime.packages_path(), "Sublemon", "powershell_exec.ps1")

    cmd = ["powershell.exe", "-ExecutionPolicy", "Unrestricted"]

    if not self.extract_argument("load_profile", args):
      cmd.append("-NoProfile")

    cmd.extend(["-File", script])

    if context:
      cmd.extend(["-Context", context])

    cmd.append("-Command")
    cmd.extend(command)

    args["cmd"] = cmd
