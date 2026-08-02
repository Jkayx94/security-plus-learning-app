from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: patch-mobile-ui.py <app.ts> <styles.css>")

app_path = Path(sys.argv[1])
css_path = Path(sys.argv[2])
app = app_path.read_text(encoding="utf-8")

old_question = """${exam?'':`<div class=\"branchButtons\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"teach\">Teach me</button><button data-special=\"forgot\">I forgot</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"guessed\">I guessed</button><button data-special=\"different\">Explain differently</button><button data-special=\"ms\">Microsoft example</button><button data-special=\"msp\">MSP example</button><button data-special=\"compare\">Compare concepts</button><button data-special=\"ai\">Ask AI</button></div><div class=\"confidence\"><b>Confidence</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>"""
new_question = """${exam?'':`<div class=\"confidence\"><b>How confident are you?</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide submitAnswer\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>${exam?'':`<details class=\"flagPanel\"><summary>⚑ Flag how this felt</summary><div class=\"branchButtons flagActions\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"guessed\">I guessed</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"teach\">Teach me</button></div></details>`}"""
if old_question not in app:
    raise SystemExit("Expected question layout fragment was not found; refusing an unsafe patch")
app = app.replace(old_question, new_question)

app = app.replace("const APP_VERSION='2.0.0', KEY='security-plus-mastery-state';", "const APP_VERSION='2.1.0', KEY='security-plus-mastery-state', PROFILE_KEY='security-plus-learner-profile';")
app = app.replace("type Confidence='I knew it'|'Fairly sure'|'Guessed'|'No idea';", "type Confidence='I knew it'|'Fairly sure'|'Guessed'|'No idea';\ntype Profile={id:string,name:string,examDate:string|null,createdAt:string};")
app = app.replace("let curriculum:any, units:any, records:any[]=[], concepts:any[]=[], acronyms:any[]=[], assessable:any[]=[], state:State, view='home'", "let curriculum:any, units:any, records:any[]=[], concepts:any[]=[], acronyms:any[]=[], assessable:any[]=[], state:State, profile:Profile|null=null, view='home'")
app = app.replace("const emit=(type:string,conceptIds:string[]=[],payload:Record<string,unknown>={},unitId?:string):StudyEvent=>({eventId:id(),schemaVersion:'2.0.0',timestamp:iso(),learnerId:'JAKE-001',type,conceptIds,unitId,payload});", "const emit=(type:string,conceptIds:string[]=[],payload:Record<string,unknown>={},unitId?:string):StudyEvent=>({eventId:id(),schemaVersion:'2.1.0',timestamp:iso(),learnerId:profile?.id||state?.learnerId||'LOCAL-LEARNER',type,conceptIds,unitId,payload});")
app = app.replace("function fresh():State{return {schemaVersion:'2.0.0',appVersion:APP_VERSION,learnerId:'JAKE-001'", "function fresh():State{return {schemaVersion:'2.1.0',appVersion:APP_VERSION,learnerId:profile?.id||id()")
app = app.replace("if(raw.schemaVersion==='2.0.0')", "if(raw.schemaVersion==='2.0.0'||raw.schemaVersion==='2.1.0')")
app = app.replace("function save(){localStorage.setItem(KEY,JSON.stringify(state))}", "function save(){state.appVersion=APP_VERSION;state.schemaVersion='2.1.0';localStorage.setItem(KEY,JSON.stringify(state))}\nfunction saveProfile(){if(profile)localStorage.setItem(PROFILE_KEY,JSON.stringify(profile))}\nfunction learnerName(){return profile?.name?.trim()||'Learner'}")

old_shell = "function shell(body:string){return `<header><button data-nav=\"home\" aria-label=\"Home\">⌂</button><div><strong>Security+ Mastery</strong><span>SY0-701 · Jake · v${APP_VERSION}</span></div>${navigator.onLine?'':'<span>Offline</span>'}</header>${body}<nav><button data-nav=\"home\">⌂<small>Home</small></button><button data-nav=\"learn\">▤<small>Learn</small></button><button data-action=\"review\">◉<small>Review</small></button><button data-nav=\"dashboard\">▥<small>Dashboard</small></button></nav>`}"
new_shell = "function shell(body:string){return `<header><button data-nav=\"home\" aria-label=\"Home\">⌂</button><div><strong>Security+ Adaptive Learning</strong><span>SY0-701 · ${esc(learnerName())} · v${APP_VERSION}</span></div>${navigator.onLine?'':'<span>Offline</span>'}</header>${body}<nav><button data-nav=\"home\">⌂<small>Home</small></button><button data-nav=\"learn\">▤<small>Learn</small></button><button data-action=\"review\">◉<small>Review</small></button><button data-nav=\"dashboard\">▥<small>Dashboard</small></button></nav>`}"
if old_shell not in app:
    raise SystemExit("Expected application shell was not found")
