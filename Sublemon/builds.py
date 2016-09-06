from Sublemon.chimney import Pipe, ChimneyCommand

import os

class PowershellCommand(ChimneyCommand):
    def preprocess_options(self, options, variables):
        script = options["script"]
        if script:
            if not os.path.isabs(script):
                script = os.path.join(variables["folder"], script)
            options.shell_cmd = "&'{}'".format(script)
