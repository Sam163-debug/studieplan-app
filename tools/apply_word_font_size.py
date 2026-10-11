from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
index=root/'index.html'
app=root/'app.js'
sw=root/'service-worker.js'

html=index.read_text(encoding='utf-8')
js=app.read_text(encoding='utf-8')
sw_text=sw.read_text(encoding='utf-8')

# Replace the old fixed size dropdown in every notes toolbar, including TODO.
old_size_re=r'<select data-note-action="size" aria-label="Textstorlek">.*?</select>'
word_size='''<div class="notes-size-control" data-note-size-control>
            <button type="button" class="notes-size-step notes-size-down" data-note-size-step="-1" title="Minska textstorlek" aria-label="Minska textstorlek">A−</button>
            <input type="number" class="notes-size-value" data-note-size-value min="8" max="96" step="1" value="16" inputmode="numeric" aria-label="Textstorlek i pixlar" title="Textstorlek">
            <button type="button" class="notes-size-step notes-size-up" data-note-size-step="1" title="Öka textstorlek" aria-label="Öka textstorlek">A+</button>
          </div>'''
html,count=re.subn(old_size_re,word_size,html,flags=re.S)
if count < 3:
    raise SystemExit(f'Expected at least 3 note size controls, replaced {count}')

# Heading defaults should not force every descendant to the heading size.
old_head='.notes-editor h1,.notes-editor h1 *{font-size:32px!important}.notes-editor h1{margin:.55em 0 .3em}.notes-editor h2,.notes-editor h2 *{font-size:28px!important}.notes-editor h2{margin:.55em 0 .3em}.notes-editor h3,.notes-editor h3 *{font-size:24px!important}.notes-editor h3{margin:.5em 0 .25em}'
new_head='.notes-editor h1{font-size:32px!important;margin:.55em 0 .3em}.notes-editor h2{font-size:28px!important;margin:.55em 0 .3em}.notes-editor h3{font-size:24px!important;margin:.5em 0 .25em}.notes-editor h1 span[style*="font-size"],.notes-editor h2 span[style*="font-size"],.notes-editor h3 span[style*="font-size"]{font-size:var(--note-inline-size,inherit)}'
if old_head not in html:
    raise SystemExit('Generated note heading CSS anchor not found')
html=html.replace(old_head,new_head,1)

size_css=r'''
/* Word-like font size control: three non-overlapping fixed-width segments. */
.notes-toolbar .notes-size-control{
  box-sizing:border-box;display:inline-grid;grid-template-columns:38px 54px 38px;
  align-items:stretch;flex:0 0 130px;width:130px;min-width:130px;
  height:34px;margin:0;border:1px solid #91afc0;border-radius:8px;
  overflow:hidden;background:#d5e5ee;vertical-align:middle;
}
.notes-toolbar .notes-size-control:focus-within{border-color:#4fa5c1;box-shadow:0 0 0 2px rgba(34,199,223,.16)}
.notes-toolbar .notes-size-control button.notes-size-step{
  box-sizing:border-box!important;display:grid!important;place-items:center!important;
  width:38px!important;min-width:38px!important;max-width:38px!important;
  height:32px!important;min-height:32px!important;margin:0!important;padding:0!important;
  border:0!important;border-radius:0!important;background:#c9dce8!important;
  color:#18364f!important;font-size:14px!important;font-weight:700!important;
  line-height:1!important;box-shadow:none!important;
}
.notes-toolbar .notes-size-control button.notes-size-step:hover{background:#afd0e1!important}
.notes-toolbar .notes-size-control input.notes-size-value{
  box-sizing:border-box!important;display:block!important;
  width:54px!important;min-width:54px!important;max-width:54px!important;
  height:32px!important;min-height:32px!important;margin:0!important;
  padding:0 3px!important;border:0!important;border-left:1px solid #a5bbc8!important;
  border-right:1px solid #a5bbc8!important;border-radius:0!important;
  background:#e6f0f5!important;color:#173047!important;font-size:14px!important;
  font-weight:600!important;line-height:32px!important;text-align:center!important;
  font-variant-numeric:tabular-nums;box-shadow:none!important;outline:0!important;
  appearance:textfield!important;-moz-appearance:textfield!important;
}
.notes-toolbar .notes-size-control input.notes-size-value::-webkit-inner-spin-button,
.notes-toolbar .notes-size-control input.notes-size-value::-webkit-outer-spin-button{-webkit-appearance:none;margin:0}
.notes-toolbar .notes-size-control input.notes-size-value:focus{background:#f0f6f9!important}
'''.strip()
if '/* Word-like font size control */' not in html:
    html=html.replace('</style>',size_css+'\n</style>',1)

