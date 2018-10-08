from Sublemon.chimney import ChimneyCommand


class PowershellCommand(ChimneyCommand):
    def preprocess_options(self, options):
        script = options['script']
        if script:
            options.shell_cmd = "&'{}'".format(script)
