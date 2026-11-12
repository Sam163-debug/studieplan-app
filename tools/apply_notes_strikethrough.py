from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
app = root / 'app.js'
html = index.read_text(encoding='utf-8')
js = app.read_text(encoding='utf-8')

# All five final note cards already use the shared toolbar; place the new
# control beside Underline rather than creating a separate editing system.
anchor = '<button type="button" data-note-action="underline" title="Understruken"><u>U</u></button>'
button = '<button type="button" data-note-action="strikethrough" title="Genomstrykning" aria-label="Genomstrykning" aria-pressed="false"><s>abc</s></button>'
count = html.count(anchor)
if count != 5:
    raise SystemExit(f'Expected five finished note toolbars, found {count}')
html = html.replace(anchor, anchor + '\n          ' + button)

# contenteditable can create <strike>, <s> or <del>, depending on browser.
# Preserve all three tags when notes are autosaved, loaded and synchronized.
old_tags = "const allowed=new Set(['DIV','P','BR','B','STRONG','I','EM','U','H1','H2','H3','SPAN','UL','OL','LI']);"
new_tags = "const allowed=new Set(['DIV','P','BR','B','STRONG','I','EM','U','S','STRIKE','DEL','H1','H2','H3','SPAN','UL','OL','LI']);"
if js.count(old_tags) != 1:
    raise SystemExit('Note HTML sanitizer anchor missing')
js = js.replace(old_tags, new_tags, 1)

# Browser execCommand uses the spelling strikeThrough. The existing command
# wrapper preserves selection and schedules note autosave after formatting.
action_anchor = "if(['bold','italic','underline'].includes(action))document.execCommand(action,false,null);"
if js.count(action_anchor) != 1:
    raise SystemExit('Note action handler anchor missing')
js = js.replace(action_anchor, """if(action==='strikethrough')document.execCommand('strikeThrough',false,null);
  else """ + action_anchor, 1)

# Display active state when the cursor is in a strikethrough span or tag,
# including when the note has been reloaded from its saved HTML.
toolbar_anchor = """  setNoteButtonState(tb.querySelector('[data-note-action="underline"]'),String(style.textDecorationLine||style.textDecoration||'').includes('underline'));"""
if js.count(toolbar_anchor) != 1:
    raise SystemExit('Note toolbar state synchronization anchor missing')
helper = """function noteHasStrikethrough(node,editor){
  let el=node&&node.nodeType===Node.TEXT_NODE?node.parentElement:node;
  for(;el&&el!==editor;el=el.parentElement){
    if(['S','STRIKE','DEL'].includes(el.tagName))return true;
    const css=getComputedStyle(el);
    if(String(css.textDecorationLine||css.textDecoration||'').includes('line-through'))return true;
  }
  return false;
}
"""
sync_anchor = 'function syncNoteToolbar(course){'
if js.count(sync_anchor) != 1:
    raise SystemExit('Note toolbar sync function missing')
js = js.replace(sync_anchor, helper + sync_anchor, 1)
js = js.replace(toolbar_anchor, toolbar_anchor + """
  setNoteButtonState(tb.querySelector('[data-note-action="strikethrough"]'),noteHasStrikethrough(node,editor));
  const strikeButton=tb.querySelector('[data-note-action="strikethrough"]');
  if(strikeButton)strikeButton.setAttribute('aria-pressed',String(noteHasStrikethrough(node,editor)));""", 1)

if html.count('data-note-action="strikethrough"') != 5:
    raise SystemExit('Not all five note toolbars have Strikethrough')
for guard in ("document.execCommand('strikeThrough'", "function noteHasStrikethrough", "'S','STRIKE','DEL'"):
    if guard not in js:
        raise SystemExit('Missing strikethrough integration: ' + guard)
index.write_text(html, encoding='utf-8')
app.write_text(js, encoding='utf-8')
print('Strikethrough enabled for all five note editors with autosave and toolbar sync')
