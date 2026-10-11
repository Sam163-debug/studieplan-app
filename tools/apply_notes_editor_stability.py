from pathlib import Path
import re
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
index=root/'index.html'
app=root/'app.js'
html=index.read_text(encoding='utf-8')
js=app.read_text(encoding='utf-8')

def replace_js(start,end,body):
    global js
    pattern=re.escape(start)+r'[\s\S]*?(?='+re.escape(end)+')'
    js,n=re.subn(pattern,lambda m:body+'\n',js,count=1)
    if n!=1:raise SystemExit('Missing JS edit anchor: '+start)

# Preserving the saved margin is mandatory: notes HTML is sanitized at every autosave/load.
needle="fontSize:el.style.fontSize,lineHeight:el.style.lineHeight}"
if needle not in js:raise SystemExit('Note sanitizer style anchor missing')
js=js.replace(needle,"fontSize:el.style.fontSize,lineHeight:el.style.lineHeight,marginBottom:el.style.marginBottom}",1)
needle="if(keep.lineHeight)el.style.lineHeight=keep.lineHeight;"
if needle not in js:raise SystemExit('Note sanitizer assignment missing')
js=js.replace(needle,needle+"if(keep.marginBottom)el.style.marginBottom=keep.marginBottom;",1)

# The old toolbar commands were discarding selected ranges too. Retain the same
# logical text selection through bold, italic, underline, fonts, colors and lists.
replace_js("function applyNoteCommand(course,action,value){","function initNoteToolbar()",r'''
function applyNoteCommand(course,action,value){
  const editor=noteEditor(course);
  restoreNoteSelection(course);
  const sel=getSelection();
  const range=sel&&sel.rangeCount?sel.getRangeAt(0):null;
  const selected=noteSelectionOffsets(editor,range);
  try{document.execCommand('styleWithCSS',false,true)}catch(_){}
  if(['bold','italic','underline'].includes(action))document.execCommand(action,false,null);
  else if(action==='format')document.execCommand('formatBlock',false,value||'p');
  else if(action==='font')document.execCommand('fontName',false,value||'system-ui');
  else if(action==='color')document.execCommand('foreColor',false,value||'#111827');
  else if(action==='size')return applyWordNoteFontSize(course,value||16);
  else if(action==='lineheight')applyGoodnotesSpacing(course,false,value||0);
  else if(action==='ul')document.execCommand('insertUnorderedList',false,null);
  else if(action==='ol')document.execCommand('insertOrderedList',false,null);
  if(selected)restoreNoteTextSelection(course,selected);
  else rememberNoteSelection(course);
  queueNotesSave();
  setTimeout(()=>syncNoteToolbar(course),0);
}
'''.strip())

# The size of marked text is the size at the first MARKED CHARACTER,
# not of an adjacent character on a text-node boundary.
replace_js("function currentNoteFontSize(course){","function setNoteSizeUi(course,value){",r'''
function currentNoteFontSize(course){
  const editor=noteEditor(course),sel=getSelection();
  if(!editor)return 16;
  const live=sel&&sel.rangeCount&&editor.contains(sel.getRangeAt(0).commonAncestorContainer)?sel.getRangeAt(0):null;
  const range=live||noteRanges[course];
  if(!range)return 16;
  let node=null;
  try{
    const offset=noteTextBoundaryOffset(editor,range.startContainer,range.startOffset);
    node=notePointAtTextOffset(editor,offset,range.collapsed?'end':'start').node;
  }catch(_){}
  if(node&&node.nodeType===Node.TEXT_NODE)node=node.parentElement;
  if(!node||!editor.contains(node))node=editor;
  return clampNoteFontSize(parseFloat(getComputedStyle(node).fontSize)||16);
}
'''.strip())

