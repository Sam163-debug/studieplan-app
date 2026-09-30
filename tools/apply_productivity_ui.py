from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'
sw = root / 'service-worker.js'

html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')
sw_text = sw.read_text(encoding='utf-8')

# --- Third notes card: full width below the two course note cards. ---
if 'id="notesTODO"' not in html:
    m = re.search(r'(<section class="notes-card ma">.*?</section>)', html, re.S)
    if not m:
        raise SystemExit('Transformer notes card anchor not found')
    todo = m.group(1)
    todo = todo.replace('class="notes-card ma"', 'class="notes-card todo"', 1)
    todo = todo.replace('Transformer &amp; signaler', 'toDo-List &amp; kom ihåg', 1)
    todo = todo.replace('MA4026', 'TODO')
    todo = todo.replace('notesMA4026', 'notesTODO')
    todo = todo.replace('TODO · Transformer, signaler och system', 'Personlig lista')
    todo = todo.replace('Skriv anteckningar för Transformer, signaler och system här…', 'Skriv din toDo-lista och saker att komma ihåg här…')
    html = html[:m.end()] + '\n      ' + todo + html[m.end():]

# --- Compact sidebar/undo controls in the top bar. ---
if 'id="sidebarToggleBtn"' not in html:
    controls = '<button id="sidebarToggleBtn" class="header-icon-btn" type="button" title="Visa/dölj sidopanel" aria-label="Visa eller dölj sidopanel" aria-expanded="true">☰</button><button id="appUndoBtn" class="header-icon-btn" type="button" title="Ångra senaste ändringen (Ctrl+Z)" aria-label="Ångra senaste ändringen" disabled>↶</button>'
    if '</header>' not in html:
        raise SystemExit('Header close anchor not found')
    html = html.replace('</header>', controls + '</header>', 1)

# --- Visual refinement + remove explanatory clutter. ---
productivity_css = r'''
/* Productivity UI: compact controls, collapsible sidebar and cleaner surfaces. */
.header-icon-btn{width:38px;height:36px;padding:0!important;display:inline-grid;place-items:center;font-size:18px;line-height:1;border-radius:9px}
.header-icon-btn:disabled{opacity:.35;cursor:default}
main{transition:grid-template-columns .2s ease,gap .2s ease}
main>aside{min-width:0;transition:opacity .16s ease,padding .2s ease,border-color .2s ease}
body.sidebar-collapsed main{grid-template-columns:0 minmax(0,1fr);gap:0}
body.sidebar-collapsed main>aside{opacity:0;visibility:hidden;pointer-events:none;overflow:hidden;padding-left:0;padding-right:0;border-left-width:0;border-right-width:0}
body.sidebar-collapsed main>.content{min-width:0}
aside h2{margin:11px 0 7px;padding-bottom:5px;border-bottom:1px solid rgba(78,117,143,.18);letter-spacing:.01em}
.content{border-radius:16px}.calendar-wrap{border-radius:12px}.viewbar{padding:7px 9px}
.notes-shell{border-radius:16px}.notes-card{box-shadow:0 4px 14px rgba(29,65,89,.06)}
.notes-card.todo{grid-column:1/-1;border-top:4px solid #22c7df}
.notes-card.todo .notes-editor{min-height:32vh}
.notes-toolbar{gap:5px}
/* Keep the UI concise. Operational status/error text is intentionally retained. */
.hint,.first-run,.notes-spacing-hint{display:none!important}
@media(max-width:1100px){body.sidebar-collapsed main{grid-template-columns:1fr}body.sidebar-collapsed main>aside{display:none}}
'''.strip()
if '/* Productivity UI:' not in html:
    if '</style>' not in html:
        raise SystemExit('Style close anchor not found')
    html = html.replace('</style>', productivity_css + '\n</style>', 1)

# --- Teach the existing rich-note implementation about the third editor. ---
def replace_once(old, new, label):
    global js
    if old not in js:
        raise SystemExit(f'{label} anchor not found')
    js = js.replace(old, new, 1)

replace_once(
    'const noteRanges={ET4012:null,MA4026:null};',
    'const noteRanges={ET4012:null,MA4026:null,TODO:null};',
    'note ranges'
)
replace_once(
    "function noteEditor(course){return $(course==='ET4012'?'notesET4012':'notesMA4026')}",
    "function noteEditor(course){const ids={ET4012:'notesET4012',MA4026:'notesMA4026',TODO:'notesTODO'};return $(ids[course]||'notesET4012')}",
    'note editor resolver'
)

fill_pattern = r"function fillNotes\(\)\{.*?\}\nfunction rememberNoteSelection"
fill_repl = "function fillNotes(){const n=state.notes||{ET4012:'',MA4026:'',TODO:''};$('notesET4012').innerHTML=sanitizeNoteHtml(n.ET4012||'');$('notesMA4026').innerHTML=sanitizeNoteHtml(n.MA4026||'');$('notesTODO').innerHTML=sanitizeNoteHtml(n.TODO||'');normalizeSpacingBlocks($('notesET4012'));normalizeSpacingBlocks($('notesMA4026'));normalizeSpacingBlocks($('notesTODO'))}\nfunction rememberNoteSelection"
js, count = re.subn(fill_pattern, fill_repl, js, count=1, flags=re.S)
if count != 1:
    raise SystemExit('fillNotes anchor not found')

snapshot_pattern = r"function snapshotNotes\(\)\{.*?\}\nfunction commitNotesSave"
snapshot_repl = "function snapshotNotes(){state.notes=state.notes||{ET4012:'',MA4026:'',TODO:''};state.notesFormat='rich-html-v1';state.notes.ET4012=sanitizeNoteHtml($('notesET4012').innerHTML);state.notes.MA4026=sanitizeNoteHtml($('notesMA4026').innerHTML);state.notes.TODO=sanitizeNoteHtml($('notesTODO').innerHTML)}\nfunction commitNotesSave"
js, count = re.subn(snapshot_pattern, snapshot_repl, js, count=1, flags=re.S)
if count != 1:
    raise SystemExit('snapshotNotes anchor not found')

