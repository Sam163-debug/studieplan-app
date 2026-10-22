from pathlib import Path
import re,sys
root=Path(sys.argv[1]);js=(root/'app.js').read_text(encoding='utf-8');html=(root/'index.html').read_text(encoding='utf-8')
for key in ['function normalizeState(', 'function openEdit(', 'function openAdd(', 'function saveModal(', 'function save(', 'function renderCalendarEnhanced(', "function renderList(", "function renderMobileView(", 'function initFeaturePack(', 'function openAddAt(']:
 i=js.find(key);print('====',key,'LOC',i,flush=True)
 if i>=0:print(js[i:i+4800],flush=True)
for key in ['id="fDescription"','id="fTitle"','id="saveBtn"','showCalendarDescriptions']:
 i=html.find(key);print('====HTML',key,i,html[max(0,i-700):i+1000],flush=True)
