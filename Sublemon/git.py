from Sublemon.chimney import ChimneyCommand

class GitDiffCommand(ChimneyCommand):
    def preprocess_options(self, options):
        options.shell_cmd = "git diff -- '{}'".format(self.var("file"))
        options.syntax = "Packages/Diff/Diff.tmLanguage"

class GitLogCommand(ChimneyCommand):
    def preprocess_options(self, options):
        options.shell_cmd = "git log -50 --follow --no-merges --format='{}' -- '{}'"\
                .format("%h %an → %s", self.var("file"))
        options.syntax = "Packages/Sublemon/git_spec/git_log.sublime-syntax"

class GitBlameCommand(ChimneyCommand):
    def preprocess_options(self, options):
        cmd = "git blame --date=short"
        view = self.window.active_view()
        sel = view.sel()[0]

        if not sel.empty():
            from_line = view.rowcol(sel.begin())[0] + 1
            to_line, to_col = view.rowcol(sel.end())
            if to_col > 0:
                to_line += 1

            cmd += " -L {},{}".format(from_line, to_line)

        options.shell_cmd = cmd + " -- '{}'".format(self.var("file"))
        options.syntax = "Packages/Sublemon/git_spec/git_blame.sublime-syntax"