app = app.replace(old_shell, new_shell)

app = app.replace("<h1>Study what will improve your exam readiness most.</h1>", "<h1>Welcome back, ${esc(learnerName())}.</h1><p>Study what will improve your exam readiness most.</p>")
app = app.replace("'This concept is being explained using its approved curriculum branch and Jake’s Microsoft/MSP context.'", "'This concept is being explained using its approved curriculum branch and Microsoft/MSP context.'")
app = app.replace("link.download=`security-plus-jake-${new Date().toISOString().slice(0,10)}.json`", "link.download=`security-plus-${learnerName().toLowerCase().replace(/[^a-z0-9]+/g,'-')||'learner'}-${new Date().toISOString().slice(0,10)}.json`")

settings_old = "function settingsView(){return shell(`<main class=\"shell\"><h1>Data, backup and migration</h1>"
settings_new = "function settingsView(){return shell(`<main class=\"shell\"><h1>Profile, data and backups</h1><section class=\"card\"><h2>Learner profile</h2><label>Display name <input id=\"profile-name\" maxlength=\"40\" value=\"${esc(learnerName())}\"></label><label>Exam date (optional) <input id=\"profile-exam\" type=\"date\" value=\"${esc(profile?.examDate||'')}\"></label><button data-action=\"save-profile-settings\">Save profile</button><p class=\"muted\">Stored locally on this device and included in exported backups.</p></section>"
if settings_old not in app:
    raise SystemExit("Expected settings view was not found")
app = app.replace(settings_old, settings_new)

insert_before_render = """function onboarding(){return `<main class=\"onboarding shell\"><section class=\"onboardingCard\"><p class=\"eyebrow\">SECURITY+ SY0-701</p><h1>Welcome to Security+ Adaptive Learning</h1><p>Short sessions adapt to your confidence, weak areas, overdue reviews and exam priorities.</p><label for=\"onboard-name\">What should we call you?</label><input id=\"onboard-name\" maxlength=\"40\" autocomplete=\"name\" placeholder=\"Your name\"><label for=\"onboard-exam\">Exam date <span class=\"muted\">(optional)</span></label><input id=\"onboard-exam\" type=\"date\"><button class=\"primary wide\" data-action=\"complete-onboarding\">Start learning</button><p class=\"privacyNote\">Your name and progress stay in this browser unless you export a backup.</p></section></main>`}\n"""
app = app.replace("function render(){app.innerHTML=", insert_before_render + "function render(){app.innerHTML=view==='onboarding'?onboarding():")

click_anchor = "const a=t.dataset.action;"
click_add = "const a=t.dataset.action;if(a==='complete-onboarding'){const name=(document.querySelector('#onboard-name') as HTMLInputElement)?.value.trim();if(!name){alert('Please enter the name you want the app to use.');return}profile={id:state?.learnerId||id(),name,examDate:(document.querySelector('#onboard-exam') as HTMLInputElement)?.value||null,createdAt:iso()};if(state)state.learnerId=profile.id;saveProfile();if(state){state.events.push(emit('profile_created',[],{hasExamDate:Boolean(profile.examDate)}));save()}view='home';render();return}if(a==='save-profile-settings'){const name=(document.querySelector('#profile-name') as HTMLInputElement)?.value.trim();if(!name){alert('Display name cannot be blank.');return}profile={...(profile||{id:state.learnerId,createdAt:iso()}),name,examDate:(document.querySelector('#profile-exam') as HTMLInputElement)?.value||null};state.learnerId=profile.id;saveProfile();state.events.push(emit('profile_updated',[],{hasExamDate:Boolean(profile.examDate)}));save();render();return}"
if click_anchor not in app:
    raise SystemExit("Expected click action anchor was not found")
app = app.replace(click_anchor, click_add, 1)

