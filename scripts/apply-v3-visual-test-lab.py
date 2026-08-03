from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit('Usage: apply-v3-visual-test-lab.py <app.ts> <styles.css>')
app_path=Path(sys.argv[1]); css_path=Path(sys.argv[2])
text=app_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')

text=text.replace("const APP_VERSION='3.0.1'", "const APP_VERSION='3.0.2'")
text=text.replace("schemaVersion:'3.0.1'", "schemaVersion:'3.0.2'")
text=text.replace("schemaVersion='3.0.1'", "schemaVersion='3.0.2'")
text=text.replace("schemaVersion:'3.0.1'}", "schemaVersion:'3.0.2'}")
text=text.replace("merged.schemaVersion='3.0.1'", "merged.schemaVersion='3.0.2'")

text=text.replace("testMode:{enabled:boolean,coins:number,unlockedCosmetics:string[],previewShield:string|null}", "testMode:{enabled:boolean,coins:number,unlockedCosmetics:string[],previewShield:string|null,font:string,overlay:string|null,animation:string|null}")
text=text.replace("testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null}", "testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null,font:'system',overlay:null,animation:null}")
text=text.replace("merged.testMode={enabled:false,coins:0,unlockedCosmetics:[],previewShield:null,...(s?.testMode||{})}", "merged.testMode={enabled:false,coins:0,unlockedCosmetics:[],previewShield:null,font:'system',overlay:null,animation:null,...(s?.testMode||{})}")
text=text.replace("testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null}}", "testMode:{enabled:false,coins:0,unlockedCosmetics:[],previewShield:null,font:'system',overlay:null,animation:null}}")
text=text.replace("state.testMode={enabled:true,coins:0,unlockedCosmetics:[],previewShield:null}", "state.testMode={enabled:true,coins:0,unlockedCosmetics:[],previewShield:null,font:'system',overlay:null,animation:null}")

