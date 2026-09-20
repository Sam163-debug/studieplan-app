from pathlib import Path
import shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
src=Path('favicon.png')
if not src.exists():
    raise SystemExit('favicon.png missing from repository root')
dst=root/'favicon.png'
shutil.copy2(src,dst)
p=root/'index.html'
html=p.read_text(encoding='utf-8')
links='<link rel="icon" type="image/png" sizes="32x32" href="favicon.png?v=1">\n<link rel="shortcut icon" href="favicon.png?v=1">\n<link rel="apple-touch-icon" href="favicon.png?v=1">\n'
if 'href="favicon.png?v=1"' not in html:
    marker='<title>Studieplan</title>\n'
    if marker not in html:
        raise SystemExit('title anchor missing')
    html=html.replace(marker,marker+links,1)
p.write_text(html,encoding='utf-8')
print('App favicon applied')
