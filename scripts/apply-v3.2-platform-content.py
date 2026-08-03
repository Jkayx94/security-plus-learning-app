from pathlib import Path
import re,sys
app=Path(sys.argv[1]); s=app.read_text(encoding='utf-8')
if "APP_VERSION='3.2.0'" in s: sys.exit(0)
s="import {loadContentPack,eligibleQuestions} from './content/loader.js';\nimport type {SecurityPlusContentPack,ContentQuestion} from './content/types.js';\n"+s
s=re.sub(r"const APP_VERSION='[^']+'", "const APP_VERSION='3.2.0'", s, count=1)
s=s.replace("schemaVersion:'3.1.0'","schemaVersion:'3.2.0'").replace("schemaVersion='3.1.0'","schemaVersion='3.2.0'").replace("schemaVersion:'3.0.2'","schemaVersion:'3.2.0'").replace("schemaVersion='3.0.2'","schemaVersion='3.2.0'")
s=s.replace("let curriculum:any, units:any, records:any[]=[], concepts:any[]=[], acronyms:any[]=[], assessable:any[]=[],", "let curriculum:any, units:any, records:any[]=[], concepts:any[]=[], acronyms:any[]=[], assessable:any[]=[], contentPack:SecurityPlusContentPack,")
start=s.index('function makeActivity('); end=s.index('function start(',start)
replacement=r'''function toActivity(q:ContentQuestion,why:string):Activity{return {id:q.questionId,conceptId:q.conceptId,unitId:q.unitId,type:q.activityType,prompt:q.prompt,options:[...q.options].sort(()=>Math.random()-.5),correct:[q.correctAnswer],reason:q.shortExplanation,distractorReasons:q.explanations,memoryCue:q.memoryCue,examTrap:q.examTip,microsoftExample:q.microsoftExample||'',mspExample:q.mspExample||'',selectionReason:why,qualityStatus:q.review.approvedForExam?'approved':q.review.approvedForBoss?'reviewed':'reviewed',difficulty:q.difficulty,objective:q.objective,commonWrongTemptation:'This option is plausible because it belongs to the same decision space, but a detail in the scenario rules it out.',sourceRefs:['approved-curriculum-v1.2'],contentVersion:q.contentVersion};}
function scoreQuestion(q:ContentQuestion,mode:string){const p=state.progress[q.conceptId]||blank(q.conceptId);return (p.nextReview&&new Date(p.nextReview)<=new Date()?45:0)+(p.stage==='unseen'?20:0)+(100-p.mastery)*.35+p.misconceptions.length*8+(mode==='mistakes'&&p.attempts>p.correct?80:0)+(mode==='low-confidence'&&p.guesses>0?80:0)+Math.random()*8}
function createSession(minutes:number,mode='adaptive'):Session{
 const boss=mode==='boss'||mode.startsWith('boss-'),exam=mode==='exam';
 const contentMode=exam?'exam':boss?'boss':'learn';let pool=eligibleQuestions(contentPack,contentMode);
 if(mode==='due')pool=pool.filter(q=>state.progress[q.conceptId]?.nextReview&&new Date(state.progress[q.conceptId].nextReview!)<=new Date());
 if(mode==='mistakes')pool=pool.filter(q=>{const p=state.progress[q.conceptId];return p&&(p.attempts>p.correct||p.misconceptions.length>0)});
 if(mode==='low-confidence')pool=pool.filter(q=>{const p=state.progress[q.conceptId];return p&&(p.guesses>0||(p.attempts>0&&p.confidenceAccuracy<55))});
 if(mode==='comparison')pool=pool.filter(q=>q.activityType==='compare'||state.progress[q.conceptId]?.misconceptions.length);
 if(!pool.length)throw Error(exam?'Exam Mode has no approved questions yet. Reviewed content will be added in the editorial releases.':'No reviewed questions are currently available for this session. Open Learn to study a concept instead.');
 const bossType:(Session['bossType'])=mode==='boss-final'?'final':mode==='boss-domain'?'domain':mode==='boss-objective'?'objective':'unit';
 const counts={unit:5,objective:8,domain:12,final:15},thresholds={unit:70,objective:75,domain:80,final:85},rewards={unit:10,objective:25,domain:75,final:150};
 const count=boss?counts[bossType!]:Math.max(1,Math.min(pool.length,Math.ceil(minutes*(minutes<=1?1:1.1))));
 const recentConcepts:string[]=[];const recentPrompts=new Set<string>();const picked:ContentQuestion[]=[];
 for(const q of [...pool].sort((a,b)=>scoreQuestion(b,mode)-scoreQuestion(a,mode))){if(recentPrompts.has(q.prompt))continue;if(recentConcepts.slice(-10).includes(q.conceptId))continue;picked.push(q);recentPrompts.add(q.prompt);recentConcepts.push(q.conceptId);if(picked.length>=count)break}
 const activities=picked.map(q=>toActivity(q,boss?'Boss milestone':mode==='mistakes'?'Previous mistake':mode==='low-confidence'?'Low-confidence evidence':mode==='comparison'?'Comparison practice':'Reviewed learning content'));
 const session:Session={id:id(),minutes,mode,activities,index:0,startedAt:iso()};if(boss){session.bossType=bossType;session.bossId=`${bossType}:${activities[0]?.unitId||'reviewed'}`;session.bossThreshold=thresholds[bossType!];session.bossCorrect=0;session.bossReward=rewards[bossType!]}
 return session;
}
'''
s=s[:start]+replacement+s[end:]
# learner lesson uses content pack, otherwise concept card
ls=s.index('function lesson()'); le=s.index('function session()',ls)
lesson=r'''function lesson(){const ids=[...currentUnit.conceptIds,...(currentUnit.acronymMappings||[]).filter((x:any)=>x.relationship==='core').map((x:any)=>x.acronymId)],r=records.find(x=>x.conceptId===ids[lessonIndex]),l=contentPack.lessons.find(x=>x.conceptId===r.conceptId);return shell(`<main class="shell"><div class="row"><span>${lessonIndex+1}/${ids.length}</span><span>${esc(currentUnit.name)}</span></div><div class="progress"><i style="width:${(lessonIndex+1)/ids.length*100}%"></i></div><section class="card lesson"><span class="pill">Objective ${esc(r.objective)}</span><h1>${esc(r.name)}</h1>${l?`<h3>What it is</h3><p class="lead">${esc(l.definition)}</p><h3>Why it matters</h3><p>${esc(l.purpose)}</p><h3>When it is used</h3><p>${esc(l.whenUsed)}</p><aside><b>Example</b><p>${esc(l.example)}</p></aside><div class="trap"><b>Common confusion</b><p>${esc(l.commonConfusion)}</p></div><div class="cue"><b>Memory cue</b><p>${esc(l.memoryCue)}</p></div><p><b>Exam distinction:</b> ${esc(l.examDistinction)}</p>`:`<p class="notice">A reviewed lesson for this concept is not available yet.</p><p><b>Official curriculum context:</b> ${esc(r.objectiveBranch)}</p><p>This concept will remain introduction-only until reviewed teaching content is added.</p>`}<div class="branchButtons"><button data-action="ask-ai">Explain current content</button><button data-action="save-cue">Save a note</button></div></section><div class="actions"><button data-action="lesson-prev" ${lessonIndex?'':'disabled'}>Previous</button><button class="primary" data-action="lesson-next">${lessonIndex+1===ids.length?'Complete unit':'Mark introduced and continue'}</button></div></main>`)}
'''
s=s[:ls]+lesson+s[le:]
# hide internal metadata and selection reason outside test mode
s=s.replace("<span class=\"quality ${a.qualityStatus||'generated'}\">${esc(a.qualityStatus||'generated')}</span>","${state.testMode.enabled?`<span class=\"quality\">${esc(a.qualityStatus||'reviewed')}</span>`:''}")
s=s.replace("${exam?'':`<section class=\"selectionReason\"><b>Why selected:</b> ${esc(a.selectionReason)}</section>`}","${state.testMode.enabled?`<section class=\"selectionReason\"><b>Developer selection reason:</b> ${esc(a.selectionReason)}</section>`:''}")
# More screen and navigation
insert=s.index('function reviewView()')
more=r'''function moreView(){return shell(`<main class="shell"><h1>More</h1><p>Profile, study records and application controls.</p><section class="grid">${[['settings','⚙','Profile and settings','Name, exam date, backup and reset'],['memory','✎','Memory bank','Notes and saved explanations'],['achievements','★','Achievements','Progress and unlocks'],['cosmetics','◆','Cosmetics','Themes, shields and styles'],['reports','⚑','Question reports','Review and export saved reports'],['backup','⇩','Backup and restore',state.lastBackupAt?`Last backup ${new Date(state.lastBackupAt).toLocaleDateString()}`:'No backup recorded'],['about','ⓘ','About and version',`Version ${APP_VERSION}`]].map(x=>`<button class="tile" data-nav="${x[0]}"><b>${x[1]} ${x[2]}</b><span>${x[3]}</span></button>`).join('')}</section></main>`)}
function backupView(){return shell(`<main class="shell"><h1>Backup and restore</h1><section class="card"><h2>Complete progress backup</h2><p>Includes genuine study events, progress, achievements, cosmetics, notes, reports and boss history. Test Mode data is excluded.</p><button class="primary wide" data-action="export">Export complete progress</button><p>${state.lastBackupAt?`Last backup: ${new Date(state.lastBackupAt).toLocaleString()}`:'No backup has been recorded on this device.'}</p></section><section class="card"><h2>Import progress</h2><p>Select a JSON backup. The app validates its schema and shows a migration confirmation before applying it.</p><input id="import" type="file" accept="application/json"></section><section class="card"><h2>Separate exports</h2><button data-action="export-notes">Export notes and memory bank</button><button data-action="export-reports">Export question reports</button></section><section class="card danger"><h2>Reset local progress</h2><p>This cannot be undone without a backup.</p><button data-action="reset">Reset all local progress</button></section></main>`)}
function aboutView(){return shell(`<main class="shell"><h1>About</h1><section class="card"><h2>Security+ Adaptive Learning</h2><p>Version <button class="versionTap" data-action="version-tap">${APP_VERSION}</button></p><p>Content pack ${esc(contentPack.contentVersion)} · Curriculum 1.2</p><p>${updateAvailable?'An update is ready to install.':'The application is up to date.'}</p>${developerCodeVisible&&!state.testMode.enabled?`<label>Developer code <input id="test-code" autocomplete="off"></label><button data-action="test-enable">Enable Test Mode</button>`:''}${state.testMode.enabled?`<p class="testWarning"><b>TEST MODE</b> Local QA tooling. Test activity is excluded from genuine progress and exports.</p><button data-nav="testlab">Open Developer Lab</button><button data-action="test-exit">Exit Test Mode</button>`:''}</section></main>`)}
function cosmeticsView(){return achievementsView()}
'''
s=s[:insert]+more+s[insert:]
s=s.replace('<button data-nav="dashboard">▥<small>Dashboard</small></button></nav>','<button data-nav="dashboard">▥<small>Dashboard</small></button><button data-nav="more">•••<small>More</small></button></nav>')
# render routes
old="view==='reports'?reportsView():view==='testlab'?visualTestLab():settingsView()"
new="view==='reports'?reportsView():view==='more'?moreView():view==='backup'?backupView():view==='about'?aboutView():view==='cosmetics'?cosmeticsView():view==='testlab'?visualTestLab():settingsView()"
s=s.replace(old,new)
# add export notes and version tap handlers before reset
needle="if(a==='export-reports'){"
pos=s.index(needle)
handler="if(a==='export-notes'){const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([JSON.stringify({notes:state.notes,exportedAt:iso(),schemaVersion:'3.2.0'},null,2)],{type:'application/json'}));link.download='security-plus-notes.json';link.click();toast('Notes exported successfully');return}if(a==='version-tap'){versionTapCount++;if(versionTapCount>=5){developerCodeVisible=true;toast('Developer code entry enabled')}render();return}"
s=s[:pos]+handler+s[pos:]
# boot content loader
s=s.replace("records=curriculum.records;", "contentPack=loadContentPack();records=curriculum.records;")
# export schema and test exclusion already present; update strings
s=s.replace("schemaVersion:'3.0.2'","schemaVersion:'3.2.0'").replace("schemaVersion:'3.1.0'","schemaVersion:'3.2.0'")
app.write_text(s,encoding='utf-8')
css=Path(sys.argv[2]); c=css.read_text(encoding='utf-8');c+='\nnav{grid-template-columns:repeat(5,1fr)}.versionTap{display:inline;min-height:44px}.testWarning{border-left:4px solid #f5a623;padding-left:12px}\n';css.write_text(c,encoding='utf-8')
