import sys

sys.path.append("../lib")
import settings


def icon(name, *scopes):
    global icons
    for scope in scopes:
        icons.append({
            'scope': scope,
            'settings': {'icon': 'file_type_' + name}
        })


icons = []

icon('source',
     'source')

icon('text',
     'text',
     'text.html.markdown',
     'text.rfc',
     'text.restructuredtext')

icon('markup',
     'text.html',
     'source.xml',
     'source.json',
     'source.yaml')

icon('css',
     'source.css')

settings.setup()
for icon in icons:
    settings.generate_settings_file(icon['scope'], icon)