# Directly format ONLY the selected text nodes, retaining their color, bold,
# italic, underline and font ancestry. No document.execCommand on a selection:
# browsers may collapse or replace the range at its first size change.
replace_js("function applyWordNoteFontSize(course,value){","function nextWordNoteFontSize(current,direction){",r'''
function applyNoteFontToSelectedText(editor,positions,px){
  const walker=document.createTreeWalker(editor,NodeFilter.SHOW_TEXT);
  const nodes=[];let node;
  while((node=walker.nextNode()))nodes.push(node);
  let cursor=0,changed=false;
  for(const original of nodes){
    const length=original.length;
    const start=Math.max(0,Math.min(length,positions.start-cursor));
    const end=Math.max(0,Math.min(length,positions.end-cursor));
    cursor+=length;
    if(end<=start)continue;
    let target=original;
    if(start>0)target=target.splitText(start);
    if(end-start<target.length)target.splitText(end-start);
    const parent=target.parentNode;
    if(!parent)continue;
    const sizeSpan=document.createElement('span');
    sizeSpan.style.fontSize=px+'px';
    parent.insertBefore(sizeSpan,target);
    sizeSpan.appendChild(target);
    changed=true;
  }
  return changed;
}
function applyWordNoteFontSize(course,value){
  const editor=noteEditor(course),px=clampNoteFontSize(value);if(!editor)return;
  restoreNoteSelection(course);
  const sel=getSelection(),range=sel&&sel.rangeCount?sel.getRangeAt(0):null;
  const positions=noteSelectionOffsets(editor,range);
  if(positions){
    if(applyNoteFontToSelectedText(editor,positions,px)){
      pendingNoteFontSize[course]=null;
      restoreNoteTextSelection(course,positions);
    }
  }else{
    // For a collapsed caret retain the browser's typing style.
    try{document.execCommand('styleWithCSS',false,false)}catch(_){}
    document.execCommand('fontSize',false,'7');
    pendingNoteFontSize[course]=px;
    rememberNoteSelection(course);
  }
  setNoteSizeUi(course,px);
  queueNotesSave();
  if(positions)restoreNoteTextSelection(course,positions);
  setTimeout(()=>syncNoteToolbar(course),0);
}
'''.strip())

# At the exact start of a styled text node, start selection there, not at the
# end of the previous sibling's text (the cause of the wrong A+ step).
replace_js("function notePointAtTextOffset(editor,offset){","function restoreNoteTextSelection(course,positions){",r'''
function notePointAtTextOffset(editor,offset,edge='start'){
  let rest=Math.max(0,offset),last=null;
  const walker=document.createTreeWalker(editor,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    last=node;
    if(rest<node.length||(rest===node.length&&edge==='end'))return {node,offset:rest};
    rest-=node.length;
  }
  return last?{node:last,offset:last.length}:{node:editor,offset:0};
}
'''.strip())
js=js.replace("notePointAtTextOffset(editor,positions.start);","notePointAtTextOffset(editor,positions.start,'start');",1)
js=js.replace("notePointAtTextOffset(editor,positions.end);","notePointAtTextOffset(editor,positions.end,'end');",1)

# Spacing is AFTER the selected paragraph. Do not set line-height.
replace_js("function spacingBlocksForCourse(course){","function lineHeightPt(block){",r'''
function spacingBlocksForCourse(course){
  const editor=noteEditor(course);if(!editor)return [];
  const sel=getSelection();
  const live=sel&&sel.rangeCount&&editor.contains(sel.getRangeAt(0).commonAncestorContainer)?sel.getRangeAt(0):null;
  const range=live||noteRanges[course];
  if(!range)return [];
  const blockFor=node=>spacingBlockFromNode(node,editor);
  if(range.collapsed){
    const block=blockFor(range.startContainer);return block?[block]:[];
  }
  const all=[...editor.querySelectorAll('div,p,h1,h2,h3,li')];
  const intersect=all.filter(b=>{try{return range.intersectsNode(b)}catch(_){return false}});
  return intersect.filter(b=>!intersect.some(child=>child!==b&&b.contains(child)));
}
'''.strip())
js=js.replace(
  "function clampSpacing(v){v=Number(v);if(!Number.isFinite(v))v=18;return Math.max(6,Math.min(120,Math.round(v*100)/100))}",
  "function clampSpacing(v){v=Number(v);if(!Number.isFinite(v))v=0;return Math.max(0,Math.min(72,Math.round(v*2)/2))}",
  1
)
if "return Math.max(0,Math.min(72" not in js:raise SystemExit('Spacing clamp anchor not found')
replace_js("function applyGoodnotesSpacing(course,auto,value){","function closeSpacingPanels(except=null){",r'''
function applyGoodnotesSpacing(course,auto,value){
  const blocks=spacingBlocksForCourse(course);if(!blocks.length)return;
  if(auto)blocks.forEach(b=>b.style.removeProperty('margin-bottom'));
  else{const pt=clampSpacing(value);blocks.forEach(b=>b.style.marginBottom=pt+'pt')}
  queueNotesSave();
}
function setSpacingPanelState(panel,course){
  const blocks=spacingBlocksForCourse(course);
  const first=blocks[0];
  const auto=blocks.length?blocks.every(b=>!b.style.marginBottom):true;
  const value=clampSpacing(first?parseFloat(first.style.marginBottom)||0:0);
  const a=panel.querySelector('[data-spacing-auto]'),r=panel.querySelector('[data-spacing-range]'),n=panel.querySelector('[data-spacing-number]'),minus=panel.querySelector('[data-spacing-minus]'),plus=panel.querySelector('[data-spacing-plus]');
  a.checked=auto;
  r.value=value;n.value=value.toFixed(1);
  r.disabled=auto;n.disabled=auto;minus.disabled=auto;plus.disabled=auto;
}
'''.strip())

