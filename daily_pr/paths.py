import os.path

DIR_HTML, DIR_JSON, DIR_PICKLE = [
    os.path.join(os.path.dirname(__file__), x)
    for x in ('cached-html', 'parsed-json', 'pickle-cache')
]
