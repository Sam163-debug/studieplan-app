from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
for name in ('cloud-sync.js','index.html'):
    p=root/name
    s=p.read_text(encoding='utf-8')
    print(f'===== {name} =====')
    markers=['tryAutoReconnect','requestAccessToken','initTokenClient','google.accounts.oauth2','GOOGLE_SCOPES','googleBtn','syncBtn','connectGoogle','disconnectGoogle','statusText','cloudStatus']
    seen=set()
    for marker in markers:
        for m in re.finditer(re.escape(marker),s):
            start=max(0,m.start()-900); end=min(len(s),m.end()+1800)
            key=(start,end)
            if key in seen: continue
            seen.add(key)
            print(f'--- {marker} @ {m.start()} ---')
            print(s[start:end])
            print()
