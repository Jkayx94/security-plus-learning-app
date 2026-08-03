from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit('Usage: apply-v3-progression-balance.py <app.ts> <styles.css>')
app_path=Path(sys.argv[1]); css_path=Path(sys.argv[2])
text=app_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')

# Extend session and persistent state contracts.
text=text.replace(
"type Session={id:string,minutes:number,mode:string,activities:Activity[],index:number,startedAt:string};",
"type Session={id:string,minutes:number,mode:string,activities:Activity[],index:number,startedAt:string,bossId?:string,bossType?:'unit'|'objective'|'domain'|'final',bossThreshold?:number,bossCorrect?:number,bossReward?:number,testOnly?:boolean};")
text=text.replace(
"lastBackupAt:string|null,activeSession?:Session};",
"lastBackupAt:string|null,rewardedEventIds:string[],bossClaims:string[],bossHistory:{bossId:string,bossType:string,score:number,passed:boolean,completedAt:string}[],testMode:{enabled:boolean,coins:number,unlockedCosmetics:string[],previewShield:string|null},activeSession?:Session};")
text=text.replace(
"lastBackupAt:null}}",
"lastBackupAt:null,rewardedEventIds:[],bossClaims:[],bossHistory:[],testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null}}}")
text=text.replace(
"merged.lastBackupAt=s?.lastBackupAt||null;merged.schemaVersion='3.0.0';",
"merged.lastBackupAt=s?.lastBackupAt||null;merged.rewardedEventIds=Array.isArray(s?.rewardedEventIds)?s.rewardedEventIds:[];merged.bossClaims=Array.isArray(s?.bossClaims)?s.bossClaims:[];merged.bossHistory=Array.isArray(s?.bossHistory)?s.bossHistory:[];merged.testMode={enabled:false,coins:0,unlockedCosmetics:[],previewShield:null,...(s?.testMode||{})};merged.schemaVersion='3.0.0';")

