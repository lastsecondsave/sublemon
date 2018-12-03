import re

from Sublemon.chimney import ChimneyCommand, ChimneyCommandListener


class PylintCommand(ChimneyCommand):
    def preprocess_options(self, options):
        cmd = ['python', '-m', 'pylint', options.source_file]

        if options['disable']:
            cmd.append('--disable=' + ','.join(options['disable']))

        options.shell_cmd = ' '.join(cmd)
        options.file_regex = r'(.+?):(\d+):(\d+): (.*)'
        options.syntax = 'Packages/Sublemon/python_spec/pylint.sublime-syntax'

    def get_listener(self):
        return PylintCommandListener()


class PylintCommandListener(ChimneyCommandListener):
    LINE_PATTERN = re.compile(r'(.+:\d+:)(\d+)(: .*)')

    def __init__(self):
        self.rank = None

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if match:
            col = int(match.group(2)) + 1
            line = match.group(1) + str(col) + match.group(3)

        if line.startswith('Your code has been rated at'):
            self.rank = line

        ctx.print(line)

    def on_complete(self, ctx):
        if self.rank:
            ctx.window.status_message(self.rank)