js=js.replace("setManual(clampSpacing(Number(number.value)-0.01))","setManual(clampSpacing(Number(number.value)-2))")
js=js.replace("setManual(clampSpacing(Number(number.value)+0.01))","setManual(clampSpacing(Number(number.value)+2))")

# Keep the existing control's IDs and attributes to preserve event listeners.
html=html.replace('data-spacing-toggle title="Radavstånd">↕ Radavstånd','data-spacing-toggle title="Avstånd efter vald rad">↕ Avstånd efter')
html=html.replace('<strong>Radavstånd</strong><label><span>Automatiskt</span>','<strong>Avstånd efter raden</strong><label><span>Inget extra</span>')
html=html.replace('data-spacing-range min="6" max="120" step="0.01" value="18"','data-spacing-range min="0" max="72" step="1" value="0"')
html=html.replace('data-spacing-number min="6" max="120" step="0.01" value="18"','data-spacing-number min="0" max="72" step="1" value="0"')

# Reduce heading and list spacing without overriding text sizes or text colors.
css=r'''
/* Compact paragraph layout: extra space is only applied when explicitly requested. */
.notes-editor h1{margin:.12em 0 .04em!important;line-height:1.18}
.notes-editor h2{margin:.12em 0 .04em!important;line-height:1.2}
.notes-editor h3{margin:.12em 0 .04em!important;line-height:1.22}
.notes-editor p{margin-top:0!important;margin-bottom:0}
.notes-editor ul,.notes-editor ol{margin-top:0!important;margin-bottom:0!important;padding-left:1.45em}
.notes-editor li{margin-top:0!important;margin-bottom:0}
.notes-spacing-panel{width:min(300px,calc(100vw - 30px))}
'''.strip()
# NB margin-bottom !important on paragraphs/LI would suppress selected
# inline margin-bottom, so do not use !important for the bottom margin.
css=css.replace('.notes-editor p{margin-top:0!important;margin-bottom:0}', '.notes-editor p{margin-top:0!important;margin-bottom:0}')
if '/* Compact paragraph layout:' not in html:
  if '</style>' not in html:raise SystemExit('CSS close anchor missing')
  html=html.replace('</style>',css+'\n</style>',1)

# Force cache invalidation so old app.js does not win via the service worker.
sw=root/'service-worker.js'
sw_text=sw.read_text(encoding='utf-8')
if 'studieplan-shell-v4' not in sw_text:raise SystemExit('service worker v4 anchor missing')
sw_text=sw_text.replace('studieplan-shell-v4','studieplan-shell-v5')
sw.write_text(sw_text,encoding='utf-8')

for required in ('function applyNoteFontToSelectedText','function restoreNoteTextSelection','style.marginBottom','marginBottom:el.style.marginBottom','Avstånd efter raden'):
  if required not in js+html:raise SystemExit('Missing editing stability guard: '+required)

index.write_text(html,encoding='utf-8')
app.write_text(js,encoding='utf-8')
print('Notes editor stability, selected-font resize and after-paragraph spacing applied')