# Replace generous achievements with slower, evidence-based progression.
text=re.sub(r"const achievementDefs=\[.*?\n\];\nfunction checkAchievements\(\).*?\n\nfunction save", """const achievementDefs=[
  {id:'first-lesson',name:'First Lesson',coins:2,test:()=>state.events.some(e=>e.type==='concept_introduced')},
  {id:'first-correct',name:'First Correct Answer',coins:2,test:()=>state.events.some(e=>e.type==='activity_answered'&&e.payload.correct===true)},
  {id:'first-understood',name:'First Concept Understood',coins:5,test:()=>Object.values(state.progress).some(p=>['understood','applied','retained','exam-ready'].includes(p.stage))},
  {id:'ten-concepts',name:'10 Concepts Introduced',coins:5,test:()=>Object.values(state.progress).filter(p=>p.stage!=='unseen').length>=10},
  {id:'hundred-questions',name:'100 Questions Answered',coins:15,test:()=>state.events.filter(e=>e.type==='activity_answered').length>=100},
  {id:'five-hundred-questions',name:'500 Questions Answered',coins:35,test:()=>state.events.filter(e=>e.type==='activity_answered').length>=500},
  {id:'seven-day-streak',name:'Seven Day Streak',coins:15,test:()=>state.streak>=7},
  {id:'thirty-day-streak',name:'Thirty Day Streak',coins:40,test:()=>state.streak>=30},
  {id:'first-boss',name:'First Boss Defeated',coins:10,test:()=>state.bossHistory.some(b=>b.passed)},
  {id:'boss-perfect',name:'Boss Battle Perfect Score',coins:20,test:()=>state.bossHistory.some(b=>b.passed&&b.score===100)},
  {id:'acronym-apprentice',name:'Acronym Apprentice',coins:8,test:()=>acronyms.filter(r=>state.progress[r.conceptId]?.stage!=='unseen').length>=50},
  {id:'acronym-expert',name:'Acronym Expert',coins:25,test:()=>acronyms.filter(r=>['retained','exam-ready'].includes(state.progress[r.conceptId]?.stage)).length>=200}
];
function awardOnce(key:string,coins:number,eventType:string,payload:Record<string,unknown>={}){if(state.rewardedEventIds.includes(key))return false;state.rewardedEventIds.push(key);state.coins+=coins;state.events.push(emit(eventType,[],{...payload,coinReward:coins,rewardKey:key}));return true}
function checkAchievements(){for(const a of achievementDefs)if(!state.achievements.includes(a.id)&&a.test()){state.achievements.push(a.id);awardOnce(`achievement:${a.id}`,a.coins,'achievement_unlocked',{achievementId:a.id});toastMessage=`Achievement unlocked: ${a.name} (+${a.coins} coins)`;toastKind='achievement'}}
const shieldTiers=[
  {id:'shield-bronze',name:'Bronze',requires:'10 concepts understood',test:()=>Object.values(state.progress).filter(p=>['understood','applied','retained','exam-ready'].includes(p.stage)).length>=10},
  {id:'shield-silver',name:'Silver',requires:'40 understood, 10 retained and one boss',test:()=>Object.values(state.progress).filter(p=>['understood','applied','retained','exam-ready'].includes(p.stage)).length>=40&&Object.values(state.progress).filter(p=>['retained','exam-ready'].includes(p.stage)).length>=10&&state.bossHistory.some(b=>b.passed)},
  {id:'shield-gold',name:'Gold',requires:'100 understood, 40 retained and three bosses',test:()=>Object.values(state.progress).filter(p=>['understood','applied','retained','exam-ready'].includes(p.stage)).length>=100&&Object.values(state.progress).filter(p=>['retained','exam-ready'].includes(p.stage)).length>=40&&state.bossHistory.filter(b=>b.passed).length>=3},
  {id:'shield-platinum',name:'Platinum',requires:'200 retained, 70% first-attempt accuracy and a domain boss',test:()=>Object.values(state.progress).filter(p=>['retained','exam-ready'].includes(p.stage)).length>=200&&firstAttemptAccuracy()>=70&&state.bossHistory.some(b=>b.passed&&b.bossType==='domain')},
  {id:'shield-diamond',name:'Diamond',requires:'350 retained and three domain bosses',test:()=>Object.values(state.progress).filter(p=>['retained','exam-ready'].includes(p.stage)).length>=350&&state.bossHistory.filter(b=>b.passed&&b.bossType==='domain').length>=3},
  {id:'shield-master',name:'Security+ Master',requires:'500 exam-ready concepts and final boss',test:()=>Object.values(state.progress).filter(p=>p.stage==='exam-ready').length>=500&&state.bossHistory.some(b=>b.passed&&b.bossType==='final')}
];
function firstAttemptAccuracy(){const a=state.events.filter(e=>e.type==='activity_answered'&&!e.payload.testOnly);return a.length?Math.round(a.filter(e=>e.payload.correct===true&&Number(e.payload.attempts||1)===1).length/a.length*100):0}

function save""", text, flags=re.S)

