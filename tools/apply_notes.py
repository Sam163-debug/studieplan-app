from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'

html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')

css_anchor = ".cloud-box{border:1px solid var(--line);border-radius:10px;padding:10px;background:#f8fafc;margin:7px 0 10px}"
notes_css = r'''
.notes-page{max-width:1500px;margin:14px auto;padding:0 14px 18px}.notes-shell{background:var(--panel);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:16px}.notes-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}.notes-head h2{font-size:20px;margin:0}.notes-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.notes-card{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fbfdff;min-width:0}.notes-card.et{border-top:4px solid #73edae}.notes-card.ma{border-top:4px solid #aa86fd}.notes-card h3{margin:0 0 4px;font-size:16px}.notes-course{font-size:12px;color:var(--muted);margin-bottom:9px}.notes-toolbar{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:8px;border:1px solid var(--line);border-bottom:0;border-radius:10px 10px 0 0;background:#f8fafc}.notes-toolbar button,.notes-toolbar select,.notes-toolbar input[type=color]{height:32px;border:1px solid #cbd5e1;background:#fff;border-radius:7px;padding:0 8px;color:var(--ink)}.notes-toolbar button{min-width:34px;font-weight:700;cursor:pointer}.notes-toolbar button:hover{background:#eef2ff}.notes-toolbar select{max-width:150px}.notes-color-wrap{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--muted)}.notes-toolbar input[type=color]{width:38px;padding:3px}.notes-editor{width:100%;min-height:54vh;border:1px solid var(--line);border-radius:0 0 10px 10px;padding:12px;background:#fff;color:var(--ink);line-height:1.5;overflow:auto;white-space:normal}.notes-editor:focus{outline:2px solid rgba(37,99,235,.16);border-color:#94a3b8}.notes-editor:empty:before{content:attr(data-placeholder);color:#94a3b8;pointer-events:none}.notes-editor h1{font-size:1.8em;margin:.55em 0 .3em}.notes-editor h2{font-size:1.45em;margin:.55em 0 .3em}.notes-editor h3{font-size:1.2em;margin:.5em 0 .25em}.notes-editor p{margin:.35em 0}.notes-save{font-size:12px;color:var(--muted);margin-top:8px}.notes-save.saved{color:var(--ok)}body.notes-mode main{display:none}body.notes-mode header .toolbar,body.notes-mode #addBtn{display:none}@media(max-width:850px){.notes-grid{grid-template-columns:1fr}.notes-editor{min-height:38vh}.notes-toolbar select{max-width:128px}}
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

def toolbar(course):
    return f'''<div class="notes-toolbar" data-note-course="{course}">
          <select data-note-action="format" aria-label="Textstil"><option value="p">Vanlig text</option><option value="h1">Rubrik 1</option><option value="h2">Rubrik 2</option><option value="h3">Rubrik 3</option></select>
          <button type="button" data-note-action="bold" title="Fetstil"><b>B</b></button>
          <button type="button" data-note-action="italic" title="Kursiv"><i>I</i></button>
          <button type="button" data-note-action="underline" title="Understruken"><u>U</u></button>
          <select data-note-action="font" aria-label="Typsnitt"><option value="system-ui">System</option><option value="Arial">Arial</option><option value="Georgia">Georgia</option><option value="Times New Roman">Times New Roman</option><option value="Verdana">Verdana</option><option value="Courier New">Courier New</option></select>
          <select data-note-action="size" aria-label="Textstorlek"><option value="12">12 px</option><option value="14">14 px</option><option value="16" selected>16 px</option><option value="18">18 px</option><option value="20">20 px</option><option value="24">24 px</option><option value="28">28 px</option><option value="32">32 px</option><option value="36">36 px</option></select>
          <select data-note-action="lineheight" aria-label="Radavstånd" title="Radavstånd"><option value="1">Rad 1,0</option><option value="1.15">Rad 1,15</option><option value="1.5" selected>Rad 1,5</option><option value="1.75">Rad 1,75</option><option value="2">Rad 2,0</option><option value="2.5">Rad 2,5</option><option value="3">Rad 3,0</option></select>
          <label class="notes-color-wrap">Färg <input type="color" data-note-action="color" value="#111827" aria-label="Textfärg"></label>
          <button type="button" data-note-action="ul" title="Punktlista">• Lista</button>
          <button type="button" data-note-action="ol" title="Numrerad lista">1. Lista</button>
        </div>'''

notes_page = f'''</main>

