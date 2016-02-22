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
