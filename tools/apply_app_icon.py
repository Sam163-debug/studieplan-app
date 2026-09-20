from pathlib import Path
import json, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
for name in ('favicon.png','app-icon-192.png'):
    src=Path(name)
    if not src.exists():
        raise SystemExit(f'{name} missing from repository root')
    shutil.copy2(src,root/name)

p=root/'index.html'
html=p.read_text(encoding='utf-8')
for old in ('favicon.png?v=1','favicon.png?v=2','app-icon-192.png?v=2'):
    html=html.replace(old,'__ICON_PLACEHOLDER__')
# Remove previous generated icon links before inserting the new set.
import re
html=re.sub(r'<link rel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>\n?','',html)
links='<link rel="icon" type="image/png" sizes="32x32" href="favicon.png?v=2">\n<link rel="shortcut icon" href="favicon.png?v=2">\n<link rel="apple-touch-icon" sizes="192x192" href="app-icon-192.png?v=2">\n'
marker='<title>Studieplan</title>\n'
if marker not in html:
    raise SystemExit('title anchor missing')
html=html.replace(marker,marker+links,1)
p.write_text(html,encoding='utf-8')

manifest=root/'manifest.webmanifest'
if manifest.exists():
    try:
        data=json.loads(manifest.read_text(encoding='utf-8'))
    except Exception:
        data={}
    data['icons']=[{'src':'app-icon-192.png?v=2','sizes':'192x192','type':'image/png','purpose':'any maskable'}]
    manifest.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

print('Updated full-frame app icon applied')
