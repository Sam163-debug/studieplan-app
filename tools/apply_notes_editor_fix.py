from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'

html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')

old_headings = '.notes-editor h1{font-size:1.8em;margin:.55em 0 .3em}.notes-editor h2{font-size:1.45em;margin:.55em 0 .3em}.notes-editor h3{font-size:1.2em;margin:.5em 0 .25em}'
new_headings = '.notes-editor h1,.notes-editor h1 *{font-size:32px!important}.notes-editor h1{margin:.55em 0 .3em}.notes-editor h2,.notes-editor h2 *{font-size:28px!important}.notes-editor h2{margin:.55em 0 .3em}.notes-editor h3,.notes-editor h3 *{font-size:24px!important}.notes-editor h3{margin:.5em 0 .25em}'
if old_headings not in html:
    raise SystemExit('Notes heading CSS anchor not found')
html = html.replace(old_headings, new_headings, 1)

toolbar_hover = '.notes-toolbar button:hover{background:#eef2ff}'
toolbar_state = '.notes-toolbar button.is-active{background:#e0e7ff;border-color:#818cf8;color:#312e81}.notes-toolbar select.is-active{border-color:#818cf8;box-shadow:0 0 0 1px #c7d2fe}'
if toolbar_state not in html:
    if toolbar_hover not in html:
        raise SystemExit('Toolbar CSS anchor not found')
    html = html.replace(toolbar_hover, toolbar_hover + toolbar_state, 1)

old_color_control = '<label class="notes-color-wrap">Färg <input type="color" data-note-action="color" value="#111827" aria-label="Textfärg"></label>'
new_color_control = '''<div class="notes-color-picker" data-note-color-picker>
            <button type="button" class="notes-color-toggle" data-note-color-toggle title="Textfärg" aria-label="Textfärg" aria-expanded="false">
              <span class="notes-color-letter">A</span><span class="notes-color-bar" data-note-color-bar style="background:#111827"></span><span class="notes-color-caret">▾</span>
            </button>
            <div class="notes-color-panel hidden" data-note-color-panel>
              <button type="button" class="notes-color-auto" data-note-color="#111827">Automatisk</button>
              <div class="notes-color-title">Temafärger</div>
              <div class="notes-color-grid notes-theme-grid" data-note-theme-colors></div>
              <div class="notes-color-title">Standardfärger</div>
              <div class="notes-color-grid notes-standard-grid" data-note-standard-colors></div>
              <label class="notes-color-more">Fler färger… <input type="color" data-note-custom-color value="#111827" aria-label="Fler textfärger"></label>
            </div>
          </div>'''
if old_color_control not in html:
    raise SystemExit('Notes color control anchor not found')
html = html.replace(old_color_control, new_color_control)

style_anchor = '.notes-color-wrap{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--muted)}'
color_css = '''.notes-color-picker{position:relative;display:inline-flex}.notes-color-toggle{min-width:48px!important;padding:3px 7px!important;display:grid;grid-template-columns:22px 10px;grid-template-rows:20px 4px;column-gap:3px;align-items:center}.notes-color-letter{grid-column:1;grid-row:1;font-size:17px;font-weight:700;line-height:18px}.notes-color-bar{grid-column:1;grid-row:2;width:22px;height:4px;border-radius:2px;background:#111827}.notes-color-caret{grid-column:2;grid-row:1/3;font-size:10px;color:#64748b}.notes-color-panel{position:absolute;z-index:90;top:38px;left:0;width:274px;padding:11px;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 14px 36px rgba(15,23,42,.2)}.notes-color-auto{width:100%;height:30px!important;text-align:left;font-weight:500!important;margin-bottom:8px}.notes-color-title{font-size:11px;font-weight:700;color:#475569;margin:7px 0 5px}.notes-color-grid{display:grid;grid-template-columns:repeat(10,22px);gap:3px}.notes-color-swatch{width:22px!important;height:22px!important;min-width:22px!important;padding:0!important;border-radius:2px!important;border:1px solid rgba(15,23,42,.22)!important}.notes-color-swatch:hover{outline:2px solid #2563eb;outline-offset:1px}.notes-color-swatch.is-active{outline:2px solid #111827;outline-offset:1px}.notes-color-more{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:10px;padding-top:9px;border-top:1px solid var(--line);font-size:12px;font-weight:600;color:#334155;cursor:pointer}.notes-color-more input[type=color]{width:42px;height:28px;padding:2px;border:1px solid #cbd5e1;border-radius:6px;background:#fff;cursor:pointer}'''
if color_css not in html:
    if style_anchor not in html:
        raise SystemExit('Notes color style anchor not found')
    html = html.replace(style_anchor, style_anchor + color_css, 1)

