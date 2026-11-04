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
new="categoryId:e.categoryId||'OTHER',origin:e.origin||'custom'})));return x;"
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
html,count=re.subn(r'<h2>Schema från TimeEdit</h2>\s*<div class="te-import-card">[\s\S]*?</div>', '', html, count=1)
if count!=1:raise SystemExit('TimeEdit sidebar import panel missing')
html,count=re.subn(r'<div id="timeeditImportDialog"[\s\S]*?</div>\s*(?=<script src="app.js")', '', html,count=1)
if count!=1:raise SystemExit('TimeEdit import modal missing')
html=html.replace('<script src="timeedit_ics_parser.js"></script><script src="timeedit_ics_import.js"></script>','')
if 'timeeditOpenImport' in html or 'timeeditConfirmImport' in html:
    raise SystemExit('Old import controls remain')

# Stronger stripes are drawn over the course background via a pseudo-element,
# rather than replacing the user-selected avocado/rose/category colors.
css=r'''
/* Imported source: thicker stripes, readable labels, no importer controls. */
.event.timeedit{isolation:isolate;position:absolute;overflow:hidden}
.event.timeedit::before{
  content:"";position:absolute;inset:0;z-index:0;pointer-events:none;
  background:repeating-linear-gradient(135deg,
    rgba(7,46,51,.18) 0 8px,
    rgba(255,255,255,.09) 8px 18px);
}
.event.timeedit > *{position:relative;z-index:1}
.event.timeedit > b,.event.timeedit > small,
.event.timeedit > .calendar-event-description{
  background:rgba(238,248,245,.93)!important;
  color:#113149!important;
  border-radius:3px;
  padding:1px 3px;
  text-shadow:none!important;
  max-width:100%;
  box-decoration-break:clone;
  -webkit-box-decoration-break:clone;
}
.event.timeedit > b{font-weight:750}
.event.timeedit > small{font-weight:650}
.event.timeedit .te-source-marker{
  display:inline-block;position:relative;z-index:2;
  background:#17455a;color:#fff;border:1px solid #eef8fb;
  border-radius:3px;padding:1px 4px;margin-top:2px;
  font-size:9px;font-weight:800;letter-spacing:.06em;line-height:1.1;
}
'''
if '</style>' not in html:raise SystemExit('Style tag missing')
html=html.replace('</style>',css+'</style>',1)

# The source marking previously lived in the import script; keep it permanent,
# so the existing imported events are labeled even without an importer.
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
sw=sw.replace('studieplan-shell-v8','studieplan-shell-v9')
for guard in ('teNormalizeImportedEvent','teCleanTimeEditTitle',
              'teMarkCalendarEvents','te-source-marker','id="fShowDescription"'):
    if guard not in html+js:raise SystemExit('Missing feature guard '+guard)
hp.write_text(html,encoding='utf-8')
ap.write_text(js,encoding='utf-8')
sp.write_text(sw,encoding='utf-8')
print('Removed importer; stronger stripes; opted-out descriptions; cleaned imported TimeEdit titles')
