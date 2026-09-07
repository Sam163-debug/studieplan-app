from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
app = root / 'app.js'
js = app.read_text(encoding='utf-8')

old_close = "function closeEventModal(){$('eventModalBack').classList.add('hidden')}"
new_close = "function closeEventModal(reason='other'){if(editingId&& !['delete','cancel','save'].includes(reason))return false;$('eventModalBack').classList.add('hidden');return true}"
if old_close not in js:
    raise SystemExit('closeEventModal anchor not found')
js = js.replace(old_close, new_close, 1)

old_save = "save();closeEventModal();render()}"
new_save = "save();closeEventModal('save');render()}"
if old_save not in js:
    raise SystemExit('saveModal close anchor not found')
js = js.replace(old_save, new_save, 1)

old_delete = "save();closeEventModal();render()}}"
new_delete = "save();closeEventModal('delete');render()}}"
if old_delete not in js:
    raise SystemExit('delete close anchor not found')
js = js.replace(old_delete, new_delete, 1)

old_handlers = "$('cancelBtn').onclick=closeEventModal;$('saveBtn').onclick=saveModal;$('deleteBtn').onclick=del;$('eventModalBack').addEventListener('click',e=>{if(e.target===$('eventModalBack'))closeEventModal()});"
new_handlers = "$('cancelBtn').onclick=()=>closeEventModal('cancel');$('saveBtn').onclick=saveModal;$('deleteBtn').onclick=del;$('eventModalBack').addEventListener('click',e=>{if(e.target===$('eventModalBack'))closeEventModal('backdrop')});"
if old_handlers not in js:
    raise SystemExit('modal handler anchor not found')
js = js.replace(old_handlers, new_handlers, 1)

escape_guard = "document.addEventListener('keydown',e=>{if(e.key==='Escape'&&editingId&&!$('eventModalBack').classList.contains('hidden')){e.preventDefault();e.stopImmediatePropagation()}},true);"
if escape_guard not in js:
    js += "\n" + escape_guard + "\n"

app.write_text(js, encoding='utf-8')
print('Locked edit modal applied')
