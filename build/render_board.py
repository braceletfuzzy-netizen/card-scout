import json, os

# THE RENDER: the md-board = the HTML-page (the dark-theme = the machine-picks per the color-blind-law)
rows = [json.loads(l) for l in open('polyscout_v1_output.jsonl', encoding='utf-8')]
md = open('polyscout_board_v1.md', encoding='utf-8').read()
print('md-lines:', len(md))

css = """
body { background: #101418; color: #e8eaed; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; }
.container { max-width: 1100px; margin: 0 auto; }
h1 { color: #7fb069; font-size: 1.6em; border-bottom: 1px solid #333; padding-bottom: 10px; }
h2 { color: #a8c5d1; font-size: 1.25em; margin-top: 1.4em; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 0.95em; }
th { background: #1a2027; color: #a8c5d1; text-align: left; padding: 8px 12px; border-bottom: 2px solid #3a4552; }
td { padding: 7px 12px; border-bottom: 1px solid #232b34; vertical-align: top; }
tr:hover { background: #161c22; }
.legend { background: #141a20; border-left: 4px solid #7fb069; padding: 10px 14px; border-radius: 4px; font-size: 0.9em; margin: 14px 0; }
em { color: #9aa7b4; }
strong { color: #dee4ea; }
.footer { color: #6a7580; font-size: 0.85em; margin-top: 30px; border-top: 1px solid #2a333d; padding-top: 12px; }
"""

html = (
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>PolyScout v1 - NYC vs Memphis</title>\n'
    '<style>' + css + '</style>\n</head>\n<body><div class="container">\n'
    + md + '\n'
    + '<div class="footer">PolyScout v1 &middot; built 2026-11-20 &middot; study-phase instrument &middot; '
      'every number source-URL-verified &middot; nulls = sourced-absent, never fabricated &middot; launch-decision 2029</div>\n'
    '</div></body></html>'
)
open('polyscout_v1_board.html', 'w', encoding='utf-8').write(html)
print('wrote polyscout_v1_board.html:', os.path.getsize('polyscout_v1_board.html'), 'bytes')