# Boss creation and completion.
text=re.sub(r"function createSession\(minutes:number,mode='adaptive'\):Session\{.*?\n\}", """function createSession(minutes:number,mode='adaptive'):Session{
  const now=new Date(),all=mode==='acronym'?acronyms:assessable;
  let pool=all;
  if(mode==='due')pool=all.filter(r=>state.progress[r.conceptId].nextReview&&new Date(state.progress[r.conceptId].nextReview!)<=now);
  if(mode==='mistakes')pool=all.filter(r=>{const p=state.progress[r.conceptId];return p.attempts>p.correct||p.misconceptions.length>0});
  if(mode==='low-confidence')pool=all.filter(r=>state.progress[r.conceptId].guesses>0||state.progress[r.conceptId].confidenceAccuracy<55&&state.progress[r.conceptId].attempts>0);
  if(mode==='comparison')pool=all.filter(r=>state.progress[r.conceptId].misconceptions.length>0);
  if(mode==='exam')pool=all.filter(r=>makeActivity(r,'Exam coverage').qualityStatus==='approved');
  if(!pool.length&&mode==='exam')throw Error('Exam Mode currently requires approved authored questions. Use adaptive or boss mode while the approved bank is expanded.');
  if(!pool.length)pool=all;
  const boss=mode==='boss'||mode.startsWith('boss-');
  const bossType:(Session['bossType'])=mode==='boss-final'?'final':mode==='boss-domain'?'domain':mode==='boss-objective'?'objective':'unit';
  const bossCounts={unit:7,objective:10,domain:12,final:15},thresholds={unit:70,objective:75,domain:80,final:85},rewards={unit:15,objective:30,domain:85,final:100};
  const count=boss?bossCounts[bossType!]:Math.max(1,Math.min(mode==='exam'?90:30,Math.ceil(minutes*(mode==='exam'?1.35:minutes<=1?1:1.1))));
  const ranked=pool.map(r=>({r,p:state.progress[r.conceptId],s:score(r,state.progress[r.conceptId],mode)})).sort((a,b)=>b.s-a.s).slice(0,count);
  const activities=ranked.map(x=>makeActivity(x.r,boss?'Boss battle milestone':mode==='mistakes'?'Selected from previous mistakes':mode==='low-confidence'?'Selected from low-confidence evidence':mode==='comparison'?'Selected for confusion-pair practice':x.p.nextReview&&new Date(x.p.nextReview)<=now?'Overdue review':x.p.stage==='unseen'?'Never introduced':x.p.misconceptions.length?'Active misconception':x.p.mastery<55?'Weak mastery':'High-priority reinforcement')).sort(()=>Math.random()-.5);
  if(boss&&activities.length){activities[0].type='comparison-check';if(activities[1])activities[1].type='scenario-classification';if(activities[2])activities[2].type='pbq-style-classification'}
  const session:Session={id:id(),minutes,mode,activities,index:0,startedAt:iso()};
  if(boss){session.bossType=bossType;session.bossId=`${bossType}:${activities.map(a=>a.unitId).sort()[0]||'mixed'}`;session.bossThreshold=thresholds[bossType!];session.bossCorrect=0;session.bossReward=rewards[bossType!]}
  return session;
}""", text, count=1, flags=re.S)

text=text.replace("function start(minutes:number,mode='adaptive'){state.activeSession=createSession(minutes,mode);", "function start(minutes:number,mode='adaptive',testOnly=false){state.activeSession=createSession(minutes,mode);state.activeSession.testOnly=testOnly;")

# Add boss completion helper before resetActivity.
text=text.replace("function resetActivity(){", """function completeBoss(s:Session){
  if(!s.bossId||!s.bossType)return;
  const total=s.activities.length,score=Math.round((s.bossCorrect||0)/Math.max(1,total)*100),passed=score>=(s.bossThreshold||70);
  if(s.testOnly){toast(`TEST MODE boss preview complete: ${score}%`);return}
  state.bossHistory.push({bossId:s.bossId,bossType:s.bossType,score,passed,completedAt:iso()});
  state.events.push(emit('boss_battle_completed',s.activities.map(a=>a.conceptId),{bossId:s.bossId,bossType:s.bossType,total,correct:s.bossCorrect||0,score,threshold:s.bossThreshold,passed}));
  if(passed&&!state.bossClaims.includes(s.bossId)){state.bossClaims.push(s.bossId);awardOnce(`boss:${s.bossId}`,s.bossReward||0,'boss_reward_claimed',{bossId:s.bossId,bossType:s.bossType});toast(`Boss defeated · ${score}% · +${s.bossReward} coins`,'achievement')}else if(passed)toast(`Boss defeated · ${score}% · reward already claimed`);else toast(`Boss survived · ${score}% · ${s.bossThreshold}% required. Retry when ready.`,'error');
}
function resetActivity(){""")

