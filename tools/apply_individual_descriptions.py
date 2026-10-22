from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
hp=root/'index.html';ap=root/'app.js';sp=root/'service-worker.js'
html=hp.read_text(encoding='utf-8');js=ap.read_text(encoding='utf-8');sw=sp.read_text(encoding='utf-8')

# Remove the old global option, keeping descriptions unchanged in state.
old='<label class="calendar-description-toggle" title="Visa eller dölj beskrivningar i kalenderblock"><input id="showCalendarDescriptions" type="checkbox" checked> Visa beskrivning</label>'
if old not in html:raise SystemExit('Global description control not found')
html=html.replace(old,'',1)
modal='<div class="field"><label>Beskrivning</label><textarea id="fDesc" rows="4"></textarea></div>'
if modal not in html:raise SystemExit('Activity description field missing')
html=html.replace(modal,modal+'\n  <label class="event-description-visibility"><input type="checkbox" id="fShowDescription" checked> Visa beskrivning i kalenderblocket</label>',1)

# Persist the flag on every event, including repeated activities and copied backups.
edit_anchor="$('fDesc').value=e.description||'';"
add_anchor="$('fDesc').value='';"
if edit_anchor not in js or add_anchor not in js:raise SystemExit('Modal edit/open anchors not found')
js=js.replace(edit_anchor,edit_anchor+"$('fShowDescription').checked=e.showDescription!==false;",1)
js=js.replace(add_anchor,add_anchor+"$('fShowDescription').checked=true;",1)

# Store a boolean in each event, and also when updating the rest of a series.
head='function saveModal(){'
tail='\nfunction del(){'
start=js.find(head);end=js.find(tail,start)
if start<0 or end<0:raise SystemExit('saveModal region missing')
section=js[start:end]
piece="description:$('fDesc').value.trim(),"
if section.count(piece)!=2:raise SystemExit('Expected two descriptions in saveModal')
section=section.replace(piece,piece+"showDescription:$('fShowDescription').checked,",2)
series_piece="description:patch.description,"
if series_piece not in section:raise SystemExit('Series update anchor missing')
section=section.replace(series_piece,series_piece+"showDescription:patch.showDescription,",1)
js=js[:start]+section+js[end:]

# Remove old global pref initializer; with the old button gone, the old
# function is inert but leaving it is confusing and risks future regressions.
js=re.sub(r"\n// UI-only preference; not part of event data or backups\.\nconst CALENDAR_DESCRIPTION_PREF=[\s\S]*?\ninitCalendarDescriptionToggle\(\);\n", '\n',js,count=1)

# Enhanced calendar renderer is the only desktop calendar entrypoint.
start=js.find('function renderCalendarEnhanced(){')
end=js.find('\nfunction statsEvents()',start)
if start<0 or end<0:raise SystemExit('Enhanced calendar not found')
section=js[start:end]
old="(e.description?`<div class=\"calendar-event-description\">${escapeHtml(e.description)}</div>`:'')"
new="(e.description&&e.showDescription!==false?`<div class=\"calendar-event-description\">${escapeHtml(e.description)}</div>`:'')"
if old not in section:raise SystemExit('Enhanced description renderer not found')
section=section.replace(old,new,1)
js=js[:start]+section+js[end:]

# Keep mobile agenda consistent with the setting in each event.
old="desc=e.description?`<div class=\"mobile-event-desc\">${escapeHtml(e.description)}</div>`:''"
new="desc=e.description&&e.showDescription!==false?`<div class=\"mobile-event-desc\">${escapeHtml(e.description)}</div>`:''"
if old not in js:raise SystemExit('Mobile description renderer not found')
js=js.replace(old,new,1)

css="""
/* Description visibility is per activity, set in the activity editor. */
.event-description-visibility{display:flex;align-items:center;gap:9px;padding:10px 12px;margin:2px 0 12px;border:1px solid #9fb9c8;border-radius:9px;background:#c9dce8;color:#173047;font-weight:600;font-size:13px;cursor:pointer}
.event-description-visibility input{accent-color:#168fae;width:17px;height:17px;margin:0;flex:none}
.calendar-event-description{font-size:14px;line-height:1.25;font-weight:600;margin-top:5px;opacity:1;white-space:pre-line;overflow-wrap:anywhere;word-break:break-word;max-width:100%}
.event.event-description-roomy .calendar-event-description{font-size:15px;line-height:1.28}
.event.event-description-compact .calendar-event-description{font-size:12px;line-height:1.2}
.event.event-description-tight .calendar-event-description{font-size:11px;line-height:1.15}
.mobile-event-desc{font-size:14px;line-height:1.35;white-space:pre-line}
""".strip()
html=html.replace('</style>',css+'\n</style>',1)
# Remove obsolete hide selector that is tied to the old global preference.
html=html.replace("body.calendar-description-hidden .calendar-event-description{display:none!important}","")

# Fit within each calendar block while keeping title and time readable.
js += """
function fitCalendarEventDescriptions(){
  document.querySelectorAll('#calendar .event').forEach(event=>{
    const desc=event.querySelector('.calendar-event-description');
    if(!desc)return;
    event.classList.remove('event-description-roomy','event-description-compact','event-description-tight');
    const available=event.clientHeight;
    if(available>=110)event.classList.add('event-description-roomy');
    if(event.scrollHeight>available)event.classList.add('event-description-compact');
    if(event.scrollHeight>available)event.classList.replace('event-description-compact','event-description-tight');
    // Event already clips overflow: the title and time retain their space.
  });
}
const originalEnhancedCalendarRender=renderCalendarEnhanced;
renderCalendarEnhanced=function(){
  originalEnhancedCalendarRender();
  fitCalendarEventDescriptions();
};
"""
# Existing render() resolves renderCalendarEnhanced dynamically, so wrapper is safe.
if 'studieplan-shell-v6' not in sw:raise SystemExit('SW cache anchor missing')
sw=sw.replace('studieplan-shell-v6','studieplan-shell-v7')
for g in ('fShowDescription','showDescription:patch.showDescription','function fitCalendarEventDescriptions','e.showDescription!==false'):
 if g not in html+js:raise SystemExit('missing guard '+g)
hp.write_text(html,encoding='utf-8');ap.write_text(js,encoding='utf-8');sp.write_text(sw,encoding='utf-8')
print('Per-activity description setting and adaptive description font applied')