word_js=r'''
const NOTE_FONT_SIZES=[8,9,10,11,12,14,16,18,20,22,24,26,28,32,36,40,44,48,54,60,72,80,96];
const pendingNoteFontSize={ET4012:null,MA4026:null,TODO:null};
function clampNoteFontSize(value){
  value=Math.round(Number(value)||16);return Math.max(8,Math.min(96,value));
}
function currentNoteFontSize(course){
  const editor=noteEditor(course),sel=getSelection();
  if(!editor)return 16;
  const active=sel&&sel.rangeCount&&editor.contains(sel.getRangeAt(0).commonAncestorContainer)
    ?sel.getRangeAt(0):noteRanges[course];
  let node=active&&active.startContainer;
  if(node&&node.nodeType===Node.ELEMENT_NODE&&node.childNodes.length){
    node=node.childNodes[Math.min(active.startOffset,node.childNodes.length-1)]||node;
    while(node&&node.firstChild)node=node.firstChild;
  }
  if(node&&node.nodeType===Node.TEXT_NODE)node=node.parentElement;
  if(!node||!editor.contains(node))node=editor;
  return clampNoteFontSize(parseFloat(getComputedStyle(node).fontSize)||16);
}
function setNoteSizeUi(course,value){
  const tb=document.querySelector('.notes-toolbar[data-note-course="'+course+'"]');
  const input=tb&&tb.querySelector('[data-note-size-value]');
  if(input&&document.activeElement!==input)input.value=String(clampNoteFontSize(value));
}
function normalizePendingNoteFont(editor,px){
  if(!editor)return;
  editor.querySelectorAll('font[size="7"]').forEach(f=>{
    const span=document.createElement('span');
    span.style.fontSize=clampNoteFontSize(px)+'px';
    while(f.firstChild)span.appendChild(f.firstChild);
    f.replaceWith(span);
  });
}
// Save logical text offsets, not DOM nodes: execCommand replaces inline nodes.
function noteTextBoundaryOffset(editor,container,offset){
  const r=document.createRange();
  r.selectNodeContents(editor);r.setEnd(container,offset);
  return r.cloneContents().textContent.length;
}
function noteSelectionOffsets(editor,range){
  if(!range||range.collapsed||!editor.contains(range.commonAncestorContainer))return null;
  return {
    start:noteTextBoundaryOffset(editor,range.startContainer,range.startOffset),
    end:noteTextBoundaryOffset(editor,range.endContainer,range.endOffset)
  };
}
function notePointAtTextOffset(editor,offset){
  let rest=Math.max(0,offset),last=null;
  const walker=document.createTreeWalker(editor,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    last=node;
    if(rest<=node.length)return {node,offset:rest};
    rest-=node.length;
  }
  return last?{node:last,offset:last.length}:{node:editor,offset:0};
}
function restoreNoteTextSelection(course,positions){
  const editor=noteEditor(course);
  if(!editor||!positions)return false;
  const start=notePointAtTextOffset(editor,positions.start);
  const end=notePointAtTextOffset(editor,positions.end);
  const range=document.createRange();
  try{
    range.setStart(start.node,start.offset);
    range.setEnd(end.node,end.offset);
    const sel=getSelection();sel.removeAllRanges();sel.addRange(range);
    noteRanges[course]=range.cloneRange();
    return !range.collapsed;
  }catch(_){return false}
}
function applyWordNoteFontSize(course,value){
  const editor=noteEditor(course),px=clampNoteFontSize(value);if(!editor)return;
  restoreNoteSelection(course);
  const sel=getSelection(),range=sel&&sel.rangeCount?sel.getRangeAt(0):null;
  const positions=noteSelectionOffsets(editor,range);
  try{document.execCommand('styleWithCSS',false,false)}catch(_){}
  const applied=document.execCommand('fontSize',false,'7');
  if(positions){
    // Apply to the newly formatted inline elements; retain the original marked word.
    normalizePendingNoteFont(editor,px);
    pendingNoteFontSize[course]=null;
    restoreNoteTextSelection(course,positions);
  }else if(applied){
    pendingNoteFontSize[course]=px;
    rememberNoteSelection(course);
  }
  setNoteSizeUi(course,px);
  queueNotesSave();
  // Keep both the actual browser selection and our saved selection for the next A+/A- click.
  if(positions)restoreNoteTextSelection(course,positions);
  setTimeout(()=>syncNoteToolbar(course),0);
}
function nextWordNoteFontSize(current,direction){
  current=clampNoteFontSize(current);
  if(direction>0)return NOTE_FONT_SIZES.find(v=>v>current)||96;
  const lower=NOTE_FONT_SIZES.filter(v=>v<current);return lower.length?lower[lower.length-1]:8;
}
function initWordNoteFontSize(){
  document.querySelectorAll('.notes-toolbar').forEach(tb=>{
    const course=tb.dataset.noteCourse,input=tb.querySelector('[data-note-size-value]');
    if(!input)return;
    tb.querySelectorAll('[data-note-size-step]').forEach(button=>{
      button.addEventListener('mousedown',e=>{e.preventDefault();rememberNoteSelection(course)});
      button.addEventListener('click',()=>{
        const base=currentNoteFontSize(course),dir=Number(button.dataset.noteSizeStep)||1;
        applyWordNoteFontSize(course,nextWordNoteFontSize(base,dir));
      });
    });
    input.addEventListener('focus',()=>{rememberNoteSelection(course);input.select()});
    input.addEventListener('keydown',e=>{
      if(e.key==='Enter'){e.preventDefault();applyWordNoteFontSize(course,input.value);input.blur()}
      if(e.key==='Escape'){e.preventDefault();setNoteSizeUi(course,currentNoteFontSize(course));input.blur()}
    });
    input.addEventListener('change',()=>applyWordNoteFontSize(course,input.value));
  });
  ['ET4012','MA4026','TODO'].forEach(course=>{
    const editor=noteEditor(course);if(!editor)return;
    editor.addEventListener('input',()=>{
      const px=pendingNoteFontSize[course];
      if(px!=null&&editor.querySelector('font[size="7"]')){
        normalizePendingNoteFont(editor,px);
        pendingNoteFontSize[course]=null;
        rememberNoteSelection(course);
        queueNotesSave();
      }
      setNoteSizeUi(course,currentNoteFontSize(course));
    });
    ['keyup','mouseup','focus'].forEach(ev=>editor.addEventListener(ev,()=>setNoteSizeUi(course,currentNoteFontSize(course))));
  });
  document.addEventListener('selectionchange',()=>{
    ['ET4012','MA4026','TODO'].forEach(course=>{
      const editor=noteEditor(course),sel=getSelection();
      if(editor&&sel&&sel.rangeCount&&editor.contains(sel.focusNode))setNoteSizeUi(course,currentNoteFontSize(course));
    });
  });
  document.addEventListener('keydown',e=>{
    if(!(e.ctrlKey||e.metaKey)||!e.shiftKey)return;
    if(e.key!=='>'&&e.key!=='.'&&e.key!=='<'&&e.key!==',')return;
    const sel=getSelection(),node=sel&&sel.focusNode;
    const course=['ET4012','MA4026','TODO'].find(c=>{const ed=noteEditor(c);return ed&&node&&ed.contains(node)});
    if(!course)return;
    e.preventDefault();
    const dir=(e.key==='>'||e.key==='.')?1:-1;
    rememberNoteSelection(course);
    applyWordNoteFontSize(course,nextWordNoteFontSize(currentNoteFontSize(course),dir));
  },true);
  ['ET4012','MA4026','TODO'].forEach(course=>setNoteSizeUi(course,currentNoteFontSize(course)));
}
initWordNoteFontSize();
'''.strip()

if 'function initWordNoteFontSize()' not in js:
    js+='\n'+word_js+'\n'

# Fresh cache for the new toolbar.
if 'studieplan-shell-v3' in sw_text:
    sw_text=sw_text.replace('studieplan-shell-v3','studieplan-shell-v4')

index.write_text(html,encoding='utf-8')
app.write_text(js,encoding='utf-8')
sw.write_text(sw_text,encoding='utf-8')
print('Word-like note font sizing applied')
