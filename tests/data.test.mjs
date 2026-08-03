import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));const c=read('src/data/sy0-701-curriculum-v1.2.json');const u=read('src/data/sy0-701-learning-units-v1.2.json');
test('authoritative record counts',()=>{assert.equal(c.records.filter(x=>x.recordClass==='assessable_concept').length,578);assert.equal(c.records.filter(x=>x.recordClass==='acronym').length,336);assert.equal(u.learningUnits.length,101)});
test('all unit concept references resolve',()=>{const ids=new Set(c.records.map(x=>x.conceptId));for(const unit of u.learningUnits)for(const id of unit.conceptIds)assert.ok(ids.has(id),`${unit.unitId}:${id}`)});
test('all objective concepts have a learning unit',()=>{const mapped=new Set(u.learningUnits.flatMap(x=>x.conceptIds));for(const r of c.records.filter(x=>x.recordClass==='assessable_concept'))assert.ok(mapped.has(r.conceptId),r.conceptId)});
