const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx={Intl,Date,Math,Error,Number,String,Set,Array};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),ctx,{filename:'timeedit_ics_parser.js'});
const parse=vm.runInContext('teParseIcs',ctx);
const id=vm.runInContext('teStableId',ctx);
const ics=[
'BEGIN:VCALENDAR',
'VERSION:2.0',
'BEGIN:VEVENT',
'UID:elektronik@hh.se',
'SUMMARY:Elektronik',
'DTSTART:20261104T080000Z',
'DTEND:20261104T100000Z',
'DESCRIPTION:Lektion\\nKurs: Elektronik',
'LOCATION:Sal B',
'END:VEVENT',
'BEGIN:VEVENT',
'UID:datorsystem@hh.se',
'SUMMARY:Datorsystemteknik I',
'DTSTART;TZID=Europe/Stockholm:20261105T101500',
'DTEND;TZID=Europe/Stockholm:20261105T120000',
'END:VEVENT',
'BEGIN:VEVENT',
'UID:recurring@hh.se',
'SUMMARY:Övning',
'DTSTART:20261102T090000',
'DTEND:20261102T103000',
'RRULE:FREQ=WEEKLY;COUNT=3;BYDAY=MO',
'EXDATE:20261109T090000',
'END:VEVENT',
'END:VCALENDAR'].join('\r\n');
const parsed=parse(ics);
assert.equal(parsed.found,3);
assert.equal(parsed.events.length,4);
assert.equal(parsed.events[0].date,'2026-11-04');
assert.equal(parsed.events[0].start,'09:00');
assert.equal(parsed.events[1].start,'10:15');
assert.equal(parsed.events[0].description,'Lektion\nKurs: Elektronik\nPlats: Sal B');
assert.equal(parsed.events.filter(x=>x.title==='Övning').length,2);
assert.equal(parsed.events.find(x=>x.title==='Övning'&&x.date==='2026-11-09'),undefined);
assert.equal(id(parsed.events[0].uid),id(parsed.events[0].uid));
assert.notEqual(id(parsed.events[0].uid),id(parsed.events[1].uid));
assert.throws(()=>parse('not a calendar'));
console.log('TimeEdit ICS parser: fixture tests passed');
