/* Import privately into local state from TimeEdit iCalendar files. */
const TE_DEFAULT_LINK='';
let teImportPreview=null;
function teStatus(message,error=false){
  const el=document.getElementById('timeeditImportStatus');
  if(!el)return;
  el.textContent=message;el.classList.toggle('te-import-error',!!error);
}
function teCourseForEvent(item){
  const s=(item.title+' '+item.description).toLowerCase();
  if(/datorsystemteknik|datorsystem/.test(s))return 'DATORSYSTEM1';
  if(/elektronik/.test(s))return 'ELEKTRONIK';
  return 'OTHER';
}
function teEnsureCategories(items){
  const need=new Set(items.map(teCourseForEvent));
  const categories=[
    {id:'ELEKTRONIK',name:'Elektronik',color:'#88b647'},
    {id:'DATORSYSTEM1',name:'Datorsystemteknik I',color:'#f197c4'}
  ];
  for(const c of categories)if(need.has(c.id)&&!state.categories.some(x=>x.id===c.id))state.categories.push({...c,locked:false});
}
function teIdentity(item){return teStableId(item.uid)}
function tePrepare(text){
  const parsed=teParseIcs(text);
  if(!parsed.found)throw Error('Filen innehåller inga kalenderposter.');
  if(!parsed.events.length)throw Error('Inga schemapass med giltig tid hittades.');
  const existing=new Set(state.events.map(e=>e.id));
  const similar=new Set(state.events.filter(e=>e.origin==='timeedit').map(e=>[e.date,e.start,e.end,String(e.title||'').trim().toLowerCase()].join('|')));
  const seen=new Set();
  const pending=parsed.events.filter(item=>{
    const id=teIdentity(item),key=[item.date,item.start,item.end,item.title.trim().toLowerCase()].join('|');
    if(existing.has(id)||similar.has(key)||seen.has(id))return false;
    seen.add(id);return true;
  });
  teImportPreview={parsed,pending};
  const counts={ELEKTRONIK:0,DATORSYSTEM1:0,OTHER:0};
  pending.forEach(e=>counts[teCourseForEvent(e)]++);
  document.getElementById('timeeditConfirmImport').disabled=!pending.length;
  const parts=['Hittade '+parsed.found+' poster.',pending.length+' nya schemapass.',
    'Elektronik: '+counts.ELEKTRONIK,'Datorsystemteknik: '+counts.DATORSYSTEM1,'Övrigt: '+counts.OTHER,
    (parsed.events.length-pending.length)+' dubbletter.'];
  if(parsed.unsupported)parts.push(parsed.unsupported+' återkommande serier i ej stött format.');
  teStatus(parts.join(' '));
}
async function teSelectFile(file){
  if(!file)return;
  try{
    if(file.size>10000000)throw Error('Maximal filstorlek är 10 MB.');
    tePrepare(await file.text());
  }catch(e){
    teImportPreview=null;document.getElementById('timeeditConfirmImport').disabled=true;
    teStatus(String(e.message||e),true);
  }
}
function teIcsUrl(input){
  let u;try{u=new URL(input.trim())}catch(_){throw Error('Ange en giltig TimeEdit-länk.')}
  if(u.protocol!=='https:'||u.hostname!=='cloud.timeedit.net')throw Error('Direkthämtning kräver en säker länk till cloud.timeedit.net.');
  if(u.pathname.toLowerCase().endsWith('.html'))u.pathname=u.pathname.slice(0,-5)+'.ics';
  if(!u.pathname.toLowerCase().endsWith('.ics'))throw Error('TimeEdit behöver exporteras i ICS-format.');
  u.hash='';return u.href;
}
async function teFetchFile(){
  const btn=document.getElementById('timeeditFetchBtn');
  btn.disabled=true;teStatus('Hämtar schema…');
  try{
    const u=teIcsUrl(document.getElementById('timeeditImportUrl').value);
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),16000);
    let response;
    try{response=await fetch(u,{mode:'cors',credentials:'omit',signal:controller.signal,cache:'no-store'})}
    finally{clearTimeout(timer)}
    if(!response.ok)throw Error('HTTP '+response.status);
    tePrepare(await response.text());
  }catch(e){
    teImportPreview=null;document.getElementById('timeeditConfirmImport').disabled=true;
    teStatus('Direkthämtning misslyckades. Exportera schemat som .ics från TimeEdit och välj filen här. Orsak: '+String(e.message||e),true);
  }finally{btn.disabled=false}
}
function teCommit(){
  if(STUDIEPLAN_VIEW_MODE||!teImportPreview||!teImportPreview.pending.length)return;
  const pending=teImportPreview.pending;
  teEnsureCategories(pending);
  const events=pending.map(item=>{
    const cat=teCourseForEvent(item);
    const found=state.categories.find(c=>c.id===cat);
    return {
      id:teIdentity(item),date:item.date,start:item.start,end:item.end,title:item.title,
      categoryId:cat,course:found?found.name:'Övrigt',kind:'timeedit',origin:'timeedit',
      sourceUid:item.sourceUid,stage:'Importerad från TimeEdit',
      description:item.description,showDescription:true,editable:true,
      planned:false,status:'planned',statusComment:'',reminders:[]
    };
  });
  state.events.push(...events);save();render();
  const count=events.length;
  teImportPreview=null;document.getElementById('timeeditConfirmImport').disabled=true;
  teStatus(count+' schemapass importerade. Samtliga går att redigera och är märkta TimeEdit.');
}
function teMarkEvents(){
  document.querySelectorAll('#calendar .event.timeedit').forEach(el=>{
    if(el.querySelector('.te-source-marker'))return;
    const badge=document.createElement('span');
    badge.className='te-source-marker';badge.textContent='TIMEEDIT';el.appendChild(badge);
  });
}
function initTimeEditImporter(){
  if(STUDIEPLAN_VIEW_MODE)return;
  const btn=document.getElementById('timeeditOpenImport');
  if(!btn)return;
  const dialog=document.getElementById('timeeditImportDialog');
  btn.addEventListener('click',()=>dialog.classList.remove('hidden'));
  document.getElementById('timeeditCloseImport').addEventListener('click',()=>dialog.classList.add('hidden'));
  document.getElementById('timeeditFetchBtn').addEventListener('click',teFetchFile);
  document.getElementById('timeeditFile').addEventListener('change',e=>teSelectFile(e.target.files[0]));
  document.getElementById('timeeditConfirmImport').addEventListener('click',teCommit);
  document.getElementById('timeeditImportUrl').value=TE_DEFAULT_LINK;
  const oldRender=renderCalendarEnhanced;
  renderCalendarEnhanced=function(){oldRender();teMarkEvents()};
  teMarkEvents();
}
initTimeEditImporter();