<section id="notesPage" class="notes-page hidden" aria-label="Kursanteckningar">
  <div class="notes-shell">
    <div class="notes-head"><button id="notesBackBtn">← Till schema</button><div><h2>📝 Anteckningar</h2><div class="hint">Markera text och använd verktygsfältet. Anteckningarna autosparas lokalt och följer med i JSON- och Drive-backupen.</div></div><span class="grow"></span><span id="notesSaveStatus" class="notes-save">Autosparande aktivt</span></div>
    <div class="notes-grid">
      <section class="notes-card et">
        <h3>Ellära</h3><div class="notes-course">ET4012 · Ellära med elektrisk mätteknik</div>
        {toolbar('ET4012')}
        <div id="notesET4012" class="notes-editor" contenteditable="true" spellcheck="true" data-placeholder="Skriv anteckningar för Ellära här…"></div>
      </section>
      <section class="notes-card ma">
        <h3>Transformer &amp; signaler</h3><div class="notes-course">MA4026 · Transformer, signaler och system</div>
        {toolbar('MA4026')}
        <div id="notesMA4026" class="notes-editor" contenteditable="true" spellcheck="true" data-placeholder="Skriv anteckningar för Transformer, signaler och system här…"></div>
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
normalize_repl = normalize_anchor + "x.notes=(x.notes&&typeof x.notes==='object')?x.notes:{};if(x.notesFormat!=='rich-html-v1'){const enc=v=>String(v||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');x.notes.ET4012=enc(typeof x.notes.ET4012==='string'?x.notes.ET4012:'');x.notes.MA4026=enc(typeof x.notes.MA4026==='string'?x.notes.MA4026:'');x.notesFormat='rich-html-v1'}else{x.notes.ET4012=typeof x.notes.ET4012==='string'?x.notes.ET4012:'';x.notes.MA4026=typeof x.notes.MA4026==='string'?x.notes.MA4026:'';}"
if "x.notesFormat!=='rich-html-v1'" not in js:
    if normalize_anchor not in js:
        raise SystemExit('Normalize anchor not found')
    js = js.replace(normalize_anchor, normalize_repl, 1)

