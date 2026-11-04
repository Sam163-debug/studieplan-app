/* Standalone TimeEdit/iCalendar parser. No external dependencies. */
function teUnescape(s) {
  return String(s||'').replace(/\\([nN,;\\])/g,(_,c)=>/[nN]/.test(c)?'\n':c);
}
function teDateParts(value) {
  const s=String(value||'').trim();
  const m=/^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})?(Z)?)?$/.exec(s);
  if(!m)return null;
  const Y=Number(m[1]),M=Number(m[2]),D=Number(m[3]),h=Number(m[4]||0),min=Number(m[5]||0),sec=Number(m[6]||0);
  const d=new Date(Date.UTC(Y,M-1,D,h,min,sec));
  if(d.getUTCFullYear()!==Y||d.getUTCMonth()!==M-1||d.getUTCDate()!==D||h>23||min>59)return null;
  if(m[7]){
    const f=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Stockholm',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
    const p={};for(const v of f.formatToParts(d))if(v.type!=='literal')p[v.type]=v.value;
    return {date:p.year+'-'+p.month+'-'+p.day,time:p.hour+':'+p.minute,allDay:false};
  }
  return {date:m[1]+'-'+m[2]+'-'+m[3],time:(m[4]||'00')+':'+(m[5]||'00'),allDay:!m[4]};
}
function teDayAdd(iso,days){
  const d=new Date(iso+'T12:00:00Z');
  d.setUTCDate(d.getUTCDate()+days);
  return d.toISOString().slice(0,10);
}
function teDateDiff(a,b){return Math.round((Date.parse(b+'T12:00:00Z')-Date.parse(a+'T12:00:00Z'))/86400000)}
function teWeekday(d){return new Date(d+'T12:00:00Z').getUTCDay()}
function teParseIcs(text){
  const raw=String(text||'');
  if(!/BEGIN:VCALENDAR/i.test(raw))throw new Error('Filen är inte en giltig ICS-kalender.');
  const lines=raw.replace(/\r\n[ \t]/g,'').replace(/\n[ \t]/g,'').split(/\r?\n/);
  const events=[];let item=null;
  for(const line of lines){
    if(/^BEGIN:VEVENT$/i.test(line.trim())){item={};continue}
    if(/^END:VEVENT$/i.test(line.trim())){if(item)events.push(item);item=null;continue}
    if(!item||!line.includes(':'))continue;
    const i=line.indexOf(':'),name=line.slice(0,i).split(';',1)[0].toUpperCase(),value=line.slice(i+1);
    (item[name]||(item[name]=[])).push(value);
  }
  const entries=[];let invalid=0,cancelled=0,unsupported=0;
  for(const e of events){
    const prop=n=>teUnescape((e[n]||[])[0]||'');
    if(prop('STATUS').toUpperCase()==='CANCELLED'){cancelled++;continue}
    const start=teDateParts(prop('DTSTART')),end=teDateParts(prop('DTEND'));
    if(!start||!end){invalid++;continue}
    const title=prop('SUMMARY').trim()||'Schemapass';
    const description=prop('DESCRIPTION').trim();
    const location=prop('LOCATION').trim();
    const uid=prop('UID')||title+'|'+start.date+'|'+start.time;
    const endTime=end.allDay?'23:59':end.time;
    const startTime=start.allDay?'00:00':start.time;
    const src={title,description:location?(description?description+'\n':'')+'Plats: '+location:description,location,uid,raw:e};
    const duration=teDateDiff(start.date,end.date);
    const create=(day)=>{const stop=(duration===0?endTime:(start.allDay?'23:59':endTime));
      if(duration===0&&stop<=startTime){invalid++;return}
      const k=day===start.date?startTime:'00:00';
      const endOnDay=day===end.date?endTime:'23:59';
      if(endOnDay<=k)return;
      entries.push({uid:uid+'|'+day,date:day,start:k,end:endOnDay,title:src.title,description:src.description,location:src.location,sourceUid:uid});
    };
    if(duration<0||duration>60){invalid++;continue}
    const rrule=prop('RRULE');
    if(rrule){
      const r={};rrule.split(';').forEach(kv=>{const i=kv.indexOf('=');if(i>0)r[kv.slice(0,i).toUpperCase()]=kv.slice(i+1)});
      const freq=(r.FREQ||'').toUpperCase(),interval=Math.max(1,Number(r.INTERVAL)||1),count=Math.min(520,Math.max(1,Number(r.COUNT)||180)),until=teDateParts(r.UNTIL||'')?.date||teDayAdd(start.date,730);
      if(!['DAILY','WEEKLY'].includes(freq)){unsupported++;continue}
      const days=['SU','MO','TU','WE','TH','FR','SA'];
      const weekdays=(r.BYDAY||days[teWeekday(start.date)]).split(',').map(d=>days.indexOf(d)).filter(d=>d>=0);
      const excluded=new Set((e.EXDATE||[]).flatMap(x=>x.split(',')).map(x=>teDateParts(x)?.date).filter(Boolean));
      let generated=0;
      for(let day=start.date,step=0;day<=until&&step<1100&&generated<count;day=teDayAdd(day,1),step++){
        const difference=teDateDiff(start.date,day);
        const matches=freq==='DAILY'?difference%interval===0:Math.floor(difference/7)%interval===0&&weekdays.includes(teWeekday(day));
        if(!matches)continue;
        generated++;
        if(excluded.has(day))continue;
        create(day);
      }
    }else {
      const exdates=new Set((e.EXDATE||[]).flatMap(x=>x.split(',')).map(x=>teDateParts(x)?.date).filter(Boolean));
      if(!exdates.has(start.date)){
        if(duration===0)create(start.date);
        else for(let day=start.date,i=0;i<=duration;i++,day=teDayAdd(day,1))create(day);
      }
    }
  }
  return {events:entries,found:events.length,invalid,cancelled,unsupported};
}
function teStableId(input){
  let h=2166136261;
  const text=String(input||'');
  for(let i=0;i<text.length;i++){h=Math.imul(h^text.charCodeAt(i),16777619)}
  return 'timeedit-ics-'+(h>>>0).toString(36);
}
