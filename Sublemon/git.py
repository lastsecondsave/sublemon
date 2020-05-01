import re

from .chimney import ChimneyBuildListener, ChimneyCommand


class GitDiffCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append('git', 'diff', build.active_file)
        build.syntax = "Packages/Diff/Diff.tmLanguage"


class GitLogCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append('git', 'log', '-200', '--follow', '--no-merges',
                       '--date=short', '--format=%h %ad %an → %s',
                       '--', build.active_file)
        build.listener = GitLogBuildListener()
        build.syntax = "git_log"


class GitLogBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(r'([0-9a-z]+) (\d{4}-\d{2}-\d{2}) (.*) → (.*)')

    def __init__(self):
        self.line_infos = []
        self.author_width = 0

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if not match:
            return

        line_info = {
            'commit': match.group(1),
            'date': match.group(2),
            'author': match.group(3).strip(),
            'message': match.group(4)
        }

        self.line_infos.append(line_info)
        self.author_width = max(self.author_width, len(line_info['author']))

    def on_complete(self, ctx):
        for line_info in reversed(self.line_infos):
            line = ' '.join([line_info['date'],
                             line_info['author'].ljust(self.author_width),
                             line_info['commit'],
                             line_info['message']])
            ctx.print(line)

        if self.line_infos:
            ctx.window.status_message('Last edited at ' + self.line_infos[0]['date'])


class GitBlameCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append('git', 'blame', '--date=short')

        view = self.window.active_view()
        sel = view.sel()[0]

        if not sel.empty():
            from_line = view.rowcol(sel.begin())[0] + 1
            to_line, to_col = view.rowcol(sel.end())
            if to_col > 0:
                to_line += 1

            build.cmd.append('-L', '{},{}'.format(from_line, to_line))

        build.cmd.append('--', build.active_file)
        build.syntax = "git_blame"
        build.listener = GitBlameBuildListener()


class GitBlameBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(r'([0-9a-z]+) (.*?)\((.+?) (\d{4}-\d{2}-\d{2}) (\s*\d+)\) (.*)')

    def __init__(self):
        self.line_infos = []
        self.code_indent = 999
        self.author_width = 0

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if not match:
            return

        line_info = {
            'commit': match.group(1),
            'author': match.group(3).strip(),
            'date': match.group(4),
            'line_number': match.group(5),
            'code': match.group(6),
            'not_committed': match.group(3) == 'Not Committed Yet'
        }

        self.line_infos.append(line_info)

        if line_info['code']:
            code = line_info['code']
            self.code_indent = min(self.code_indent, len(code) - len(code.lstrip()))

        if not line_info['not_committed']:
            self.author_width = max(self.author_width, len(line_info['author']))

    def on_complete(self, ctx):
        for line_info in self.line_infos:
            if not line_info['not_committed']:
                line = ' '.join([line_info['date'],
                                 line_info['author'].ljust(self.author_width),
                                 line_info['commit']])
            else:
                line = ' ' * (len(line_info['commit']) + self.author_width + 12)

            line += '   ' + line_info['line_number']
            if line_info['code']:
                line += ' ' + line_info['code'][self.code_indent:]

            ctx.print(line)
