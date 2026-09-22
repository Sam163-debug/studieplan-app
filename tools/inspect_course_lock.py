from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else '.')/'app.js'
s=p.read_text(encoding='utf-8')
for marker in ['openCourses','courseRows','locked','readOnly','readonly','disabled','course-row','categories']:
    print('===== '+marker+' =====')
    for m in list(re.finditer(re.escape(marker),s,re.I))[:12]:
        print(s[max(0,m.start()-900):min(len(s),m.end()+1800)])
        print()
