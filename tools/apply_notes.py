from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'

html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')

css_anchor = ".cloud-box{border:1px solid var(--line);border-radius:10px;padding:10px;background:#f8fafc;margin:7px 0 10px}"
notes_css = r'''
.notes-page{max-width:1500px;margin:14px auto;padding:0 14px 18px}.notes-shell{background:var(--panel);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:16px}.notes-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}.notes-head h2{font-size:20px;margin:0}.notes-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.notes-card{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fbfdff;min-width:0}.notes-card.et{border-top:4px solid #73edae}.notes-card.ma{border-top:4px solid #aa86fd}.notes-card h3{margin:0 0 4px;font-size:16px}.notes-course{font-size:12px;color:var(--muted);margin-bottom:9px}.notes-card textarea{width:100%;min-height:54vh;resize:vertical;border:1px solid var(--line);border-radius:10px;padding:12px;background:#fff;color:var(--ink);line-height:1.5}.notes-card textarea:focus{outline:2px solid rgba(37,99,235,.16);border-color:#94a3b8}.notes-save{font-size:12px;color:var(--muted);margin-top:8px}.notes-save.saved{color:var(--ok)}body.notes-mode main{display:none}body.notes-mode header .toolbar,body.notes-mode #addBtn{display:none}@media(max-width:850px){.notes-grid{grid-template-columns:1fr}.notes-card textarea{min-height:38vh}}
'''.strip()
if '.notes-page{' not in html:
    if css_anchor not in html:
        raise SystemExit('CSS anchor not found')
    html = html.replace(css_anchor, notes_css + '\n' + css_anchor, 1)

header_anchor = '<div class="grow"></div><span id="saveStatus" class="statusbar">Lokalt autosparande aktivt</span><button class="primary" id="addBtn">+ Lägg till aktivitet</button>'
header_repl = '<div class="grow"></div><span id="saveStatus" class="statusbar">Lokalt autosparande aktivt</span><button id="notesBtn">📝 Anteckningar</button><button class="primary" id="addBtn">+ Lägg till aktivitet</button>'
if 'id="notesBtn"' not in html:
    if header_anchor not in html:
        raise SystemExit('Header anchor not found')
    html = html.replace(header_anchor, header_repl, 1)

main_close = '</main>\n\n<div id="eventModalBack"'
notes_page = r'''</main>

<section id="notesPage" class="notes-page hidden" aria-label="Kursanteckningar">
  <div class="notes-shell">
    <div class="notes-head"><button id="notesBackBtn">← Till schema</button><div><h2>📝 Anteckningar</h2><div class="hint">Anteckningarna autosparas lokalt och följer med i JSON- och Drive-backupen.</div></div><span class="grow"></span><span id="notesSaveStatus" class="notes-save">Autosparande aktivt</span></div>
    <div class="notes-grid">
      <section class="notes-card et">
        <h3>Ellära</h3><div class="notes-course">ET4012 · Ellära med elektrisk mätteknik</div>
        <textarea id="notesET4012" spellcheck="true" placeholder="Skriv anteckningar för Ellära här…"></textarea>
      </section>
      <section class="notes-card ma">
        <h3>Transformer &amp; signaler</h3><div class="notes-course">MA4026 · Transformer, signaler och system</div>
        <textarea id="notesMA4026" spellcheck="true" placeholder="Skriv anteckningar för Transformer, signaler och system här…"></textarea>
      </section>
    </div>
  </div>
</section>

<div id="eventModalBack"'''
if 'id="notesPage"' not in html:
    if main_close not in html:
        raise SystemExit('Main close anchor not found')
    html = html.replace(main_close, notes_page, 1)

normalize_anchor = "const x=clone(s||INITIAL_STATE);x.schema=4;x.categories=Array.isArray(x.categories)?x.categories:[];x.events=Array.isArray(x.events)?x.events:[];"
normalize_repl = normalize_anchor + "x.notes=(x.notes&&typeof x.notes==='object')?x.notes:{};x.notes.ET4012=typeof x.notes.ET4012==='string'?x.notes.ET4012:'';x.notes.MA4026=typeof x.notes.MA4026==='string'?x.notes.MA4026:'';"
if "x.notes.ET4012" not in js:
    if normalize_anchor not in js:
        raise SystemExit('Normalize anchor not found')
    js = js.replace(normalize_anchor, normalize_repl, 1)

insert_anchor = "function sourceLabel(e){return e.origin==='timeedit'?'TimeEdit':e.origin==='gym'?'Gym':e.origin==='plan'?'Studieplan':'Egen'}"
notes_js = r'''
let notesSaveTimer=null;
function fillNotes(){const n=state.notes||{ET4012:'',MA4026:''};$('notesET4012').value=n.ET4012||'';$('notesMA4026').value=n.MA4026||''}
function setNotesMode(open){document.body.classList.toggle('notes-mode',open);$('notesPage').classList.toggle('hidden',!open);$('notesBtn').textContent=open?'← Till schema':'📝 Anteckningar';if(open){fillNotes();setTimeout(()=>$('notesET4012').focus({preventScroll:true}),0)}}
function commitNotesSave(){clearTimeout(notesSaveTimer);notesSaveTimer=null;state.notes=state.notes||{ET4012:'',MA4026:''};state.notes.ET4012=$('notesET4012').value;state.notes.MA4026=$('notesMA4026').value;save();const s=$('notesSaveStatus');s.textContent='Autosparat '+new Date().toLocaleTimeString('sv-SE',{hour:'2-digit',minute:'2-digit'});s.classList.add('saved')}
function queueNotesSave(){state.notes=state.notes||{ET4012:'',MA4026:''};state.notes.ET4012=$('notesET4012').value;state.notes.MA4026=$('notesMA4026').value;const s=$('notesSaveStatus');s.textContent='Sparar…';s.classList.remove('saved');clearTimeout(notesSaveTimer);notesSaveTimer=setTimeout(commitNotesSave,650)}
'''.strip()
if 'function queueNotesSave()' not in js:
    if insert_anchor not in js:
        raise SystemExit('JS function anchor not found')
    js = js.replace(insert_anchor, notes_js + '\n' + insert_anchor, 1)

handler_anchor = "$('manageCoursesBtn').onclick=openCourses;"
handlers = "$('notesBtn').onclick=()=>setNotesMode(!document.body.classList.contains('notes-mode'));$('notesBackBtn').onclick=()=>setNotesMode(false);$('notesET4012').addEventListener('input',queueNotesSave);$('notesMA4026').addEventListener('input',queueNotesSave);$('notesET4012').addEventListener('blur',()=>{if(notesSaveTimer)commitNotesSave()});$('notesMA4026').addEventListener('blur',()=>{if(notesSaveTimer)commitNotesSave()});window.addEventListener('pagehide',()=>{if(notesSaveTimer)commitNotesSave()});\n"
if "$('notesBtn').onclick" not in js:
    if handler_anchor not in js:
        raise SystemExit('Handler anchor not found')
    js = js.replace(handler_anchor, handlers + handler_anchor, 1)

load_anchor = 'load();render();'
if 'load();render();fillNotes();' not in js:
    if load_anchor not in js:
        raise SystemExit('Load anchor not found')
    js = js.replace(load_anchor, 'load();render();fillNotes();', 1)

index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
print('Notes feature applied')
