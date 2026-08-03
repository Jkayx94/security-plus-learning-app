from pathlib import Path
import re, sys

app_path = Path(sys.argv[1])
source = app_path.read_text(encoding='utf-8')

# Preserve the already validated deterministic boot function. Repair only legacy malformed variants.
source = source.replace("catch{profile=null}[curriculum,units]=await Promise.all(", "catch{profile=null;}\n;[curriculum,units]=await Promise.all(")
source = source.replace("catch{profile=null;}[curriculum,units]=await Promise.all(", "catch{profile=null;}\n;[curriculum,units]=await Promise.all(")
source = source.replace("if(!profile){view='onboarding'}else{state.learnerId=profile.id}", "view=profile?'home':'onboarding';if(profile)state.learnerId=profile.id")
source = source.replace("if(t.dataset.testScreen==='session'){try{start(2,'adaptive',true)}", "if(t.dataset.testScreen==='session'){try{start(.5,'adaptive',true)}")

# Apply test cosmetics directly to the rendered document instead of showing a generic overlay.
old_render_tail = "document.documentElement.dataset.font=state?.testMode?.enabled?state.testMode.font:'system';if(view==='session'||view==='feedback')document.querySelector('nav')?.remove()"
new_render_tail = "document.documentElement.dataset.font=state?.testMode?.enabled?state.testMode.font:'system';document.documentElement.dataset.cosmetic=state?.testMode?.enabled?(state.testMode.previewCosmetic||''):'';if(view==='session'||view==='feedback')document.querySelector('nav')?.remove()"
if old_render_tail in source:
    source = source.replace(old_render_tail, new_render_tail, 1)