# Boss health UI and proper completion.
text=text.replace("if(!a){delete state.activeSession;checkAchievements();save();view='dashboard';return dashboard()}", "if(!a){if(s.bossId)completeBoss(s);delete state.activeSession;checkAchievements();save();view='dashboard';return dashboard()}")
text=text.replace("<div class=\"progress\"><i style=\"width:${(s.index+1)/s.activities.length*100}%\"></i></div>", "<div class=\"progress\"><i style=\"width:${(s.index+1)/s.activities.length*100}%\"></i></div>${s.bossId?`<section class=\"bossHud\" aria-label=\"Boss health\"><div class=\"bossTitle\"><b>${esc(s.bossType)} boss</b><span>${s.bossThreshold}% required</span></div><div class=\"bossHealth\"><i style=\"width:${Math.max(0,100-((s.bossCorrect||0)/Math.max(1,s.activities.length)*100))}%\"></i></div><small>Boss health · ${Math.round(Math.max(0,100-((s.bossCorrect||0)/Math.max(1,s.activities.length)*100)))}%</small></section>`:''}")

# Replace reward block with restrained, idempotent rewards and test isolation.
old="const xp=correct?(guess?6:12):4,coins=correct?(guess?2:5):1;state.xp+=xp;state.coins+=coins;"
new="""const previousStage=p.stage,newStage=np.stage,stageCoins:Record<Stage,number>={unseen:0,introduced:0,recognised:0,understood:2,applied:3,retained:5,'exam-ready':10};
const xp=correct&&rating==='I knew it'&&feedback.attempts===1?2:correct?1:0;let coins=0;
const session=state.activeSession,testOnly=Boolean(session?.testOnly);
if(!testOnly){state.xp+=xp;if(previousStage!==newStage&&stageCoins[newStage]>0){const key=`stage:${a.conceptId}:${newStage}`;if(awardOnce(key,stageCoins[newStage],'stage_rewarded',{conceptId:a.conceptId,stage:newStage}))coins=stageCoins[newStage]}if(session?.bossId&&correct)session.bossCorrect=(session.bossCorrect||0)+1}else{state.testMode.coins+=correct?1:0}
"""
text=text.replace(old,new)
text=text.replace("state.progress[a.conceptId]=np;state.events.push(emit('activity_answered'", "if(!state.activeSession?.testOnly)state.progress[a.conceptId]=np;if(!state.activeSession?.testOnly)state.events.push(emit('activity_answered'")
# Close conditional event push by replacing known ending.
text=text.replace("nextReview:np.nextReview},a.unitId));const previousStage", "nextReview:np.nextReview,testOnly:false},a.unitId));const previousStage")
text=text.replace("if((!correct||guess)&&state.activeSession&&state.activeSession.mode!=='exam')", "if((!correct||guess)&&state.activeSession&&!state.activeSession.testOnly&&state.activeSession.mode!=='exam')")

# Settings: developer code and test controls, shields.
needle="<section class=\"card danger\"><h2>Reset</h2>"
insert="""<section class=\"card\"><h2>Shield progression</h2>${shieldTiers.map(t=>`<p><b>${t.name}</b> · ${t.test()?'Unlocked':`Locked — ${t.requires}`}</p>`).join('')}</section><section class=\"card\"><h2>Developer test mode</h2>${state.testMode.enabled?`<p class=\"testWarning\"><b>TEST MODE</b> Test coins and unlocks are isolated from real progress.</p><p>${state.testMode.coins} test coins · ${state.testMode.unlockedCosmetics.length} test cosmetics</p><div class=\"branchButtons\"><button data-action=\"test-coins\">Grant 1,000 test coins</button><button data-action=\"test-unlock\">Unlock all cosmetics</button><button data-action=\"test-boss\">Preview unit boss</button><button data-action=\"test-achievement\">Preview achievement</button><button data-action=\"test-reset\">Reset test data</button><button data-action=\"test-exit\">Exit test mode</button></div>`:`<label>Developer code <input id=\"test-code\" autocomplete=\"off\"></label><button data-action=\"test-enable\">Enable test mode</button>`}</section>"""
text=text.replace(needle,insert+needle)

