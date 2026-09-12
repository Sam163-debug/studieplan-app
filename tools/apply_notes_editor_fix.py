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
  const color=tb.querySelector('[data-note-action="color"]');if(color)color.value=noteCssColorToHex(style.color);
  const panel=tb.querySelector('[data-spacing-panel]');if(panel&&!panel.classList.contains('hidden'))setSpacingPanelState(panel,course);
}
function syncActiveNoteToolbar(){
  const sel=getSelection();if(!sel||!sel.rangeCount)return;
  const node=sel.focusNode||sel.anchorNode;
  if($('notesET4012').contains(node)){rememberNoteSelection('ET4012');syncNoteToolbar('ET4012')}
  else if($('notesMA4026').contains(node)){rememberNoteSelection('MA4026');syncNoteToolbar('MA4026')}
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
init_new = 'initNoteToolbar();initGoodnotesSpacing();initNoteToolbarSync();'
if init_new not in js:
    if init_old not in js:
        raise SystemExit('Notes toolbar initialization anchor not found')
    js = js.replace(init_old, init_new, 1)

index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
print('Notes editor heading sizes and toolbar sync applied')
