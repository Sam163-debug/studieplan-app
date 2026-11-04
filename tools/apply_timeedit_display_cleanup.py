from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
hp=root/'index.html';ap=root/'app.js';sp=root/'service-worker.js'
html=hp.read_text(encoding='utf-8')
js=ap.read_text(encoding='utf-8')
sw=sp.read_text(encoding='utf-8')

helper=Path('tools/timeedit_display_cleanup.js').read_text(encoding='utf-8')
if 'function teNormalizeImportedEvent' not in helper:
    raise SystemExit('Missing TimeEdit title cleanup helper')
# Inline the helper BEFORE the app initialization, so state loading, imports
# and later Google sync normalization all use the same migration.
js="let teMigrationChanged=false;\n"+helper+'\n'+js
js=js.replace(
    "x.events=x.events.map(e=>({...e,",
    "x.events=x.events.map(e=>teNormalizeImportedEvent({...e,",
    1
)
# Close the teNormalizeImportedEvent call after the normalization object.
old="categoryId:e.categoryId||'OTHER',origin:e.origin||'custom'}));return x;"
new="categoryId:e.categoryId||'OTHER',origin:e.origin||'custom'}));return x;"
if old not in js:raise SystemExit('Event normalization anchor missing')
js=js.replace(old,new,1)
old="if(!raw)save();}catch(err){"
new="if(!raw||teMigrationChanged){save();teMigrationChanged=false;}}catch(err){"
if old not in js:raise SystemExit('Initial state save anchor missing')
js=js.replace(old,new,1)

# Set description checkbox OFF when creating a new activity. An explicit
# checked state saved later still wins, including for previously edited events.
old="$('fShowDescription').checked=true;"
if old not in js:raise SystemExit('New activity description default anchor missing')
js=js.replace(old,"$('fShowDescription').checked=false;",1)
old='<input type="checkbox" id="fShowDescription" checked>'
if old not in html:raise SystemExit('Description checkbox HTML anchor missing')
html=html.replace(old,'<input type="checkbox" id="fShowDescription">',1)

# Remove old importer UI, parser and import buttons from the published site
# without touching the user's local/Google synced events.
import re
html=re.sub(r'<h2>Schema från TimeEdit</h2>\s*<div class="te-import-card">[\s\S]*?</div>', '', html, count=1)
html=re.sub(r'<div id="timeeditImportDialog"[\s\S]*?</div>\s*(?=<script src="app.js")', '', html,count=1)
html=html.replace('<script src="timeedit_ics_parser.js"></script><script src="timeedit_ics_import.js"></script>','')
if 'timeeditOpenImport' in html or 'timeeditConfirmImport' in html:
    raise SystemExit('Old import controls remain')

# Preserve each category's original block color. Replace only the diagonal
# texture with wider, very low contrast stripes. No white label backgrounds.
css=r'''
/* The calendar renderer paints the FULL opaque course color.
   Never override that inline background with a pale CSS gradient. */
.event.timeedit{background-repeat:repeat}
/* Keep all calendar text directly on the colored activity block. */
.event.timeedit .te-source-marker{
  position:absolute;
  right:4px;
  bottom:3px;
  z-index:2;
  display:block;
  background:transparent;
  border:0;
  border-radius:0;
  box-shadow:none;
  padding:0;
  margin:0;
  color:inherit;
  font-size:8px;
  font-weight:600;
  letter-spacing:.025em;
  line-height:1;
  opacity:.16;
  pointer-events:none;
}
'''.strip()
if '</style>' not in html:raise SystemExit('Style tag missing')
html=html.replace('</style>',css+'</style>',1)

# The source marking previously lived in the import script; keep it permanent,
# so the existing imported events are labeled even without an importer.
# Pass the actual, user-editable course color into each imported block.
# CSS must not replace a background image without restoring the color beneath it.
# The old styleFor used translucent course colors inside its stripes; that
# caused the background of each event to appear almost white/blue. Use the
# chosen fully opaque course color as the lowest background layer, and overlay
# just a faint diagonal pattern on top. Keep other origins' styles unchanged.
old_style=r'''function styleFor(e){const base=validHex(category(e.categoryId).color);let bg=rgba(base,.16);if(e.origin==='timeedit')bg=`repeating-linear-gradient(135deg,${rgba(base,.30)} 0,${rgba(base,.30)} 7px,${rgba(base,.08)} 7px,${rgba(base,.08)} 14px)`;else if(e.origin==='gym')bg=`radial-gradient(circle at 4px 4px,${rgba(base,.38)} 0 2px,${rgba(base,.10)} 2.5px 100%)`;return {borderColor:base,background:bg,color:'#1f2937'}}'''
new_style=r'''function teVisualCourseColor(e){
  const cat=category(e.categoryId);
  const key=[e.categoryId||'',cat.name||'',e.course||'',e.title||''].join(' ').toLocaleLowerCase('sv-SE');
  if(/datorsystemteknik|datorsystem/.test(key))return '#fbb7d9';
  if(/elektronik/.test(key))return '#bbe77e';
  return validHex(cat.color);
}
function styleFor(e){
  const base=e.origin==='timeedit'?teVisualCourseColor(e):validHex(category(e.categoryId).color);
  let bg=rgba(base,.16);
  if(e.origin==='timeedit'){
    bg='repeating-linear-gradient(135deg, rgba(0,0,0,.065) 0 13px, rgba(255,255,255,.018) 13px 30px), linear-gradient('+base+','+base+')';
  }else if(e.origin==='gym'){
    bg=`radial-gradient(circle at 4px 4px,${rgba(base,.38)} 0 2px,${rgba(base,.10)} 2.5px 100%)`;
  }
  return {borderColor:base,background:bg,color:'#1f2937'};
}'''
if old_style not in js:raise SystemExit('TimeEdit styleFor original code not found')
js=js.replace(old_style,new_style,1)

render_anchor="el.className='event '+e.origin+' status-'+e.status;applyStyle(el,e);"
if render_anchor not in js:raise SystemExit('Enhanced event render style anchor missing')
js=js.replace(render_anchor,
  render_anchor+"if(e.origin==='timeedit')el.style.setProperty('--te-category-color',teVisualCourseColor(e));",
  1)

js+=r'''
function teMarkCalendarEvents(){
  document.querySelectorAll('#calendar .event.timeedit').forEach(event=>{
    if(event.querySelector('.te-source-marker'))return;
    const marker=document.createElement('span');
    marker.className='te-source-marker';
    marker.textContent='TIMEEDIT';
    event.appendChild(marker);
  });
}
const tePreviousCalendarRender=renderCalendarEnhanced;
renderCalendarEnhanced=function(){
  tePreviousCalendarRender();
  teMarkCalendarEvents();
};
teMarkCalendarEvents();
'''

if 'studieplan-shell-v8' not in sw:raise SystemExit('Missing cache version 8')
sw=sw.replace('studieplan-shell-v8','studieplan-shell-v13')
for guard in ('teNormalizeImportedEvent','teCleanTimeEditTitle',
              'teMarkCalendarEvents','te-source-marker','id="fShowDescription"'):
    if guard not in html+js:raise SystemExit('Missing feature guard '+guard)
hp.write_text(html,encoding='utf-8')
ap.write_text(js,encoding='utf-8')
sp.write_text(sw,encoding='utf-8')
print('TimeEdit blocks use full category-color backgrounds with low-contrast stripes')