insert_anchor = "function sourceLabel(e){return e.origin==='timeedit'?'TimeEdit':e.origin==='gym'?'Gym':e.origin==='plan'?'Studieplan':'Egen'}"
notes_js = r'''
let notesSaveTimer=null;
const noteRanges={ET4012:null,MA4026:null};
const noteBlockTags=new Set(['DIV','P','H1','H2','H3','LI']);
function noteEditor(course){return $(course==='ET4012'?'notesET4012':'notesMA4026')}
function sanitizeNoteHtml(html){
  const t=document.createElement('template');t.innerHTML=String(html||'');
  const allowed=new Set(['DIV','P','BR','B','STRONG','I','EM','U','H1','H2','H3','SPAN','UL','OL','LI']);
  const blocked=new Set(['SCRIPT','STYLE','IFRAME','OBJECT','EMBED','SVG','MATH','LINK','META']);
  const clean=node=>{
    [...node.children].forEach(el=>{
      clean(el);
      if(blocked.has(el.tagName)){el.remove();return}
      if(!allowed.has(el.tagName)){el.replaceWith(...el.childNodes);return}
      const keep={color:el.style.color,fontWeight:el.style.fontWeight,fontStyle:el.style.fontStyle,textDecoration:el.style.textDecoration,fontFamily:el.style.fontFamily,fontSize:el.style.fontSize,lineHeight:el.style.lineHeight};
      [...el.attributes].forEach(a=>el.removeAttribute(a.name));
      if(keep.color)el.style.color=keep.color;if(keep.fontWeight)el.style.fontWeight=keep.fontWeight;if(keep.fontStyle)el.style.fontStyle=keep.fontStyle;if(keep.textDecoration)el.style.textDecoration=keep.textDecoration;if(keep.fontFamily)el.style.fontFamily=keep.fontFamily;if(keep.fontSize)el.style.fontSize=keep.fontSize;if(keep.lineHeight)el.style.lineHeight=keep.lineHeight;
    })
  };clean(t.content);return t.innerHTML;
}
function fillNotes(){const n=state.notes||{ET4012:'',MA4026:''};$('notesET4012').innerHTML=sanitizeNoteHtml(n.ET4012||'');$('notesMA4026').innerHTML=sanitizeNoteHtml(n.MA4026||'')}
function rememberNoteSelection(course){const e=noteEditor(course),sel=getSelection();if(!e||!sel||!sel.rangeCount)return;const r=sel.getRangeAt(0);if(e.contains(r.commonAncestorContainer))noteRanges[course]=r.cloneRange()}
function restoreNoteSelection(course){const e=noteEditor(course),r=noteRanges[course];e.focus({preventScroll:true});if(r){const sel=getSelection();sel.removeAllRanges();sel.addRange(r)}}
function setNotesMode(open){document.body.classList.toggle('notes-mode',open);$('notesPage').classList.toggle('hidden',!open);$('notesBtn').textContent=open?'← Till schema':'📝 Anteckningar';if(open){fillNotes();setTimeout(()=>$('notesET4012').focus({preventScroll:true}),0)}}
function snapshotNotes(){state.notes=state.notes||{ET4012:'',MA4026:''};state.notesFormat='rich-html-v1';state.notes.ET4012=sanitizeNoteHtml($('notesET4012').innerHTML);state.notes.MA4026=sanitizeNoteHtml($('notesMA4026').innerHTML)}
function commitNotesSave(){clearTimeout(notesSaveTimer);notesSaveTimer=null;snapshotNotes();save();const s=$('notesSaveStatus');s.textContent='Autosparat '+new Date().toLocaleTimeString('sv-SE',{hour:'2-digit',minute:'2-digit'});s.classList.add('saved')}
function queueNotesSave(){snapshotNotes();const s=$('notesSaveStatus');s.textContent='Sparar…';s.classList.remove('saved');clearTimeout(notesSaveTimer);notesSaveTimer=setTimeout(commitNotesSave,650)}
function replaceSizeFonts(editor,px){editor.querySelectorAll('font[size="7"]').forEach(f=>{const s=document.createElement('span');s.style.fontSize=px+'px';while(f.firstChild)s.appendChild(f.firstChild);f.replaceWith(s)})}
function closestNoteBlock(node,editor){if(node&&node.nodeType===Node.TEXT_NODE)node=node.parentElement;while(node&&node!==editor&&!noteBlockTags.has(node.tagName))node=node.parentElement;return node&&node!==editor?node:null}
function applyNoteLineHeight(course,value){
  const editor=noteEditor(course),range=noteRanges[course];if(!editor)return;
  const blocks=new Set();
  if(range){
    const start=closestNoteBlock(range.startContainer,editor),end=closestNoteBlock(range.endContainer,editor);if(start)blocks.add(start);if(end)blocks.add(end);
    const walker=document.createTreeWalker(editor,NodeFilter.SHOW_ELEMENT,{acceptNode:n=>noteBlockTags.has(n.tagName)&&range.intersectsNode(n)?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_SKIP});let n;while((n=walker.nextNode()))blocks.add(n);
  }
  if(!blocks.size){const sel=getSelection();if(sel&&sel.rangeCount){const b=closestNoteBlock(sel.getRangeAt(0).startContainer,editor);if(b)blocks.add(b)}}
  if(!blocks.size){document.execCommand('formatBlock',false,'p');const sel=getSelection();if(sel&&sel.rangeCount){const b=closestNoteBlock(sel.getRangeAt(0).startContainer,editor);if(b)blocks.add(b)}}
  blocks.forEach(b=>b.style.lineHeight=String(value||1.5));
}
function applyNoteCommand(course,action,value){const e=noteEditor(course);restoreNoteSelection(course);try{document.execCommand('styleWithCSS',false,true)}catch(_){}
  if(action==='bold'||action==='italic'||action==='underline')document.execCommand(action,false,null);
  else if(action==='format')document.execCommand('formatBlock',false,value||'p');
  else if(action==='font')document.execCommand('fontName',false,value||'system-ui');
  else if(action==='color')document.execCommand('foreColor',false,value||'#111827');
  else if(action==='size'){try{document.execCommand('styleWithCSS',false,false)}catch(_){}document.execCommand('fontSize',false,'7');replaceSizeFonts(e,value||16)}
  else if(action==='lineheight')applyNoteLineHeight(course,value||1.5);
  else if(action==='ul')document.execCommand('insertUnorderedList',false,null);
  else if(action==='ol')document.execCommand('insertOrderedList',false,null);
  rememberNoteSelection(course);queueNotesSave();
}
function initNoteToolbar(){
  document.querySelectorAll('.notes-editor').forEach(e=>{const course=e.id==='notesET4012'?'ET4012':'MA4026';['keyup','mouseup','input','focus'].forEach(ev=>e.addEventListener(ev,()=>rememberNoteSelection(course)));e.addEventListener('input',queueNotesSave);e.addEventListener('blur',()=>{if(notesSaveTimer)commitNotesSave()})});
  document.querySelectorAll('.notes-toolbar').forEach(tb=>{const course=tb.dataset.noteCourse;tb.querySelectorAll('button[data-note-action]').forEach(b=>{b.addEventListener('mousedown',ev=>ev.preventDefault());b.addEventListener('click',()=>applyNoteCommand(course,b.dataset.noteAction,b.value))});tb.querySelectorAll('select[data-note-action],input[type=color][data-note-action]').forEach(c=>{c.addEventListener('focus',()=>rememberNoteSelection(course));c.addEventListener('change',()=>applyNoteCommand(course,c.dataset.noteAction,c.value))})});
}
'''.strip()
if 'function initNoteToolbar()' not in js:
    if insert_anchor not in js:
        raise SystemExit('JS function anchor not found')
    js = js.replace(insert_anchor, notes_js + '\n' + insert_anchor, 1)

handler_anchor = "$('manageCoursesBtn').onclick=openCourses;"
handlers = "$('notesBtn').onclick=()=>setNotesMode(!document.body.classList.contains('notes-mode'));$('notesBackBtn').onclick=()=>setNotesMode(false);window.addEventListener('pagehide',()=>{if(notesSaveTimer)commitNotesSave()});initNoteToolbar();\n"
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
print('Rich notes feature applied')
