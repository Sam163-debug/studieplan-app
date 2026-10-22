from pathlib import Path
import re,sys
js=(Path(sys.argv[1])/'app.js').read_text(encoding='utf-8')
print('=== APP SOURCE SIZE ===',len(js),flush=True)
keys=['let week','const week','weekStart','weekOffset','currentWeek','startOfWeek','weekMonday','monday','viewDate','gotoDate','prevWeek','nextWeek','planStart','function renderCalendar','function renderCalendarEnhanced','function render()','function load()','load();render();','description','e.desc','ev.desc','event-desc','event-description','innerHTML','function renderStats']
for key in keys:
  print('\n=== '+key+' ===',flush=True)
  all_matches=list(re.finditer(re.escape(key),js,re.I))
  print('count',len(all_matches),flush=True)
  for m in all_matches[:6]:
    print(js[max(0,m.start()-280):min(len(js),m.end()+950)].replace('\n','\\n'),flush=True)
