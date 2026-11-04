const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source='let teMigrationChanged=false;\n'+fs.readFileSync(process.argv[2],'utf8');
const context={};vm.createContext(context);vm.runInContext(source,context);
const clean=vm.runInContext('teCleanTimeEditTitle',context);
const normalize=vm.runInContext('teNormalizeImportedEvent',context);
assert.equal(
 clean('Kurs: Datorsystemteknik I, Hazem Ali, Aktivitet: Föreläsning, Information: HW','DATORSYSTEM1'),
 'Datorsystemteknik I, Föreläsning, HW'
);
assert.equal(
 clean('Kurs: Elektronik, Aktivitet: Övning, Information: Lödning, 2h/student','ELEKTRONIK'),
 'Elektronik, Övning, Lödning, 2h/student'
);
assert.equal(
 clean('Kurs: Datorsystemteknik I, Hazem Ali, Aktivitet: Föreläsning, Information: HW','OTHER'),
 'Datorsystemteknik I, Föreläsning, HW'
);
assert.equal(
 clean('Kurs: Elektronik, Aktivitet: Laboration, Information: Lödning, Hazem Ali, 2h/student','ELEKTRONIK'),
 'Elektronik, Laboration, Lödning, 2h/student'
);
const custom={origin:'custom',title:'Kurs: Min kurs, Hazem Ali, Aktivitet: Övning',showDescription:true};
const unchanged=normalize(custom);
assert.equal(unchanged.title,custom.title);
assert.equal(unchanged.showDescription,true);
const old={origin:'timeedit',title:'Kurs: Elektronik, Aktivitet: Övning, Information: Lödning, 2h/student',categoryId:'ELEKTRONIK',showDescription:true};
const migrated=normalize(old);
assert.equal(migrated.title,'Elektronik, Övning, Lödning, 2h/student');
assert.equal(migrated.showDescription,false);
assert.equal(migrated.teDescriptionDefaultV1,true);
assert.equal(migrated.teCleanedTitleV1,true);
const once=normalize({...migrated,showDescription:true,title:'Elektronik, ändrad av mig'});
assert.equal(once.showDescription,true);
assert.equal(once.title,'Elektronik, ändrad av mig');
assert.equal(old.title,'Kurs: Elektronik, Aktivitet: Övning, Information: Lödning, 2h/student');
console.log('TimeEdit title cleanup and description default tests passed');