anchor="function toastView(){return toastMessage?"
if 'function shieldMarkup(' not in text:
    insertion=r'''function shieldMarkup(size='normal'){
  const id=state.testMode.enabled&&state.testMode.previewShield?state.testMode.previewShield:state.cosmetics.equippedShield;
  const name=id.replace('shield-','').replaceAll('-',' ');
  return `<div class="profileShield ${esc(id)} ${esc(size)}" aria-label="${esc(name)} shield"><span>◆</span><b>${esc(name)}</b></div>`;
}
function bossConsole(s:Session){
  if(!s.bossId)return '';
  const total=s.activities.length,done=s.index,correct=s.bossCorrect||0,hp=Math.max(0,100-Math.round(correct/Math.max(1,total)*100));
  const frames=['[=== SECURITY WRAITH ===]','[==  SECURITY WRAITH  ==]','[=   SECURITY WRAITH   =]'];
  const frame=frames[Math.min(frames.length-1,Math.floor(correct/Math.max(1,total)*frames.length))];
  const log=done===0?'BOSS DETECTED. SELECT THE BEST RESPONSE.':correct===0?'ATTACK BLOCKED. ANALYSE THE NEXT SCENARIO.':hp===0?'FINAL STRIKE READY. COMPLETE THE BATTLE.':`SHIELD IMPACT. ${correct} HIT${correct===1?'':'S'} LANDED.`;
  return `<section class="bossTerminal ${state.testMode.animation==='critical'?'criticalPreview':''}" aria-label="Text battle display"><pre>${esc(frame)}
      /\\_/
  ___( o.o )___
 /___  >^<  ___\\
     \\___/</pre><div class="terminalLine">&gt; ${esc(log)}</div><div class="terminalStats"><span>HP ${hp}%</span><span>HITS ${correct}/${total}</span><span>ROUND ${Math.min(done+1,total)}/${total}</span></div></section>`;
}
function visualTestLab(){
  if(!state.testMode.enabled)return settingsView();
  const shields=['shield-basic','shield-bronze','shield-silver','shield-gold','shield-platinum','shield-diamond','shield-master'];
  const fonts=[['system','System'],['compact','Compact'],['readable','Readable'],['mono','Terminal']];
  return shell(`<main class="shell testLab"><h1>Visual test laboratory</h1><p class="notice">TEST MODE previews are isolated from real progress and exports.</p><section class="card"><h2>Profile shield</h2>${shieldMarkup('large')}<div class="previewGrid">${shields.map(x=>`<button data-test-shield="${x}">${x.replace('shield-','')}</button>`).join('')}</div></section><section class="card"><h2>Typography</h2><p class="fontSample">Security controls reduce risk. Choose the BEST answer.</p><div class="previewGrid">${fonts.map(([id,label])=>`<button data-test-font="${id}">${label}</button>`).join('')}</div></section><section class="card"><h2>Overlay previews</h2><div class="previewGrid"><button data-test-overlay="achievement">Achievement</button><button data-test-overlay="coins">Coin reward</button><button data-test-overlay="update">Update available</button><button data-test-overlay="feedback-correct">Correct feedback</button><button data-test-overlay="feedback-wrong">Incorrect feedback</button><button data-test-overlay="tutor">Tutor sheet</button><button data-test-overlay="report">Report sheet</button></div></section><section class="card"><h2>Animation previews</h2><div class="previewGrid"><button data-test-animation="impact">Shield impact</button><button data-test-animation="critical">Critical hit</button><button data-test-animation="defeated">Boss defeated</button></div></section><section class="card"><h2>Boss previews</h2><div class="previewGrid"><button data-test-boss="boss">Unit boss</button><button data-test-boss="boss-objective">Objective boss</button><button data-test-boss="boss-domain">Domain boss</button><button data-test-boss="boss-final">Final boss</button></div></section><section class="card"><h2>Test data</h2><p>${state.testMode.coins} test coins · ${state.testMode.unlockedCosmetics.length} test cosmetics</p><div class="previewGrid"><button data-action="test-coins">Grant test coins</button><button data-action="test-unlock">Unlock test cosmetics</button><button data-action="test-reset">Reset test data</button><button data-action="test-exit">Exit test mode</button></div></section></main>`);
}
function testOverlay(){
 const o=state.testMode.overlay;if(!state.testMode.enabled||!o)return '';
 const title=o==='achievement'?'Achievement unlocked':o==='coins'?'+25 test coins':o==='update'?'Update available':o==='feedback-correct'?'Correct':o==='feedback-wrong'?'Not correct':o==='tutor'?'Grounded tutor':'Report question';
 return `<div class="testOverlayBackdrop"><section class="testOverlay ${esc(o)}" role="dialog" aria-modal="true"><p class="eyebrow">TEST PREVIEW</p><h2>${esc(title)}</h2><p>This is a visual-only preview. It does not change study evidence.</p><button class="primary wide" data-action="test-close-overlay">Close preview</button></section></div>`;
}
'''
    text=text.replace(anchor,insertion+anchor)

text=text.replace("${state?.testMode?.enabled?'<span class=\"testModeBadge\">TEST MODE</span>':''}</header>", "${shieldMarkup('header')}${state?.testMode?.enabled?'<button class=\"testModeBadge\" data-nav=\"testlab\">TEST MODE</button>':''}</header>")
text=text.replace("</section>${exam?'':`<section class=\"selectionReason\">", "</section>${bossConsole(s)}${exam?'':`<section class=\"selectionReason\">")
text=text.replace("view==='reports'?reportsView():settingsView())+aiPanel()+reportPanel()+toastView()", "view==='reports'?reportsView():view==='testlab'?visualTestLab():settingsView())+aiPanel()+reportPanel()+testOverlay()+toastView()")
text=text.replace("document.documentElement.dataset.theme=state?.cosmetics?.equippedTheme||'theme-blue';", "document.documentElement.dataset.theme=state?.cosmetics?.equippedTheme||'theme-blue';document.documentElement.dataset.font=state?.testMode?.enabled?state.testMode.font:'system';")
text=text.replace("state.testMode.enabled=true;save();toast('TEST MODE enabled')", "state.testMode.enabled=true;save();view='testlab';toast('TEST MODE enabled')")

