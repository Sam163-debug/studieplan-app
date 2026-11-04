from pathlib import Path
import sys, shutil

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
page=root/'index.html'
html=page.read_text(encoding='utf-8')

# Deliver parser and import logic as assets; the schedule itself is never
# distributed by GitHub Pages. Imported items live in the user's app state.
for filename in ('timeedit_ics_parser.js','timeedit_ics_import.js'):
    source=Path('tools')/filename
    if not source.is_file():raise SystemExit('Missing '+str(source))
    shutil.copy2(source,root/filename)

entry='<h2>Google &amp; moln</h2>'
if entry not in html:
    entry='<h2>Google & moln</h2>'
if entry not in html:raise SystemExit('Sidebar Google section anchor missing')

panel='''<h2>Schema från TimeEdit</h2>
<div class="te-import-card">
  <p>Importera iCalendar (.ics) med redigerbara, randmarkerade pass.</p>
  <button id="timeeditOpenImport" type="button">↧ Importera TimeEdit-schema</button>
</div>
'''
html=html.replace(entry,panel+entry,1)

modal='''<div id="timeeditImportDialog" class="modal-back hidden" role="dialog" aria-modal="true" aria-labelledby="teImportHeading">
  <div class="modal te-import-modal">
    <div class="te-import-heading"><h2 id="teImportHeading">Importera TimeEdit-schema</h2><button type="button" id="timeeditCloseImport" aria-label="Stäng importfönstret">Stäng</button></div>
    <div class="field"><label for="timeeditImportUrl">Länk till TimeEdit (iCalendar/ICS)</label>
      <input id="timeeditImportUrl" type="url" spellcheck="false" autocomplete="off" placeholder="https://cloud.timeedit.net/... .ics">
    </div>
    <button id="timeeditFetchBtn" type="button">Hämta från länk</button>
    <div class="te-import-divider">Eller välj en nedladdad .ics-fil</div>
    <div class="field"><input id="timeeditFile" type="file" accept=".ics,text/calendar"></div>
    <div id="timeeditImportStatus" class="te-import-status" role="status" aria-live="polite">Schema sparas bara i dina appdata, inte i GitHub-repot.</div>
    <div class="modal-actions">
      <button id="timeeditConfirmImport" class="primary" disabled type="button">Importera nya schemapass</button>
    </div>
  </div>
</div>
'''
anchor='<script src="app.js"></script>'
if anchor not in html:raise SystemExit('app.js script anchor missing')
html=html.replace(anchor,modal+anchor,1)
scripts='<script src="timeedit_ics_parser.js"></script><script src="timeedit_ics_import.js"></script>'
if scripts not in html:html=html.replace('</body>',scripts+'\n</body>',1)

css='''
.te-import-card{padding:10px;background:#c6dae5;border:1px solid #99b6c6;border-radius:10px;margin:8px 0}
.te-import-card p{margin:0 0 9px;color:#38556b;font-size:12px;line-height:1.35}
.te-import-card button{width:100%;background:#174c68;color:#f5fcff;border-color:#2c7898}
.te-import-card button:hover{background:#216282;color:#fff}
.te-import-modal{max-width:640px;width:min(95vw,640px);max-height:88vh;overflow:auto}
.te-import-heading{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-bottom:16px}
.te-import-heading h2{margin:0}
.te-import-divider{margin:17px 0 10px;padding-top:12px;border-top:1px solid #9fbac9;font-size:12px;color:#426276}
.te-import-status{min-height:60px;margin:15px 0;padding:11px 13px;background:#b7d7e0;border:1px solid #90bac7;border-radius:8px;color:#19384d;line-height:1.45;font-size:13px}
.te-import-status.te-import-error{background:#eed8d8;border-color:#d7a5a5;color:#7e2630}
.event.timeedit{box-shadow:inset 3px 0 0 rgba(11,63,84,.75),0 2px 7px rgba(19,40,50,.14)}
.te-source-marker{display:inline-block;font-size:9px;line-height:1.2;font-weight:800;letter-spacing:.04em;vertical-align:middle;margin:3px 0 0;padding:1px 4px;background:rgba(2,51,68,.76);color:#f8ffff;border:1px solid rgba(255,255,255,.4);border-radius:3px}
'''
if '</style>' not in html:raise SystemExit('Missing style tag')
html=html.replace('</style>',css+'</style>',1)

for val in ['id="timeeditOpenImport"','id="timeeditImportDialog"','id="timeeditFile"','timeedit_ics_parser.js','timeedit_ics_import.js']:
    if val not in html:raise SystemExit('TimeEdit UI guard failed '+val)
page.write_text(html,encoding='utf-8')
print('TimeEdit importer assets and UI installed')