boot_old = "async function boot(){try{[curriculum,units]=await Promise.all("
boot_new = "async function boot(){try{try{profile=JSON.parse(localStorage.getItem(PROFILE_KEY)||'null')}catch{profile=null}[curriculum,units]=await Promise.all("
if boot_old not in app:
    raise SystemExit("Expected boot function was not found")
app = app.replace(boot_old, boot_new)
app = app.replace("state=migrate(JSON.parse(stored||'null'));if(stored&&!localStorage.getItem(KEY))", "state=migrate(JSON.parse(stored||'null'));if(!profile){view='onboarding'}else{state.learnerId=profile.id}if(stored&&!localStorage.getItem(KEY))")
app = app.replace("{from:'prototype-v1',to:'2.0.0'}", "{from:'prototype-v1',to:'2.1.0'}")
app = app.replace("app = app.replace(\"2.0.0\", \"2.0.1\")" if False else "", "")
app_path.write_text(app, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
base_shell = ".shell{width:min(760px,100%);margin:auto;padding:18px 14px}"
if base_shell not in css:
    raise SystemExit("Expected shell CSS was not found; refusing an unsafe patch")
css = css.replace(base_shell, ".shell{width:min(760px,100%);margin:auto;padding:18px 14px calc(112px + env(safe-area-inset-bottom))}")
css += """
.submitAnswer{position:static;margin:14px 0 10px;box-shadow:none}
.flagPanel{margin:8px 0 24px;border:1px solid #2a3950;border-radius:12px;background:#0d1522;padding:2px 10px}
.flagPanel summary{cursor:pointer;min-height:46px;display:flex;align-items:center;justify-content:center;font-weight:700;color:#aebdd0;font-size:.92rem}
.flagPanel summary::marker{content:""}
.flagActions{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:4px 0 10px}
.flagActions button{background:#111c2c;border:1px solid #34445a;color:#d4dce8;font-weight:600;min-height:44px;font-size:.9rem}
.feedback .wide{position:static;margin:16px 0 20px}
body:has(.question) nav,body:has(.feedback) nav,body:has(.onboarding) nav{display:none!important}
body:has(.question) .shell,body:has(.feedback) .shell{padding-bottom:calc(36px + env(safe-area-inset-bottom))!important}
.question,.feedback{min-height:auto;overflow:visible}
.onboarding{min-height:100dvh;display:grid;place-items:center;padding:24px 16px!important}
.onboardingCard{width:min(100%,520px);background:linear-gradient(180deg,#121d2d,#0c1421);border:1px solid #2b3b52;border-radius:24px;padding:26px 20px;box-shadow:0 24px 60px #0008}
.onboardingCard h1{font-size:clamp(1.8rem,8vw,2.7rem);line-height:1.05;margin:.4rem 0 1rem}
.onboardingCard label{display:block;margin:18px 0 7px;font-weight:750}
.onboardingCard input{width:100%;min-height:52px;font-size:1rem}
.onboardingCard .primary{margin-top:22px}
.privacyNote{font-size:.86rem;color:#aebbd0;text-align:center;margin:14px 0 0}
@media(max-width:420px){.flagActions{grid-template-columns:1fr}.confidence button{min-height:42px;font-size:.88rem}}
"""
css_path.write_text(css, encoding="utf-8")

sw_path = app_path.parent.parent / "public" / "sw.js"
if sw_path.exists():
    sw = sw_path.read_text(encoding="utf-8")
    sw = sw.replace("2.0.0", "2.1.0").replace("2.0.1", "2.1.0")
    sw = re.sub(r"(CACHE(?:_NAME)?\s*=\s*['\"]).*?(['\"])", r"\1security-plus-v2.1.0\2", sw, count=1)
    if "skipWaiting" not in sw:
        sw += "\nself.addEventListener('install',()=>self.skipWaiting());\nself.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));\n"
    sw_path.write_text(sw, encoding="utf-8")

manifest_path = app_path.parent.parent / "public" / "manifest.webmanifest"
if manifest_path.exists():
    manifest = manifest_path.read_text(encoding="utf-8").replace("Security+ Mastery", "Security+ Adaptive Learning").replace("2.0.0", "2.1.0").replace("2.0.1", "2.1.0")
    manifest_path.write_text(manifest, encoding="utf-8")

print("Public learner onboarding, profile support, simplified question UI and v2.1.0 cache update applied")