# Persistent badge in shell.
text=text.replace("${navigator.onLine?'':'<span>Offline</span>'}</header>", "${navigator.onLine?'':'<span>Offline</span>'}${state?.testMode?.enabled?'<span class=\"testModeBadge\">TEST MODE</span>':''}</header>")

# Add click actions before update-now.
marker="if(a==='update-now'){location.reload();return}"
actions="""if(a==='test-enable'){const code=(document.querySelector('#test-code') as HTMLInputElement)?.value;if(code==='JAKE-SECPLUS-TEST'){state.testMode.enabled=true;save();toast('TEST MODE enabled')}else toast('Incorrect test code','error');return}if(a==='test-exit'){state.testMode.enabled=false;save();toast('TEST MODE disabled');return}if(a==='test-coins'&&state.testMode.enabled){state.testMode.coins+=1000;save();toast('1,000 test coins granted');return}if(a==='test-unlock'&&state.testMode.enabled){state.testMode.unlockedCosmetics=['theme-blue','theme-green','theme-purple','theme-oled','shield-bronze','shield-silver','shield-gold','shield-platinum','shield-diamond','shield-master'];save();toast('Test cosmetics unlocked');return}if(a==='test-boss'&&state.testMode.enabled){start(5,'boss',true);return}if(a==='test-achievement'&&state.testMode.enabled){toast('Achievement unlocked: Test Preview','achievement');return}if(a==='test-reset'&&state.testMode.enabled){state.testMode={enabled:true,coins:0,unlockedCosmetics:[],previewShield:null};save();toast('Test-only data reset');return}"""+marker
text=text.replace(marker,actions)

# Exclude test data from export.
text=text.replace("const payload={profile,state,exportedAt:iso(),schemaVersion:'3.0.0'};", "const exportState={...state,testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null}};const payload={profile,state:exportState,exportedAt:iso(),schemaVersion:'3.0.0'};")

# Version bump.
text=text.replace("const APP_VERSION='3.0.0'", "const APP_VERSION='3.0.1'")
text=text.replace("schemaVersion:'3.0.0'", "schemaVersion:'3.0.1'")
text=text.replace("merged.schemaVersion='3.0.0'", "merged.schemaVersion='3.0.1'")
text=text.replace("state.schemaVersion='3.0.0'", "state.schemaVersion='3.0.1'")
text=text.replace("schemaVersion:'3.0.0'}", "schemaVersion:'3.0.1'}")

# CSS for boss health and reduced motion.
css += """

.bossHud{padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--panel);margin:12px 0}.bossTitle{display:flex;justify-content:space-between;gap:12px}.bossHealth{height:14px;border-radius:999px;background:var(--line);overflow:hidden;margin:10px 0}.bossHealth i{display:block;height:100%;background:linear-gradient(90deg,#f59e0b,#ef4444);transition:width .28s ease}.testModeBadge{position:fixed;top:8px;right:8px;z-index:1000;padding:5px 8px;border-radius:999px;background:#f59e0b;color:#111;font-weight:800;font-size:12px}.testWarning{border-left:4px solid #f59e0b;padding:10px}.bossHud{animation:bossEntrance .22s ease-out}.feedback.correct .reward{animation:rewardPulse .25s ease-out}@keyframes bossEntrance{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}@keyframes rewardPulse{50%{transform:scale(1.03)}}@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

app_path.write_text(text,encoding='utf-8');css_path.write_text(css,encoding='utf-8')
print('Applied v3.0.1 progression, boss, reward and test-mode balance')