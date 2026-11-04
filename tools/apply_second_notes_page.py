from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
page = root / 'index.html'
app = root / 'app.js'
sw = root / 'service-worker.js'
html = page.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')
cache = sw.read_text(encoding='utf-8')

def swap(old, new, label, count=1):
    global js
    if js.count(old) < count:
        raise SystemExit('Missing ' + label + ': ' + str(js.count(old)))
    js = js.replace(old, new, count)

# Duplicate the EXACT finished rich-text toolbars, including Word font sizes,
# text colors, list controls and paragraph spacing.
start = html.find('<section id="notesPage"')
end = html.find('<div id="eventModalBack"', start)
if start < 0 or end < 0: raise SystemExit('Notes page not found')
block = html[start:end]
def clone_card(css, old_code, new_code, title, subtitle, placeholder, new_css):
    pattern = r'<section class="notes-card '+css+r'">[\s\S]*?</section>'
    m = re.search(pattern, block)
    if not m: raise SystemExit('Missing notes card ' + old_code)
    card = m.group(0)
    card = card.replace('class="notes-card '+css+'"','class="notes-card '+new_css+'"',1)
    card = card.replace('data-note-course="'+old_code+'"','data-note-course="'+new_code+'"')
    card = card.replace('id="notes'+old_code+'"','id="notes'+new_code+'"')
    card = re.sub(r'<h3>.*?</h3>', '<h3>'+title+'</h3>', card, count=1)
    card = re.sub(r'<div class="notes-course">.*?</div>', '<div class="notes-course">'+subtitle+'</div>',card,count=1)
    card = re.sub(r'data-placeholder="[^"]*"', 'data-placeholder="'+placeholder+'"',card,count=1)
    return card
electronics = clone_card('et','ET4012','ELEKTRONIK','Elektronik','Elektronik','Skriv anteckningar för Elektronik här…','electronics')
computers = clone_card('ma','MA4026','DATORSYSTEM1','Datorsystemteknik I','Datorsystemteknik I','Skriv anteckningar för Datorsystemteknik I här…','computers')
if '<div class="notes-grid">' not in block: raise SystemExit('Notes grid missing')
block = block.replace('<div class="notes-grid">','<div id="notesOriginalGrid" class="notes-grid">',1)
end_grid = '    </div>\n  </div>\n</section>'
at = block.rfind(end_grid)
if at < 0: raise SystemExit('End of notes page not found')
new_grid = ('    </div>\n'
    '    <div id="notesSecondGrid" class="notes-grid hidden">\n'
    '      '+electronics+'\n'
    '      '+computers+'\n'
    '    </div>\n'
    '  </div>\n</section>')
block = block[:at] + new_grid + block[at+len(end_grid):]
title = '<h2>📝 Anteckningar</h2>'
if title not in block:raise SystemExit('Notes header missing')
tabs = (title +
    '<div class="notes-tabs" role="group" aria-label="Välj anteckningssida">'
    '<button type="button" id="notesOriginalTab" class="is-active" aria-pressed="true">Ellära · Transformer · Att göra</button>'
    '<button type="button" id="notesSecondTab" aria-pressed="false">Elektronik · Datorsystemteknik</button>'
    '</div>')
block=block.replace(title,tabs,1)
html=html[:start]+block+html[end:]

swap('const noteRanges={ET4012:null,MA4026:null,TODO:null};',
    'const noteRanges={ET4012:null,MA4026:null,TODO:null,ELEKTRONIK:null,DATORSYSTEM1:null};','note ranges')
swap("const ids={ET4012:'notesET4012',MA4026:'notesMA4026',TODO:'notesTODO'}",
    "const ids={ET4012:'notesET4012',MA4026:'notesMA4026',TODO:'notesTODO',ELEKTRONIK:'notesELEKTRONIK',DATORSYSTEM1:'notesDATORSYSTEM1'}",'editor resolver')
swap("const course=e.id==='notesET4012'?'ET4012':e.id==='notesMA4026'?'MA4026':'TODO';",
    "const course=({notesET4012:'ET4012',notesMA4026:'MA4026',notesTODO:'TODO',notesELEKTRONIK:'ELEKTRONIK',notesDATORSYSTEM1:'DATORSYSTEM1'})[e.id]||'TODO';",'editor event routing')
