import fs from 'node:fs';import path from 'node:path';
const read=p=>JSON.parse(fs.readFileSync(path.resolve(p),'utf8'));
const c=read('src/data/sy0-701-curriculum-v1.2.json');const u=read('src/data/sy0-701-learning-units-v1.2.json');const l=read('src/data/prototype-lessons-unit-1.1.json');const q=read('src/data/prototype-question-bank-unit-1.1.json');
const errors=[];const records=c.records||[];const ids=new Set(records.map(r=>r.conceptId));const objective=records.filter(r=>r.recordClass==='assessable_concept');const acr=records.filter(r=>r.recordClass==='acronym');
if(objective.length!==578)errors.push(`objective concepts ${objective.length}/578`);if(acr.length!==336)errors.push(`acronyms ${acr.length}/336`);if((u.learningUnits||[]).length!==101)errors.push(`units ${u.learningUnits?.length}/101`);
const seen=new Set();for(const unit of u.learningUnits||[]){if(seen.has(unit.unitId))errors.push(`duplicate unit ${unit.unitId}`);seen.add(unit.unitId);if(!unit.conceptIds?.length)errors.push(`empty unit ${unit.unitId}`);for(const id of unit.conceptIds||[])if(!ids.has(id))errors.push(`${unit.unitId} -> missing ${id}`);for(const m of unit.acronymMappings||[])if(!ids.has(m.acronymId))errors.push(`${unit.unitId} -> missing acronym ${m.acronymId}`);}
const mapped=new Set((u.learningUnits||[]).flatMap(x=>x.conceptIds));for(const r of objective)if(!mapped.has(r.conceptId))errors.push(`unmapped concept ${r.conceptId}`);
for(const item of q.questions||[]){if(!item.answerOptions?.includes(item.correctAnswer))errors.push(`invalid correct mapping ${item.questionId}`);for(const id of item.conceptIds||[])if(!ids.has(id))errors.push(`question missing concept ${id}`);}
if((q.questions||[]).length!==30)errors.push(`prototype questions ${q.questions?.length}/30`);if((l.lessons||[]).length!==2)errors.push(`prototype lessons ${l.lessons?.length}/2`);
if(errors.length){console.error('VALIDATION FAILED\n'+errors.slice(0,50).join('\n'));process.exit(1)}
console.log(`VALIDATION PASSED: ${objective.length} objective concepts, ${acr.length} acronyms, ${u.learningUnits.length} units, ${q.questions.length} prototype questions.`);
