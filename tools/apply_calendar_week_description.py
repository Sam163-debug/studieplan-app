from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
index=root/'index.html'
app=root/'app.js'
sw=root/'service-worker.js'
html=index.read_text(encoding='utf-8')
js=app.read_text(encoding='utf-8')
sw_text=sw.read_text(encoding='utf-8')

old="currentMonday=isoToDate('2026-08-31')"
if old not in js:raise SystemExit('Calendar starting week anchor missing')
js=js.replace(old,"currentMonday=mondayOf(new Date())",1)

# The latest enhanced renderer is authoritative; the old fallback is intentionally untouched.
start=js.find('function renderCalendarEnhanced(){')
end=js.find('\nfunction statsEvents()',start)
if start<0 or end<0:raise SystemExit('Enhanced calendar renderer not found')
render=js[start:end]
old_render="</small>`+reminder;el.addEventListener("
new_render="</small>`+reminder+(e.description?`<div class=\"calendar-event-description\">${escapeHtml(e.description)}</div>`:'');el.addEventListener("
if old_render not in render:raise SystemExit('Enhanced event body renderer anchor missing')
render=render.replace(old_render,new_render,1)
js=js[:start]+render+js[end:]

# Remember user's preference in this browser only. Never modify activity descriptions.
ui='<label class="calendar-description-toggle" title="Visa eller dölj beskrivningar i kalenderblock"><input id="showCalendarDescriptions" type="checkbox" checked> Visa beskrivning</label>'
anchor='<button onclick="window.print()">Skriv ut</button>'
if anchor not in html:raise SystemExit('Week toolbar anchor missing')
html=html.replace(anchor,ui+anchor,1)

css="""
/* Description visibility applies only to displayed calendar blocks. */
.calendar-description-toggle{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border:1px solid #9fb9c8;border-radius:8px;background:#c9dce8;color:#173047;font-size:12px;font-weight:600;white-space:nowrap;cursor:pointer}
.calendar-description-toggle input{accent-color:#168fae;margin:0}
.calendar-event-description{font-size:11px;line-height:1.23;margin-top:4px;white-space:pre-line;overflow-wrap:anywhere;word-break:break-word;opacity:.92}
body.calendar-description-hidden .calendar-event-description{display:none!important}
@media print{.calendar-description-toggle{display:none!important}}
""".strip()
html=html.replace('</style>',css+'\n</style>',1)

js += """
// UI-only preference; not part of event data or backups.
const CALENDAR_DESCRIPTION_PREF='studieplan-show-calendar-descriptions-v1';
function initCalendarDescriptionToggle(){
  const control=$('showCalendarDescriptions');
  if(!control)return;
  let visible=true;
  try{visible=localStorage.getItem(CALENDAR_DESCRIPTION_PREF)!=='0'}catch(_){}
  control.checked=visible;
  document.body.classList.toggle('calendar-description-hidden',!visible);
  control.addEventListener('change',()=>{
    const show=control.checked;
    document.body.classList.toggle('calendar-description-hidden',!show);
    try{localStorage.setItem(CALENDAR_DESCRIPTION_PREF,show?'1':'0')}catch(_){}
  });
}
initCalendarDescriptionToggle();
"""

if 'studieplan-shell-v5' in sw_text:
  sw_text=sw_text.replace('studieplan-shell-v5','studieplan-shell-v6')
else:raise SystemExit('Service worker cache anchor missing')

for guard in ["currentMonday=mondayOf(new Date())","calendar-event-description","showCalendarDescriptions","CALENDAR_DESCRIPTION_PREF"]:
  if guard not in js+html:raise SystemExit('Missing new calendar guard '+guard)
index.write_text(html,encoding='utf-8')
app.write_text(js,encoding='utf-8')
sw.write_text(sw_text,encoding='utf-8')
print('Current-week startup and calendar description preference applied')
