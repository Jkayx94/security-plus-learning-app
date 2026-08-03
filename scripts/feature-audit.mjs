import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2] || 'dist';
const expectedVersion = process.env.APP_VERSION || '2.2.1';
const read = p => fs.readFileSync(path.join(root,p),'utf8');
const exists = p => fs.existsSync(path.join(root,p));
const failures=[];
const check=(ok,msg)=>{if(!ok)failures.push(msg);};

for(const file of ['index.html','assets/app.js','assets/styles.css','manifest.webmanifest','sw.js','icons/icon-192.png','icons/icon-512.png','data/sy0-701-curriculum-v1.2.json','data/sy0-701-learning-units-v1.2.json']) check(exists(file),`Missing ${file}`);
if(failures.length){console.error(failures.join('\n'));process.exit(1)}

const app=read('assets/app.js');
const css=read('assets/styles.css');
const sw=read('sw.js');
const manifest=JSON.parse(read('manifest.webmanifest'));
const curriculum=JSON.parse(read('data/sy0-701-curriculum-v1.2.json'));
const units=JSON.parse(read('data/sy0-701-learning-units-v1.2.json'));
const records=curriculum.records||[];

check(records.filter(r=>r.recordClass==='assessable_concept').length===578,'Expected 578 assessable concepts');
check(records.filter(r=>r.recordClass==='acronym').length===336,'Expected 336 acronym records');
check((units.learningUnits||[]).length===101,'Expected 101 learning units');
check(app.includes('What should we call you'),'Onboarding missing');
check(app.includes('PROFILE_KEY'),'Profile persistence missing');
check(app.includes('Download JSON backup'),'Export control missing');
check(app.includes('id="import"'),'Import control missing');
check(app.includes('Reset all local progress'),'Reset control missing');
check(app.includes('Acronym trainer'),'Acronym mode missing');
check(app.includes('Exam mode'),'Exam mode missing');
check(app.includes('Memory bank'),'Memory bank missing');
check(app.includes('Readiness analytics'),'Dashboard missing');
check(app.includes('data-rating'),'Post-answer confidence controls missing');
check(app.includes('Did you know it?'),'Post-answer self-assessment missing');
check(app.includes('Why this answer is correct'),'Progressive explanation missing');
check(app.includes('Flag this question'),'Question flag control missing');
check(!app.includes('How confident are you?</b>'),'Pre-answer confidence still visible');
check(!app.includes('A scenario points to'), 'Invalid fabricated scenario generator remains');
check(!app.includes("compare-two-concepts',prompt"), 'Invalid generated compare activity remains');
check(css.includes('.postAnswerConfidence'),'Post-answer confidence styling missing');
check(css.includes('.explanationPanel'),'Explanation dropdown styling missing');
check(css.includes('body:has(.questionScreen) nav'),'Question navigation suppression missing');
check(sw.includes(`security-plus-v${expectedVersion}`),'Service-worker cache not bumped');
check(app.includes(expectedVersion),'Visible app version not bumped');
check(manifest.name?.includes('Security+'),'Manifest name invalid');
check(manifest.start_url,'Manifest start_url missing');
check(manifest.display==='standalone','Manifest is not standalone');

const handlers=['data-nav','data-start','data-unit','data-option','data-rating','save-cue','save-note','start-exam','export','reset','complete-onboarding','save-profile-settings'];
for(const h of handlers) check(app.includes(h),`Expected interaction missing: ${h}`);

if(failures.length){console.error('Feature audit failed:\n- '+failures.join('\n- '));process.exit(1)}
console.log('Feature audit passed');
console.log(JSON.stringify({concepts:578,acronyms:336,units:101,version:expectedVersion,checkedFeatures:handlers.length},null,2));