handler_anchor="if(t.dataset.cosmetic){"
handler_insert="""if(t.dataset.testShield&&state.testMode.enabled){state.testMode.previewShield=t.dataset.testShield;save();toast('Shield preview changed');return}if(t.dataset.testFont&&state.testMode.enabled){state.testMode.font=t.dataset.testFont;save();toast('Font preview changed');return}if(t.dataset.testOverlay&&state.testMode.enabled){state.testMode.overlay=t.dataset.testOverlay;render();return}if(t.dataset.testAnimation&&state.testMode.enabled){state.testMode.animation=t.dataset.testAnimation;toast(`Animation preview: ${t.dataset.testAnimation}`,'achievement');return}if(t.dataset.testBoss&&state.testMode.enabled){start(5,t.dataset.testBoss,true);return}"""
if handler_insert not in text:
    text=text.replace(handler_anchor,handler_insert+handler_anchor)
text=text.replace("if(a==='test-exit'){state.testMode.enabled=false", "if(a==='test-close-overlay'){state.testMode.overlay=null;render();return}if(a==='test-exit'){state.testMode.enabled=false")

# Ensure displayed boss label handles all boss modes.
text=text.replace("s.mode==='boss'?'Boss battle'", "s.bossId?'Boss battle'")

css_add=r'''
.profileShield{display:inline-grid;place-items:center;min-width:54px;min-height:54px;padding:.35rem;border:2px solid currentColor;clip-path:polygon(50% 0,92% 18%,84% 72%,50% 100%,16% 72%,8% 18%);background:linear-gradient(145deg,#26364f,#101722);text-transform:capitalize;text-align:center;line-height:1}.profileShield span{font-size:1.15rem}.profileShield b{font-size:.55rem}.profileShield.header{min-width:42px;min-height:42px}.profileShield.large{width:130px;height:145px;margin:1rem auto;font-size:1.25rem}.shield-bronze{color:#d18a55}.shield-silver{color:#d8e0ea}.shield-gold{color:#ffd66b}.shield-platinum{color:#9ce8ff}.shield-diamond{color:#c6b7ff}.shield-master{color:#fff;background:linear-gradient(145deg,#5739a6,#116d82)}
.bossTerminal{background:#050a08;border:1px solid #36d27a;border-radius:12px;color:#7cffaa;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;padding:12px;margin:12px 0;box-shadow:inset 0 0 24px #001d0d;overflow:hidden}.bossTerminal pre{font-size:.72rem;line-height:1.05;text-align:center;margin:0;white-space:pre}.terminalLine{border-top:1px dashed #237d4a;margin-top:8px;padding-top:8px;min-height:2.5em}.terminalStats{display:flex;justify-content:space-between;font-size:.72rem;margin-top:8px}.criticalPreview{animation:criticalHit .45s ease-in-out 2}.previewGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.fontSample{font-size:1.15rem;padding:12px;border:1px solid var(--border);border-radius:10px}.testOverlayBackdrop{position:fixed;inset:0;background:#000b;display:grid;place-items:end center;z-index:1000}.testOverlay{width:min(100%,520px);background:var(--card);border-radius:20px 20px 0 0;padding:24px;box-shadow:0 -18px 60px #0008}.testLab .card{overflow:hidden}html[data-font='compact'] body{font-family:Arial Narrow,Roboto Condensed,sans-serif;font-size:14px}html[data-font='readable'] body{font-family:Verdana,Arial,sans-serif;font-size:17px;line-height:1.65}html[data-font='mono'] body{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}@keyframes criticalHit{0%,100%{transform:translateX(0);filter:none}25%{transform:translateX(-5px);filter:brightness(1.8)}75%{transform:translateX(5px)}}@media(prefers-reduced-motion:reduce){.bossTerminal,.criticalPreview,.profileShield,.testOverlay{animation:none!important;transition:none!important}}
'''
if '.bossTerminal{' not in css:
    css += '\n'+css_add

app_path.write_text(text,encoding='utf-8');css_path.write_text(css,encoding='utf-8')
print('Applied v3.0.2 visual test lab, shields, typography previews and ASCII boss console')