replace_once(
    "const course=e.id==='notesET4012'?'ET4012':'MA4026';",
    "const course=e.id==='notesET4012'?'ET4012':e.id==='notesMA4026'?'MA4026':'TODO';",
    'note toolbar course mapping'
)

sync_pattern = r"function syncActiveNoteToolbar\(\)\{.*?\}\nfunction closeWordColorPanels"
sync_repl = """function syncActiveNoteToolbar(){
  const sel=getSelection();if(!sel||!sel.rangeCount)return;
  const node=sel.focusNode||sel.anchorNode;
  if($('notesET4012').contains(node)){rememberNoteSelection('ET4012');syncNoteToolbar('ET4012')}
  else if($('notesMA4026').contains(node)){rememberNoteSelection('MA4026');syncNoteToolbar('MA4026')}
  else if($('notesTODO').contains(node)){rememberNoteSelection('TODO');syncNoteToolbar('TODO')}
}
function closeWordColorPanels"""
js, count = re.subn(sync_pattern, sync_repl, js, count=1, flags=re.S)
if count != 1:
    raise SystemExit('active note toolbar sync anchor not found')

if "['ET4012','MA4026'].forEach(course=>{" not in js:
    raise SystemExit('note toolbar sync course list anchor not found')
js = js.replace("['ET4012','MA4026'].forEach(course=>{", "['ET4012','MA4026','TODO'].forEach(course=>{", 1)

# --- Sidebar persistence + four-step application undo. ---
productivity_js = r'''
const SIDEBAR_COLLAPSE_KEY='studieplan-sidebar-collapsed-v1';
const APP_UNDO_LIMIT=4;
const appUndoHistory=[];
let appUndoApplying=false;
let appUndoLastCommitted=clone(state);
const appUndoBaseSave=save;
function appUndoComparable(value){
  const x=clone(value||{});delete x.notes;delete x.notesFormat;return JSON.stringify(x);
}
function updateAppUndoButton(){const b=$('appUndoBtn');if(b)b.disabled=appUndoHistory.length===0}
function setSidebarCollapsed(collapsed,persist=true){
  document.body.classList.toggle('sidebar-collapsed',!!collapsed);
  const b=$('sidebarToggleBtn');if(b){b.setAttribute('aria-expanded',collapsed?'false':'true');b.title=collapsed?'Visa sidopanel':'Dölj sidopanel'}
  if(persist){try{localStorage.setItem(SIDEBAR_COLLAPSE_KEY,collapsed?'1':'0')}catch(_){}}
}
function initSidebarCollapse(){
  let collapsed=false;try{collapsed=localStorage.getItem(SIDEBAR_COLLAPSE_KEY)==='1'}catch(_){}
  setSidebarCollapsed(collapsed,false);
  const b=$('sidebarToggleBtn');if(b)b.addEventListener('click',()=>setSidebarCollapsed(!document.body.classList.contains('sidebar-collapsed')));
}
function installAppUndo(){
  save=function(){
    const beforeSave=clone(state);
    if(!appUndoApplying&&appUndoComparable(beforeSave)!==appUndoComparable(appUndoLastCommitted)){
      appUndoHistory.push(clone(appUndoLastCommitted));
      if(appUndoHistory.length>APP_UNDO_LIMIT)appUndoHistory.shift();
    }
    const result=appUndoBaseSave();appUndoLastCommitted=clone(state);updateAppUndoButton();return result;
  };
}
function performAppUndo(){
  if(!appUndoHistory.length)return false;
  const modal=$('eventModalBack');if(modal&&!modal.classList.contains('hidden'))return false;
  const currentNotes=clone((state&&state.notes)||{}),currentNotesFormat=state&&state.notesFormat;
  const previous=clone(appUndoHistory.pop());
  Object.keys(state).forEach(k=>delete state[k]);Object.assign(state,previous);
  state.notes=currentNotes;if(currentNotesFormat)state.notesFormat=currentNotesFormat;
  appUndoApplying=true;
  try{appUndoBaseSave()}finally{appUndoApplying=false}
  appUndoLastCommitted=clone(state);
  render();
  if(document.body.classList.contains('notes-mode'))fillNotes();
  if(typeof unlockAllCourseNameInputs==='function')setTimeout(unlockAllCourseNameInputs,0);
  updateAppUndoButton();
  if(typeof toast==='function')toast('Senaste ändringen ångrades.');
  return true;
}
function initAppUndo(){
  installAppUndo();updateAppUndoButton();
  const b=$('appUndoBtn');if(b)b.addEventListener('click',performAppUndo);
  document.addEventListener('keydown',e=>{
    if(!(e.ctrlKey||e.metaKey)||e.shiftKey||String(e.key).toLowerCase()!=='z')return;
    const t=e.target,editable=t&&(t.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(t.tagName));
    if(editable)return;
    if(performAppUndo()){e.preventDefault();e.stopPropagation()}
  },true);
}
initSidebarCollapse();
initAppUndo();
'''.strip()
if 'const APP_UNDO_LIMIT=4;' not in js:
    js += '\n' + productivity_js + '\n'

# Force a service-worker refresh so the new shell is not hidden by an old cache.
if 'studieplan-shell-v2' in sw_text:
    sw_text = sw_text.replace('studieplan-shell-v2', 'studieplan-shell-v3')

index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
sw.write_text(sw_text, encoding='utf-8')
print('Productivity UI, four-step undo and third notes editor applied')
