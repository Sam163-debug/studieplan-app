/* TimeEdit event display cleanup: preserve user-created titles. */
function teLooksLikePerson(value){
  const text=String(value||'').trim();
  // A free-standing two-to-four-token personal name, e.g. "Hazem Ali".
  // Typed course names are handled separately.
  return /^[A-ZÅÄÖ][a-zåäöéèüû'-]+(?:[\s-]+[A-ZÅÄÖ][a-zåäöéèüû'-]+){1,3}$/u.test(text);
}
function teCleanTimeEditTitle(input,categoryId){
  const original=String(input||'').trim();
  if(!/\b(?:kurs|aktivitet|information)\s*:/i.test(original))return original;
  const fieldPattern=/\b(kurs|aktivitet|information|lärare|föreläsare|teacher|lecturer|person|personal|plats|lokal|grupp)\s*:/gi;
  const matches=Array.from(original.matchAll(fieldPattern));
  const fields={};
  matches.forEach((m,i)=>{
    const key=m[1].toLocaleLowerCase('sv-SE');
    const end=i+1<matches.length?matches[i+1].index:original.length;
    const value=original.slice(m.index+m[0].length,end).replace(/^[\s,;|]+|[\s,;|]+$/g,'').trim();
    if(value && ['kurs','aktivitet','information'].includes(key))fields[key]=fields[key]?fields[key]+', '+value:value;
  });
  const courseFromCategory=categoryId==='ELEKTRONIK'?'Elektronik':categoryId==='DATORSYSTEM1'?'Datorsystemteknik I':'';
  const rawCourse=String(fields.kurs||'').trim();
  const course=courseFromCategory ||
    (/datorsystemteknik\s*(?:i|1)?/i.exec(rawCourse)?.[0] || /elektronik/i.exec(rawCourse)?.[0] || rawCourse.split(',')[0] || '').trim();
  const activity=(fields.aktivitet||'').split(',').map(x=>x.trim()).find(Boolean)||'';
  const info=String(fields.information||'').split(',').map(x=>x.trim()).filter(x=>x&&!teLooksLikePerson(x)).join(', ');
  const values=[course,activity,info].filter(Boolean);
  return values.length?values.join(', '):original;
}
function teNormalizeImportedEvent(event){
  if(!event||event.origin!=='timeedit')return event;
  const updated={...event};
  if(!updated.teCleanedTitleV1){
    if(/\b(?:kurs|aktivitet|information)\s*:/i.test(updated.title||'')){
      updated.title=teCleanTimeEditTitle(updated.title,updated.categoryId);
    }
    updated.teCleanedTitleV1=true;
    teMigrationChanged=true;
  }
  // The old ICS import defaulted to "show", so migrate existing imports
  // once. From then on, an explicit checkbox selection is authoritative.
  if(!updated.teDescriptionDefaultV1){
    updated.showDescription=false;
    updated.teDescriptionDefaultV1=true;
    teMigrationChanged=true;
  }
  return updated;
}
