from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'
html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')

old_control = '<select data-note-action="lineheight" aria-label="Radavstånd" title="Radavstånd"><option value="1">Rad 1,0</option><option value="1.15">Rad 1,15</option><option value="1.5" selected>Rad 1,5</option><option value="1.75">Rad 1,75</option><option value="2">Rad 2,0</option><option value="2.5">Rad 2,5</option><option value="3">Rad 3,0</option></select>'
new_control = '''<div class="notes-spacing-wrap" data-spacing-wrap>
            <button type="button" class="notes-spacing-toggle" data-spacing-toggle title="Radavstånd">↕ Radavstånd</button>
            <div class="notes-spacing-panel hidden" data-spacing-panel>
              <div class="notes-spacing-head"><strong>Radavstånd</strong><label><span>Automatiskt</span><input type="checkbox" data-spacing-auto checked></label></div>
              <div class="notes-spacing-adjust"><button type="button" data-spacing-minus aria-label="Minska radavstånd">−</button><input type="range" data-spacing-range min="6" max="120" step="0.01" value="18"><button type="button" data-spacing-plus aria-label="Öka radavstånd">+</button></div>
              <div class="notes-spacing-value"><input type="number" data-spacing-number min="6" max="120" step="0.01" value="18" inputmode="decimal"><span>pt</span></div>
              <div class="notes-spacing-hint">Markera text eller placera markören i ett stycke. Ändringen visas direkt.</div>
            </div>
          </div>'''
if old_control not in html:
    raise SystemExit('Old line spacing control not found')
html = html.replace(old_control, new_control)

style_anchor = '.notes-color-wrap{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--muted)}'
spacing_css = '''.notes-spacing-wrap{position:relative;display:inline-flex}.notes-spacing-toggle{font-weight:600!important;min-width:110px!important}.notes-spacing-panel{position:absolute;z-index:80;top:38px;left:0;width:300px;padding:12px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 36px rgba(15,23,42,.18)}.notes-spacing-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.notes-spacing-head label{display:flex;align-items:center;gap:7px;font-size:13px}.notes-spacing-adjust{display:grid;grid-template-columns:34px 1fr 34px;gap:8px;align-items:center}.notes-spacing-adjust button{min-width:34px!important;padding:0!important;font-size:19px}.notes-spacing-adjust input[type=range]{width:100%;accent-color:#2563eb}.notes-spacing-value{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:9px}.notes-spacing-value input{width:94px;height:32px;border:1px solid #cbd5e1;border-radius:7px;text-align:right;padding:0 8px}.notes-spacing-hint{margin-top:9px;font-size:11px;line-height:1.35;color:var(--muted)}.notes-spacing-panel input:disabled,.notes-spacing-panel button:disabled{opacity:.45;cursor:not-allowed}'''
if spacing_css not in html:
    if style_anchor not in html:
        raise SystemExit('Notes style anchor not found')
    html = html.replace(style_anchor, style_anchor + spacing_css, 1)

fill_old = "function fillNotes(){const n=state.notes||{ET4012:'',MA4026:''};$('notesET4012').innerHTML=sanitizeNoteHtml(n.ET4012||'');$('notesMA4026').innerHTML=sanitizeNoteHtml(n.MA4026||'')}"
fill_new = "function fillNotes(){const n=state.notes||{ET4012:'',MA4026:''};$('notesET4012').innerHTML=sanitizeNoteHtml(n.ET4012||'');$('notesMA4026').innerHTML=sanitizeNoteHtml(n.MA4026||'');normalizeSpacingBlocks($('notesET4012'));normalizeSpacingBlocks($('notesMA4026'))}"
if fill_old not in js:
    raise SystemExit('fillNotes anchor not found')
js = js.replace(fill_old, fill_new, 1)