cosmetics_fn = r'''function cosmeticsView(){
 const test=state.testMode.enabled;
 return shell(`<main class="shell cosmeticsScreen">${test?'<p class="eyebrow">TEST PREVIEW</p><p class="testWarning">Test cosmetics affect only the local QA sandbox. Genuine ownership and coins are unchanged.</p>':''}<h1>Cosmetics</h1><p>Cosmetics never alter learning content, mastery or readiness.</p><section class="card cosmeticPreview">${shieldMarkup('large')}<p>${test?`Real coins: ${state.coins} · Test coins: ${state.testMode.unlimitedCoins?'Unlimited':state.testMode.coins}`:`${state.coins} coins available`}</p>${test?'<button data-action="test-restore-appearance">Restore genuine appearance</button>':''}</section>${cosmeticCatalogue.map(([idn,name,cost])=>{const item=String(idn),owned=test?(state.testMode.unlockEverything||state.testMode.unlockedCosmetics.includes(item)):state.cosmetics.owned.includes(item),equipped=test?(state.testMode.equippedTheme===item||state.testMode.equippedShield===item||state.testMode.previewCosmetic===item):(state.cosmetics.equippedTheme===item||state.cosmetics.equippedShield===item);return `<section class="card cosmetic ${equipped?'testEquipped':''}"><div><h2>${esc(name)}</h2><p>${equipped?(test?'Active test preview':'Equipped'):owned?(test?'Available in Test Mode':'Owned'):`${cost} coins`}</p></div><button data-cosmetic="${item}" data-cost="${cost}">${test?(equipped?'Preview active':'Preview / equip'):(equipped?'Equipped':owned?'Equip':'Unlock')}</button></section>`}).join('')}</main>`)
}'''
source, count = re.subn(r"function cosmeticsView\(\)\{.*?\nfunction reportsView", cosmetics_fn + "\nfunction reportsView", source, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace cosmeticsView exactly once')

old_test_cosmetic = "if(state.testMode.enabled){if(!state.testMode.unlockEverything&&!state.testMode.unlockedCosmetics.includes(item)){if(!state.testMode.unlimitedCoins&&state.testMode.coins<cost){toast('Not enough test coins','error');return}if(!state.testMode.unlimitedCoins)state.testMode.coins-=cost;state.testMode.unlockedCosmetics.push(item)}if(item.startsWith('theme-'))state.testMode.equippedTheme=item;else state.testMode.equippedShield=item;save();toast('Test cosmetic equipped');return}"
new_test_cosmetic = "if(state.testMode.enabled){if(!state.testMode.unlockEverything&&!state.testMode.unlockedCosmetics.includes(item)){if(!state.testMode.unlimitedCoins&&state.testMode.coins<cost){toast('Not enough test coins','error');return}if(!state.testMode.unlimitedCoins)state.testMode.coins-=cost;state.testMode.unlockedCosmetics.push(item)}state.testMode.previewCosmetic=item;if(item.startsWith('theme-'))state.testMode.equippedTheme=item;else if(item.startsWith('shield-'))state.testMode.equippedShield=item;save();toast('Test cosmetic preview applied');return}"
if old_test_cosmetic not in source:
    raise SystemExit('Could not find Test Mode cosmetic handler')
source = source.replace(old_test_cosmetic, new_test_cosmetic, 1)

restore_anchor = "if(a==='complete-onboarding')"
restore_handler = "if(a==='test-restore-appearance'&&state.testMode.enabled){state.testMode.previewCosmetic='';state.testMode.equippedTheme=state.cosmetics.equippedTheme;state.testMode.equippedShield=state.cosmetics.equippedShield;save();toast('Genuine appearance restored');return}"
if restore_handler not in source:
    source = source.replace(restore_anchor, restore_handler + restore_anchor, 1)

# Boss arena is a shared component used on questions, feedback and results.
boss_helpers = r'''function bossArenaMarkup(s:Session,phase:'question'|'hit'|'critical'|'miss'|'result'='question'){
 if(!s.bossId)return '';
 const total=Math.max(1,s.activities.length),done=Math.min(s.index,total),correct=s.bossCorrect||0,damage=Math.min(100,Math.round(correct/total*100)),hp=Math.max(0,100-damage),finishReady=damage>=70&&done<total,completed=done>=total;
 const bossName=s.bossType==='final'?'RISK TITAN':s.bossType==='domain'?'IDENTITY GATEKEEPER':s.bossType==='objective'?'CERTIFICATE GUARDIAN':'ROGUE PROCESS';
 const stateClass=completed?'battleComplete':finishReady?'finishReady':phase;
 const status=completed?(damage>=(s.bossThreshold||70)?'FINAL STRIKE LANDED':'BOSS SURVIVED'):finishReady?'FINAL STRIKE READY — COMPLETE EVERY QUESTION':phase==='critical'?'CRITICAL HIT':phase==='hit'?'DIRECT HIT':phase==='miss'?'ATTACK BLOCKED':'THREAT ENGAGED';
 return `<section class="bossArena ${stateClass}" aria-label="Boss battle status"><div class="bossVisual ${s.bossType} ${stateClass}" aria-hidden="true"><span class="bossCore">◆</span><b>${bossName}</b></div>${bossConsole(s,status)}<section class="bossHud" aria-label="Boss health"><div class="bossTitle"><b>${esc(s.bossType)} boss</b><span>${s.bossThreshold}% required</span></div><div class="bossHealth"><i style="width:${hp}%"></i></div><small>Boss HP ${hp}% · ${correct}/${total} successful hits</small>${finishReady?'<p class="finishPrompt">FINISH MODE ARMED — the final strike unlocks after the last question.</p>':''}</section></section>`;
}
function bossResultArena(b:any){
 const passed=Boolean(b.passed),score=Number(b.score||0),bossType=b.bossType||'unit',name=bossType==='final'?'RISK TITAN':bossType==='domain'?'IDENTITY GATEKEEPER':bossType==='objective'?'CERTIFICATE GUARDIAN':'ROGUE PROCESS';
 return `<section class="bossArena result ${passed?'defeated':'survived'}"><div class="bossVisual ${bossType} ${passed?'defeated':'survived'}" aria-hidden="true"><span class="bossCore">◆</span><b>${name}</b></div><section class="bossTerminal"><pre>[ ${passed?'THREAT NEUTRALISED':'THREAT STILL ACTIVE'} ]</pre><div class="terminalLine">&gt; ${passed?'FINAL STRIKE CONFIRMED. BOSS DEFEATED.':'BOSS SURVIVED. REVIEW AND RETURN.'}</div><div class="terminalStats"><span>SCORE ${score}%</span><span>${passed?'DEFEATED':'SURVIVED'}</span></div></section></section>`;
}'''
if 'function bossArenaMarkup(' not in source:
    source = source.replace('function bossConsole(s:Session){', boss_helpers + '\nfunction bossConsole(s:Session,statusOverride?:string){', 1)
else:
    source = source.replace('function bossConsole(s:Session){', 'function bossConsole(s:Session,statusOverride?:string){', 1)
source = source.replace("const log=done===0?'BOSS DETECTED. SELECT THE BEST RESPONSE.':correct===0?'ATTACK BLOCKED. ANALYSE THE NEXT SCENARIO.':hp===0?'FINAL STRIKE READY. COMPLETE THE BATTLE.':`SHIELD IMPACT. ${correct} HIT${correct===1?'':'S'} LANDED.`;", "const log=statusOverride|| (done===0?'BOSS DETECTED. SELECT THE BEST RESPONSE.':correct===0?'ATTACK BLOCKED. ANALYSE THE NEXT SCENARIO.':hp===0?'FINAL STRIKE READY. COMPLETE THE BATTLE.':`SHIELD IMPACT. ${correct} HIT${correct===1?'':'S'} LANDED.`);", 1)

# Replace the question-only inline boss markup with the shared arena.
source, count = re.subn(r"\$\{s\.bossId\?`<section class=\"bossArena\">.*?</section>`:''\}", "${bossArenaMarkup(s,'question')}", source, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace inline session boss arena exactly once')

# Keep the boss visible on confidence and feedback screens.
source = source.replace("const {a,correct,selected:sel,committed,exam}=feedback;", "const {a,correct,selected:sel,committed,exam}=feedback;\n const bossSession=state.activeSession?.bossId?state.activeSession:null,bossPhase=committed?(correct?(feedback.confidence==='I knew it'?'critical':'hit'):'miss'):'question',bossArena=bossSession?bossArenaMarkup(bossSession,bossPhase):'';", 1)
source = source.replace('<main class="shell feedbackScreen"><section class="card feedback', '<main class="shell feedbackScreen">${bossArena}<section class="card feedback', 3)

# Complete a boss from the final feedback Continue action instead of dropping to Dashboard.
old_continue = "if(a==='continue'){resetActivity();view=state.activeSession&&state.activeSession.index<state.activeSession.activities.length?'session':'dashboard';render();return}"
new_continue = "if(a==='continue'){const active=state.activeSession;if(active?.bossId&&active.index>=active.activities.length){completeBoss(active);delete state.activeSession;checkAchievements();save();view='boss-result';render();return}resetActivity();view=active&&active.index<active.activities.length?'session':'dashboard';render();return}"
if old_continue not in source:
    raise SystemExit('Could not find Continue handler')
source = source.replace(old_continue, new_continue, 1)

# Preserve test boss results in the isolated sandbox so the result screen remains visible.
old_test_complete = "if(s.testOnly){toast(`TEST MODE boss preview complete: ${score}%`);return}"
new_test_complete = "if(s.testOnly){state.testMode.lastBossResult={bossId:s.bossId,bossType:s.bossType,score,passed,completedAt:iso(),testOnly:true};toast(`TEST MODE boss preview complete: ${score}%`);return}"
if old_test_complete in source:
    source = source.replace(old_test_complete, new_test_complete, 1)

boss_result_fn = r'''function bossResultView(){const testResult=state.testMode.enabled?state.testMode.lastBossResult:null,b=testResult||state.bossHistory.at(-1);if(!b)return dashboard();const weak=Object.values(state.progress).filter(p=>p.misconceptions.length||p.mastery<50).slice(0,5);return shell(`<main class="shell">${testResult?'<p class="eyebrow">TEST PREVIEW</p>':''}${bossResultArena(b)}<section class="card bossResult ${b.passed?'defeated':'survived'}"><p class="eyebrow">${b.passed?'BOSS DEFEATED':'BOSS SURVIVED'}</p><h1>${b.score}%</h1><p>${testResult?'Test result only. Genuine boss history and rewards were not changed.':b.passed?'Pass threshold met. Reward issued once.':'No penalty. Review the weak concepts and retry when ready.'}</p><h2>Weak concepts</h2>${weak.map(p=>`<p>${esc(records.find(r=>r.conceptId===p.conceptId)?.name||p.conceptId)}</p>`).join('')||'<p>No specific weak concept detected.</p>'}${b.passed?'<button class="primary wide" data-nav="home">Continue</button>':'<div class="feedbackActions"><button data-mode="mistakes" data-minutes="5">Start targeted review</button><button data-nav="review">Retry later</button></div>'}</section></main>`)}'''
source, count = re.subn(r"function bossResultView\(\)\{.*?\nfunction dashboard", boss_result_fn + "\nfunction dashboard", source, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace bossResultView exactly once')

app_path.write_text(source, encoding='utf-8')

styles_path = app_path.with_name('styles.css')
styles = styles_path.read_text(encoding='utf-8')
marker = '/* v3.2.1 cosmetic and persistent boss UX */'
if marker not in styles:
    styles += r'''

/* v3.2.1 cosmetic and persistent boss UX */
html[data-cosmetic="card-glass"] .card{background:linear-gradient(145deg,#17243add,#0b1422cc);backdrop-filter:blur(14px);box-shadow:0 16px 42px #0007}
html[data-cosmetic="card-flat"] .card{box-shadow:none;border-radius:8px}
html[data-cosmetic="border-bronze"] .card,html[data-cosmetic="border-bronze"] .profileSummary{border-color:#b97a48}
html[data-cosmetic="border-neon"] .card,html[data-cosmetic="border-neon"] .profileSummary{border-color:#58e7ff;box-shadow:0 0 16px #28cbea44}
html[data-cosmetic="background-grid"] body{background-color:#08111b;background-image:linear-gradient(#1b385733 1px,transparent 1px),linear-gradient(90deg,#1b385733 1px,transparent 1px);background-size:24px 24px}
html[data-cosmetic="motion-subtle"] .card{animation:cosmeticRise .22s ease-out}
.cosmeticPreview{position:relative;overflow:hidden}.cosmetic.testEquipped{border-color:#62dfb6}.cosmetic.testEquipped::after{content:"TEST PREVIEW";font-size:.68rem;letter-spacing:.08em;color:#62dfb6}
.bossArena{margin:12px 0}.feedbackScreen .bossArena{position:sticky;top:76px;z-index:5;background:#090d14;padding:4px 0}.bossVisual{display:grid;place-items:center;gap:6px;min-height:92px;border:1px solid #34445d;border-radius:16px;background:radial-gradient(circle,#243b5f,#0b1320 70%);transition:transform .22s ease,filter .22s ease}.bossVisual .bossCore{font-size:2rem}.bossArena.hit .bossVisual{animation:bossHit .34s ease}.bossArena.critical .bossVisual{animation:bossCritical .48s ease}.bossArena.miss .bossVisual{animation:bossBlock .3s ease}.bossArena.finishReady .bossVisual{border-color:#ffb84d;box-shadow:0 0 24px #f59e0b66;animation:finishPulse 1.1s ease-in-out infinite}.finishPrompt{margin:8px 0 0;color:#ffd082;font-weight:800;letter-spacing:.03em}.bossArena.result .bossVisual{min-height:140px}.bossArena.defeated .bossVisual{animation:bossDefeat .65s ease forwards}.bossArena.survived .bossVisual{border-color:#ef6b73}.bossHealth i{transition:width .45s cubic-bezier(.2,.8,.2,1)}
@keyframes cosmeticRise{from{opacity:.75;transform:translateY(4px)}to{opacity:1;transform:none}}@keyframes bossHit{25%{transform:translateX(-7px);filter:brightness(1.7)}60%{transform:translateX(5px)}}@keyframes bossCritical{20%{transform:scale(1.06);filter:brightness(2)}45%{transform:translateX(-10px) rotate(-1deg)}70%{transform:translateX(7px) rotate(1deg)}}@keyframes bossBlock{50%{filter:grayscale(.8);transform:scale(.98)}}@keyframes finishPulse{50%{transform:scale(1.018);filter:brightness(1.25)}}@keyframes bossDefeat{to{opacity:.35;filter:grayscale(1);transform:translateY(10px) scale(.94)}}
@media(prefers-reduced-motion:reduce){.bossArena .bossVisual,.bossHealth i,html[data-cosmetic="motion-subtle"] .card{animation:none!important;transition:none!important}}
'''
    styles_path.write_text(styles, encoding='utf-8')
