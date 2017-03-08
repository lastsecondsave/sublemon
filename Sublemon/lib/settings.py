import hashlib
import os
import plistlib
import shutil

def cleanup():
    shutil.rmtree("generated", ignore_errors=True)
    os.mkdir("generated")

def entry(
        scope,
        increaseIndentPatterns=None, decreaseIndentPatterns=None,
        line_comment=None, line_comments=None, block_comment=None,
        symbolTransformations=None,
        **settings):
    if increaseIndentPatterns != None:
        settings['increaseIndentPattern'] = '|'.join(increaseIndentPatterns)

    if decreaseIndentPatterns != None:
        settings['decreaseIndentPattern'] = '|'.join(decreaseIndentPatterns)

    if symbolTransformations != None:
        settings['symbolTransformation'] = ';'.join(symbolTransformations) + ';'

    shell_vars = []
    comment_idx = 1

    def comment_spec(variant, value):
        return dict(
            name = 'TM_COMMENT_{}_{}'.format(variant, comment_idx),
            value = value
        )

    if line_comment != None:
        shell_vars.append(comment_spec('START', line_comment))
        comment_idx += 1

    if line_comments != None:
        for line_comment in line_comments:
            shell_vars.append(comment_spec('START', line_comment))
            comment_idx += 1

    if block_comment != None:
        shell_vars.append(comment_spec('START', block_comment[0]))
        shell_vars.append(comment_spec('END', block_comment[1]))
        comment_idx += 1

    if len(shell_vars) > 0:
        settings['shellVariables'] = shell_vars

    filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
    print("{}: {}".format(filename, scope))

    with open(os.path.join("generated", filename), "wb") as pfile:
        plistlib.dump(dict(scope=scope, settings=settings), pfile)