insert_before = 'function fillNotes(){'
spacing_js = r'''
function normalizeSpacingBlocks(editor){
  if(!editor)return;
  const structural=new Set(['DIV','P','H1','H2','H3','UL','OL']);
  const nodes=[...editor.childNodes];
  if(!nodes.some(n=>n.nodeType===Node.TEXT_NODE||(n.nodeType===Node.ELEMENT_NODE&&n.tagName==='BR')))return;
  const out=document.createDocumentFragment();let line=document.createElement('div');let touched=false;
  const flush=(force=false)=>{if(line.childNodes.length||force){if(!line.childNodes.length)line.appendChild(document.createElement('br'));out.appendChild(line);line=document.createElement('div');touched=true}};
  nodes.forEach(n=>{if(n.nodeType===Node.ELEMENT_NODE&&structural.has(n.tagName)){flush();out.appendChild(n);touched=true}else if(n.nodeType===Node.ELEMENT_NODE&&n.tagName==='BR'){flush(true)}else line.appendChild(n)});
  flush();if(touched)editor.replaceChildren(out);
}
function spacingBlockFromNode(node,editor){if(node&&node.nodeType===Node.TEXT_NODE)node=node.parentElement;while(node&&node!==editor){if(noteBlockTags.has(node.tagName))return node;node=node.parentElement}return null}
function spacingBlocksForCourse(course){
  const editor=noteEditor(course),range=noteRanges[course];if(!editor||!range)return [];
  const blocks=new Set();
  if(range.collapsed){const b=spacingBlockFromNode(range.startContainer,editor);if(b)blocks.add(b)}else{
    editor.querySelectorAll('div,p,h1,h2,h3,li').forEach(b=>{try{if(range.intersectsNode(b))blocks.add(b)}catch(_){}});
  }
  if(!blocks.size){restoreNoteSelection(course);document.execCommand('formatBlock',false,'div');rememberNoteSelection(course);const r=noteRanges[course];if(r){const b=spacingBlockFromNode(r.startContainer,editor);if(b)blocks.add(b)}}
  return [...blocks];
}
function lineHeightPt(block){
  if(!block)return 18;
  const inline=block.style.lineHeight||'';if(inline.endsWith('pt'))return parseFloat(inline)||18;
  const cs=getComputedStyle(block),lh=parseFloat(cs.lineHeight),fs=parseFloat(cs.fontSize)||16;
  return Number.isFinite(lh)?lh*.75:fs*1.2*.75;
}
function clampSpacing(v){v=Number(v);if(!Number.isFinite(v))v=18;return Math.max(6,Math.min(120,Math.round(v*100)/100))}
function applyGoodnotesSpacing(course,auto,value){
  const blocks=spacingBlocksForCourse(course);if(!blocks.length)return;
  if(auto)blocks.forEach(b=>b.style.removeProperty('line-height'));else{const pt=clampSpacing(value);blocks.forEach(b=>b.style.lineHeight=pt+'pt')}
  queueNotesSave();
}
function setSpacingPanelState(panel,course){
  const blocks=spacingBlocksForCourse(course),first=blocks[0];
  const auto=blocks.length?blocks.every(b=>!b.style.lineHeight):true;
  const value=clampSpacing(lineHeightPt(first));
  const a=panel.querySelector('[data-spacing-auto]'),r=panel.querySelector('[data-spacing-range]'),n=panel.querySelector('[data-spacing-number]'),minus=panel.querySelector('[data-spacing-minus]'),plus=panel.querySelector('[data-spacing-plus]');
  a.checked=auto;r.value=value;n.value=value.toFixed(2);r.disabled=auto;n.disabled=auto;minus.disabled=auto;plus.disabled=auto;
}
function closeSpacingPanels(except=null){document.querySelectorAll('[data-spacing-panel]').forEach(p=>{if(p!==except)p.classList.add('hidden')})}
function initGoodnotesSpacing(){
  document.querySelectorAll('[data-spacing-wrap]').forEach(w=>{
    const toolbar=w.closest('.notes-toolbar'),course=toolbar.dataset.noteCourse,panel=w.querySelector('[data-spacing-panel]'),toggle=w.querySelector('[data-spacing-toggle]'),auto=w.querySelector('[data-spacing-auto]'),range=w.querySelector('[data-spacing-range]'),number=w.querySelector('[data-spacing-number]'),minus=w.querySelector('[data-spacing-minus]'),plus=w.querySelector('[data-spacing-plus]');
    toggle.addEventListener('mousedown',e=>{e.preventDefault();rememberNoteSelection(course)});
    toggle.addEventListener('click',e=>{e.stopPropagation();const willOpen=panel.classList.contains('hidden');closeSpacingPanels();if(willOpen){setSpacingPanelState(panel,course);panel.classList.remove('hidden')}});
    panel.addEventListener('mousedown',e=>e.stopPropagation());panel.addEventListener('click',e=>e.stopPropagation());
    const setManual=v=>{v=clampSpacing(v);auto.checked=false;range.disabled=false;number.disabled=false;minus.disabled=false;plus.disabled=false;range.value=v;number.value=v.toFixed(2);applyGoodnotesSpacing(course,false,v)};
    auto.addEventListener('change',()=>{if(auto.checked){applyGoodnotesSpacing(course,true);setSpacingPanelState(panel,course)}else setManual(number.value)});
    range.addEventListener('input',()=>setManual(range.value));
    number.addEventListener('change',()=>setManual(number.value));
    minus.addEventListener('click',()=>setManual(clampSpacing(Number(number.value)-0.01)));
    plus.addEventListener('click',()=>setManual(clampSpacing(Number(number.value)+0.01)));
  });
  document.addEventListener('click',()=>closeSpacingPanels());document.addEventListener('keydown',e=>{if(e.key==='Escape')closeSpacingPanels()});
}
'''.strip()
if 'function initGoodnotesSpacing()' not in js:
    if insert_before not in js:
        raise SystemExit('JS insertion anchor not found')
    js = js.replace(insert_before, spacing_js + '\n' + insert_before, 1)

init_anchor = 'initNoteToolbar();'
if 'initGoodnotesSpacing();' not in js:
    if init_anchor not in js:
        raise SystemExit('Toolbar init anchor not found')
    js = js.replace(init_anchor, init_anchor + 'initGoodnotesSpacing();', 1)

index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
print('Goodnotes-style line spacing applied')
