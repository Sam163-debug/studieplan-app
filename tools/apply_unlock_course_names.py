from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
app=root/'app.js'
js=app.read_text(encoding='utf-8')

patch=r'''
function unlockAllCourseNameInputs(){
  const rows=[...document.querySelectorAll('#courseRows .course-row')];
  rows.forEach((row,index)=>{
    const input=row.querySelector('input[type="text"]');
    const cat=state&&Array.isArray(state.categories)?state.categories[index]:null;
    if(!input||!cat)return;
    input.disabled=false;
    input.readOnly=false;
    input.removeAttribute('disabled');
    input.removeAttribute('readonly');
    if(input.dataset.courseNameUnlocked==='1')return;
    input.dataset.courseNameUnlocked='1';
    const commitName=()=>{
      const name=String(input.value||'').trim();
      if(!name||name===cat.name)return;
      cat.name=name;
      save();
      render();
    };
    input.addEventListener('change',commitName);
    input.addEventListener('blur',commitName);
  });
}
function initUnlockedCourseNames(){
  const rows=$('courseRows');
  if(rows){
    new MutationObserver(()=>unlockAllCourseNameInputs()).observe(rows,{childList:true,subtree:true});
  }
  const btn=$('manageCoursesBtn');
  if(btn)btn.addEventListener('click',()=>setTimeout(unlockAllCourseNameInputs,0));
  setTimeout(unlockAllCourseNameInputs,0);
}
initUnlockedCourseNames();
'''.strip()

if 'function unlockAllCourseNameInputs()' not in js:
    js += '\n' + patch + '\n'

app.write_text(js,encoding='utf-8')
print('Course names unlocked for editing')