insert_anchor = "function sourceLabel(e){return e.origin==='timeedit'?'TimeEdit':e.origin==='gym'?'Gym':e.origin==='plan'?'Studieplan':'Egen'}"
sync_js = r'''
function noteSelectionElement(course){
  const editor=noteEditor(course),sel=getSelection();if(!editor)return null;
  let node=null;
  if(sel&&sel.rangeCount&&editor.contains(sel.getRangeAt(0).commonAncestorContainer))node=sel.focusNode||sel.anchorNode;
  else if(noteRanges[course])node=noteRanges[course].startContainer;
  if(node&&node.nodeType===Node.TEXT_NODE)node=node.parentElement;
  return node&&editor.contains(node)?node:null;
}
function noteCssColorToHex(color){
  if(!color)return '#111827';
  if(/^#[0-9a-f]{6}$/i.test(color))return color.toLowerCase();
  const m=String(color).match(/rgba?\(\s*(\d+)\D+(\d+)\D+(\d+)/i);
  if(!m)return '#111827';
  return '#'+[m[1],m[2],m[3]].map(v=>Math.max(0,Math.min(255,Number(v))).toString(16).padStart(2,'0')).join('');
}
function noteToolbarBlock(node,editor){
  while(node&&node!==editor){if(['P','DIV','H1','H2','H3','LI'].includes(node.tagName))return node;node=node.parentElement}
  return null;
}
function setNoteButtonState(button,on){
  if(!button)return;button.classList.toggle('is-active',!!on);button.setAttribute('aria-pressed',on?'true':'false');
}
function syncNoteColorUi(tb,hex){
  hex=String(hex||'#111827').toLowerCase();
  const bar=tb.querySelector('[data-note-color-bar]');if(bar)bar.style.background=hex;
  const custom=tb.querySelector('[data-note-custom-color]');if(custom)custom.value=hex;
  tb.querySelectorAll('[data-note-color]').forEach(b=>b.classList.toggle('is-active',String(b.dataset.noteColor||'').toLowerCase()===hex));
  tb.querySelectorAll('.notes-color-swatch').forEach(b=>b.classList.toggle('is-active',String(b.dataset.noteColor||'').toLowerCase()===hex));
}
function syncNoteToolbar(course){
  const editor=noteEditor(course),tb=document.querySelector('.notes-toolbar[data-note-course="'+course+'"]'),node=noteSelectionElement(course);
  if(!editor||!tb||!node)return;
  const block=noteToolbarBlock(node,editor),style=getComputedStyle(node),blockStyle=getComputedStyle(block||node);
  const format=tb.querySelector('[data-note-action="format"]');
  const tag=block&&['H1','H2','H3'].includes(block.tagName)?block.tagName.toLowerCase():'p';
  if(format){format.value=tag;format.classList.toggle('is-active',tag!=='p')}
  setNoteButtonState(tb.querySelector('[data-note-action="bold"]'),parseInt(style.fontWeight,10)>=600||style.fontWeight==='bold');
  setNoteButtonState(tb.querySelector('[data-note-action="italic"]'),style.fontStyle==='italic'||style.fontStyle==='oblique');
  setNoteButtonState(tb.querySelector('[data-note-action="underline"]'),String(style.textDecorationLine||style.textDecoration||'').includes('underline'));
  const ul=node.closest&&node.closest('ul'),ol=node.closest&&node.closest('ol');
  setNoteButtonState(tb.querySelector('[data-note-action="ul"]'),!!(ul&&editor.contains(ul)));
  setNoteButtonState(tb.querySelector('[data-note-action="ol"]'),!!(ol&&editor.contains(ol)));
  const size=tb.querySelector('[data-note-action="size"]'),px=Math.round(parseFloat(blockStyle.fontSize)||parseFloat(style.fontSize)||16);
  if(size){
    const opts=[...size.options],best=opts.reduce((a,o)=>Math.abs(Number(o.value)-px)<Math.abs(Number(a.value)-px)?o:a,opts[0]);
    if(best)size.value=best.value;
  }
  const font=tb.querySelector('[data-note-action="font"]');
  if(font){
    const family=String(style.fontFamily||'').toLowerCase().replace(/["']/g,'');
    const found=[...font.options].find(o=>family.split(',').map(x=>x.trim()).includes(o.value.toLowerCase())||family.includes(o.value.toLowerCase()));
    if(found)font.value=found.value;
  }
  syncNoteColorUi(tb,noteCssColorToHex(style.color));
  const panel=tb.querySelector('[data-spacing-panel]');if(panel&&!panel.classList.contains('hidden'))setSpacingPanelState(panel,course);
}
function syncActiveNoteToolbar(){
  const sel=getSelection();if(!sel||!sel.rangeCount)return;
  const node=sel.focusNode||sel.anchorNode;
  if($('notesET4012').contains(node)){rememberNoteSelection('ET4012');syncNoteToolbar('ET4012')}
  else if($('notesMA4026').contains(node)){rememberNoteSelection('MA4026');syncNoteToolbar('MA4026')}
}
function closeWordColorPanels(except=null){
  document.querySelectorAll('[data-note-color-panel]').forEach(p=>{if(p!==except){p.classList.add('hidden');const t=p.closest('[data-note-color-picker]')?.querySelector('[data-note-color-toggle]');if(t)t.setAttribute('aria-expanded','false')}})
}
function makeNoteColorSwatch(course,color){
  const b=document.createElement('button');b.type='button';b.className='notes-color-swatch';b.dataset.noteColor=color;b.style.background=color;b.title=color;b.setAttribute('aria-label','Textfärg '+color);
  b.addEventListener('mousedown',e=>{e.preventDefault();rememberNoteSelection(course)});
  b.addEventListener('click',e=>{e.stopPropagation();applyNoteCommand(course,'color',color);syncNoteColorUi(b.closest('.notes-toolbar'),color);closeWordColorPanels()});
  return b;
}
function initWordNoteColors(){
  const themeColumns=[
    ['#ffffff','#f2f2f2','#d9d9d9','#bfbfbf','#a6a6a6','#7f7f7f'],
    ['#000000','#7f7f7f','#595959','#3f3f3f','#262626','#0d0d0d'],
    ['#44546a','#d6dce4','#adb9ca','#8496b0','#323f4f','#222b35'],
    ['#e7e6e6','#f2f2f2','#d9d9d9','#b4b4b4','#8e8e8e','#595959'],
    ['#4472c4','#d9e2f3','#b4c6e7','#8eaadb','#2f5597','#203864'],
    ['#ed7d31','#fce4d6','#f8cbad','#f4b183','#c65911','#843c0c'],
    ['#a5a5a5','#ededed','#dbdbdb','#c9c9c9','#7b7b7b','#525252'],
    ['#ffc000','#fff2cc','#ffe699','#ffd966','#bf9000','#806000'],
    ['#5b9bd5','#ddebf7','#bdd7ee','#9dc3e6','#2e75b6','#1f4e79'],
    ['#70ad47','#e2f0d9','#c6e0b4','#a9d18e','#548235','#375623']
  ];
  const standard=['#c00000','#ff0000','#ffc000','#ffff00','#92d050','#00b050','#00b0f0','#0070c0','#002060','#7030a0'];
  document.querySelectorAll('[data-note-color-picker]').forEach(picker=>{
    const tb=picker.closest('.notes-toolbar'),course=tb.dataset.noteCourse,panel=picker.querySelector('[data-note-color-panel]'),toggle=picker.querySelector('[data-note-color-toggle]'),theme=picker.querySelector('[data-note-theme-colors]'),std=picker.querySelector('[data-note-standard-colors]'),auto=picker.querySelector('.notes-color-auto'),custom=picker.querySelector('[data-note-custom-color]');
    for(let shade=0;shade<6;shade++)themeColumns.forEach(col=>theme.appendChild(makeNoteColorSwatch(course,col[shade])));
    standard.forEach(color=>std.appendChild(makeNoteColorSwatch(course,color)));
    toggle.addEventListener('mousedown',e=>{e.preventDefault();rememberNoteSelection(course)});
    toggle.addEventListener('click',e=>{e.stopPropagation();const opening=panel.classList.contains('hidden');closeWordColorPanels();if(typeof closeSpacingPanels==='function')closeSpacingPanels();if(opening){panel.classList.remove('hidden');toggle.setAttribute('aria-expanded','true');syncNoteToolbar(course)}});
    panel.addEventListener('mousedown',e=>e.stopPropagation());panel.addEventListener('click',e=>e.stopPropagation());
    auto.addEventListener('mousedown',e=>{e.preventDefault();rememberNoteSelection(course)});
    auto.addEventListener('click',()=>{applyNoteCommand(course,'color','#111827');syncNoteColorUi(tb,'#111827');closeWordColorPanels()});
    custom.addEventListener('focus',()=>rememberNoteSelection(course));
    custom.addEventListener('change',()=>{applyNoteCommand(course,'color',custom.value);syncNoteColorUi(tb,custom.value);closeWordColorPanels()});
  });
  document.querySelectorAll('[data-spacing-toggle]').forEach(b=>b.addEventListener('click',()=>closeWordColorPanels()));
  document.addEventListener('click',()=>closeWordColorPanels());
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeWordColorPanels()});
}
function initNoteToolbarSync(){
  document.addEventListener('selectionchange',syncActiveNoteToolbar);
  ['ET4012','MA4026'].forEach(course=>{
    const editor=noteEditor(course),tb=document.querySelector('.notes-toolbar[data-note-course="'+course+'"]');
    ['keyup','mouseup','focus','input'].forEach(ev=>editor.addEventListener(ev,()=>syncNoteToolbar(course)));
    tb.addEventListener('click',()=>setTimeout(()=>syncNoteToolbar(course),0));
    tb.addEventListener('change',()=>setTimeout(()=>syncNoteToolbar(course),0));
  });
}
'''.strip()

if 'function initNoteToolbarSync()' not in js:
    if insert_anchor not in js:
        raise SystemExit('JS toolbar sync insertion anchor not found')
    js = js.replace(insert_anchor, sync_js + '\n' + insert_anchor, 1)

init_old = 'initNoteToolbar();initGoodnotesSpacing();'
init_new = 'initNoteToolbar();initGoodnotesSpacing();initWordNoteColors();initNoteToolbarSync();'
if init_new not in js:
    if init_old not in js:
        raise SystemExit('Notes toolbar initialization anchor not found')
    js = js.replace(init_old, init_new, 1)

index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
print('Notes editor heading sizes, Word color panel and toolbar sync applied')
