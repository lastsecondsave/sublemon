from Sublemon.chimney import ChimneyCommand, Pipe


class GitDiffCommand(ChimneyCommand):
    def preprocess_options(self, options):
        options.shell_cmd = "git diff -- '{}'".format(self.source_file())
        options.syntax = "Packages/Diff/Diff.tmLanguage"


class GitLogPipe(Pipe):
    def __init__(self):
        self.lines = []
        self.max_padding = 0

    def output(self, line):
        self.lines.append(line)
        self.max_padding = max(line.find('→'), self.max_padding)

    def flush(self):
        for line in self.lines:
            padding = line.find('→')
            line = (line[:padding-1] +
                    ' ' * (self.max_padding - padding) +
                    line[padding-1:])
            self.next_pipe.output(line)
        self.next_pipe.flush()


class GitLogCommand(ChimneyCommand):
    def create_pipe(self, options):
        return GitLogPipe()

    def preprocess_options(self, options):
        template = "git log -50 --follow --no-merges --date=short --format='{}' -- '{}'"

        options.shell_cmd = template.format("%h %ad %an → %s", self.source_file())
        options.syntax = "Packages/Sublemon/git_spec/git_log.sublime-syntax"
        options.scroll_to_end = False


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

        options.shell_cmd = cmd + " -- '{}'".format(self.source_file())
        options.syntax = "Packages/Sublemon/git_spec/git_blame.sublime-syntax"