fill="normalizeSpacingBlocks($('notesTODO'))"
swap(fill,fill+
    ";$('notesELEKTRONIK').innerHTML=sanitizeNoteHtml(n.ELEKTRONIK||'')"+
    ";$('notesDATORSYSTEM1').innerHTML=sanitizeNoteHtml(n.DATORSYSTEM1||'')"+
    ";normalizeSpacingBlocks($('notesELEKTRONIK'));normalizeSpacingBlocks($('notesDATORSYSTEM1'))",'load editor content')
save="state.notes.TODO=sanitizeNoteHtml($('notesTODO').innerHTML)"
swap(save,save+";state.notes.ELEKTRONIK=sanitizeNoteHtml($('notesELEKTRONIK').innerHTML)"+
    ";state.notes.DATORSYSTEM1=sanitizeNoteHtml($('notesDATORSYSTEM1').innerHTML)",'save editor content')
sel="else if($('notesTODO').contains(node)){rememberNoteSelection('TODO');syncNoteToolbar('TODO')}"
swap(sel,sel+
    "\n  else if($('notesELEKTRONIK').contains(node)){rememberNoteSelection('ELEKTRONIK');syncNoteToolbar('ELEKTRONIK')}"+
    "\n  else if($('notesDATORSYSTEM1').contains(node)){rememberNoteSelection('DATORSYSTEM1');syncNoteToolbar('DATORSYSTEM1')}",'editor selection synchronization')
old_list="['ET4012','MA4026','TODO']"
new_list="['ET4012','MA4026','TODO','ELEKTRONIK','DATORSYSTEM1']"
if js.count(old_list)<3:raise SystemExit('Expected multiple toolbar lists')
js=js.replace(old_list,new_list)
swap("const pendingNoteFontSize={ET4012:null,MA4026:null,TODO:null};",
    "const pendingNoteFontSize={ET4012:null,MA4026:null,TODO:null,ELEKTRONIK:null,DATORSYSTEM1:null};",'pending typing size')

# No new storage schema: both texts go into state.notes, the same backing
# state that the existing Google Drive/JSON backup synchronizes.
js += r'''
function selectCourseNotesPage(second) {
  if (notesSaveTimer) commitNotesSave();
  $('notesOriginalGrid').classList.toggle('hidden', second);
  $('notesSecondGrid').classList.toggle('hidden', !second);
  $('notesOriginalTab').classList.toggle('is-active', !second);
  $('notesSecondTab').classList.toggle('is-active', second);
  $('notesOriginalTab').setAttribute('aria-pressed', String(!second));
  $('notesSecondTab').setAttribute('aria-pressed', String(second));
}
$('notesOriginalTab').addEventListener('click',()=>selectCourseNotesPage(false));
$('notesSecondTab').addEventListener('click',()=>selectCourseNotesPage(true));
'''
html=html.replace('</style>',r'''
.notes-tabs{display:flex;flex-wrap:wrap;gap:7px;margin-top:8px}
.notes-tabs button{background:#c6d9e5;color:#173047;border:1px solid #98b4c3;border-radius:9px;padding:8px 12px;font-weight:600}
.notes-tabs button.is-active{background:#174c68;color:#f5fcff;border-color:#197e9d}
.notes-card.electronics{border-top:4px solid #88b647}
.notes-card.computers{border-top:4px solid #f197c4}
'''+'</style>',1)
if 'studieplan-shell-v7' not in cache:raise SystemExit('Expected cache v7')
cache=cache.replace('studieplan-shell-v7','studieplan-shell-v8')
for key in ('notesELEKTRONIK','notesDATORSYSTEM1','notesSecondTab','state.notes.ELEKTRONIK','state.notes.DATORSYSTEM1'):
    if key not in html+js:raise SystemExit('Missing ' + key)
page.write_text(html,encoding='utf-8')
app.write_text(js,encoding='utf-8')
sw.write_text(cache,encoding='utf-8')
print('Second course notes page installed; existing notes preserved')
