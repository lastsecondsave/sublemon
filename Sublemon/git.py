import re

from Sublemon.chimney import ChimneyCommand, Pipe


class GitDiffCommand(ChimneyCommand):
    def preprocess_options(self, options):
        options.shell_cmd = "git diff -- '{}'".format(self.source_file())
        options.syntax = "Packages/Diff/Diff.tmLanguage"


class GitLogPipe(Pipe):
    LINE_PATTERN = re.compile(r'([0-9a-z]+) (\d{4}-\d{2}-\d{2}) (.*) → (.*)')

    def __init__(self):
        self.line_infos = []
        self.author_width = 0

    def output(self, line):
        m = self.LINE_PATTERN.match(line)
        if not m:
            return

        line_info = {
            'commit': m.group(1),
            'date': m.group(2),
            'author': m.group(3).strip(),
            'message': m.group(4)
        }

        self.line_infos.append(line_info)
        self.author_width = max(self.author_width, len(line_info['author']))

    def flush(self):
        for line_info in self.line_infos:
            line = ' '.join([line_info['commit'],
                             line_info['author'].ljust(self.author_width),
                             line_info['date'],
                             line_info['message']])
            self.next_pipe.output(line)

        self.next_pipe.flush()


class GitLogCommand(ChimneyCommand):
    def create_pipe(self, options):
        return GitLogPipe()

    def preprocess_options(self, options):
        template = "git log -200 --follow --no-merges --date=short --format='{}' -- '{}'"

        options.shell_cmd = template.format("%h %ad %an → %s", self.source_file())
        options.syntax = "Packages/Sublemon/git_spec/git_log.sublime-syntax"
        options.scroll_to_end = False


class GitBlamePipe(Pipe):
    LINE_PATTERN = re.compile(r'([0-9a-z]+) (.*?)\((.+?) (\d{4}-\d{2}-\d{2}) (\s*\d+)\) (.*)')

    def __init__(self):
        self.line_infos = []
        self.code_indent = 999
        self.author_width = 0

    def output(self, line):
        m = self.LINE_PATTERN.match(line)
        if not m:
            return

        line_info = {
            'commit': m.group(1),
            'author': m.group(3).strip(),
            'date': m.group(4),
            'line_number': m.group(5),
            'code': m.group(6),
            'not_committed': m.group(3) == 'Not Committed Yet'
        }

        self.line_infos.append(line_info)

        if line_info['code']:
            code = line_info['code']
            self.code_indent = min(self.code_indent, len(code) - len(code.lstrip()))

        if not line_info['not_committed']:
            self.author_width = max(self.author_width, len(line_info['author']))

    def flush(self):
        for line_info in self.line_infos:
            if not line_info['not_committed']:
                line = ' '.join([line_info['commit'],
                                 line_info['author'].ljust(self.author_width),
                                 line_info['date']])
            else:
                line = ' ' * (len(line_info['commit']) + self.author_width + 12)

            line += ' ' + line_info['line_number']
            if line_info['code']:
                line += ' ' + line_info['code'][self.code_indent:]

            self.next_pipe.output(line)

        self.next_pipe.flush()


class GitBlameCommand(ChimneyCommand):
    def create_pipe(self, options):
        return GitBlamePipe()

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
        options.scroll_to_end = False
