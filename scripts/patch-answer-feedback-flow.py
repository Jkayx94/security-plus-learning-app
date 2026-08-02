from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: patch-answer-feedback-flow.py <app.ts> <styles.css>")

app_path = Path(sys.argv[1])
css_path = Path(sys.argv[2])
text = app_path.read_text(encoding="utf-8")

# Track a pre-answer uncertainty flag without asking for confidence before submission.
text = text.replace(
    "activityStarted=Date.now();",
    "activityStarted=Date.now(), preAnswerFlag='';"
)
text = text.replace(
    "function resetActivity(){selected=[];confidence='Fairly sure';attempt=1;guidance='';activityStarted=Date.now()}",
    "function resetActivity(){selected=[];confidence='Fairly sure';attempt=1;guidance='';preAnswerFlag='';activityStarted=Date.now()}"
)

session_re = re.compile(r"function session\(\)\{.*?\nfunction finishAnswer", re.S)
new_session = r'''function session(){const s=state.activeSession!,a=s.activities[s.index];if(!a){delete state.activeSession;save();view='dashboard';return dashboard()}const exam=s.mode==='exam';return shell(`<main class="shell questionScreen"><div class="row"><span>${exam?'Exam':'Adaptive session'} · ${s.index+1}/${s.activities.length}</span><span>${exam?'No hints':'Answer first'}</span></div><div class="progress"><i style="width:${(s.index+1)/s.activities.length*100}%"></i></div>${exam?'':`<section class="selectionReason"><b>Why selected:</b> ${esc(a.selectionReason)}</section>`}<section class="card question"><span class="pill">${esc(a.type)}</span><h1>${esc(a.prompt)}</h1><div class="answers">${a.options.map(o=>`<button data-option="${encodeURIComponent(o)}" class="${selected.includes(o)?'selected':''}">${esc(o)}</button>`).join('')}</div>${exam?'':`<details class="flagPanel"><summary>⚑ Flag this question</summary><p class="muted">Optional. This does not submit an answer.</p><div class="flagActions"><button data-special="dontknow" class="${preAnswerFlag==='dontknow'?'selected':''}">I don’t know</button><button data-special="forgot" class="${preAnswerFlag==='forgot'?'selected':''}">I forgot</button><button data-special="confusing" class="${preAnswerFlag==='confusing'?'selected':''}">I’m mixing this up</button></div></details>`}</section><button class="primary wide submitAnswer" data-action="submit" ${selected.length?'':'disabled'}>Submit answer</button></main>`)}
function finishAnswer'''
if not session_re.search(text):
    raise SystemExit("Session function was not found")
text = session_re.sub(new_session, text, count=1)

flow_re = re.compile(r"function finishAnswer\(correct:boolean\)\{.*?\nfunction dashboard", re.S)
new_flow = r'''function finishAnswer(correct:boolean){const s=state.activeSession!,a=s.activities[s.index];s.index++;feedback={a,correct,selected:[...selected],attempts:attempt,responseTimeSeconds:Math.round((Date.now()-activityStarted)/1000),preAnswerFlag,exam:s.mode==='exam',committed:false};save();view='feedback';render()}
function commitAnswer(rating:Confidence){if(!feedback||feedback.committed)return;confidence=rating;const {a,correct}=feedback,p=state.progress[a.conceptId],guess=rating==='Guessed'||rating==='No idea'||Boolean(feedback.preAnswerFlag),interval=!correct?1:guess?1:feedback.attempts>1?3:7;const mastery=Math.max(0,Math.min(100,p.mastery+(correct?(guess?3:12):-8))),order:Stage[]=['unseen','introduced','recognised','understood','applied','retained','exam-ready'];let si=order.indexOf(p.stage);if(correct&&!guess)si=Math.min(order.length-1,Math.max(1,si+1));else if(p.stage==='unseen')si=1;const misconception=!correct?(a.confusionWith||feedback.preAnswerFlag||'precision_vs_related_term'):feedback.preAnswerFlag||'';const np={...p,stage:order[si],mastery,attempts:p.attempts+1,correct:p.correct+(correct?1:0),guesses:p.guesses+(guess?1:0),hints:p.hints,misconceptions:misconception?[...new Set([...p.misconceptions,misconception])]:p.misconceptions,nextReview:addDays(interval),lastSeen:iso(),recognition:Math.max(p.recognition,correct?mastery:0),understanding:Math.max(p.understanding,correct&&!guess?mastery-8:0),application:Math.max(p.application,correct&&['scenario-classification','practical-workplace-recognition'].includes(a.type)?mastery-5:0),scenarioTransfer:Math.max(p.scenarioTransfer,correct&&a.type==='scenario-classification'?mastery:0),confidenceAccuracy:Math.round((p.confidenceAccuracy*p.attempts+(correct&&!guess?100:correct?35:rating==='I knew it'?0:50))/(p.attempts+1)),responseTimes:[...p.responseTimes.slice(-19),feedback.responseTimeSeconds]};state.progress[a.conceptId]=np;state.events.push(emit('activity_answered',[a.conceptId],{activityId:a.id,activityType:a.type,selected:feedback.selected,correct,correctAnswer:a.correct,attempts:feedback.attempts,confidence:rating,preAnswerFlag:feedback.preAnswerFlag||null,hintsUsed:0,responseTimeSeconds:feedback.responseTimeSeconds,nextReview:np.nextReview},a.unitId));state.xp+=correct?10:4;feedback={...feedback,confidence:rating,np,committed:true};save();render()}
function feedbackView(){const {a,correct,selected:sel,committed,exam}=feedback;if(!committed)return shell(`<main class="shell feedbackScreen"><section class="card feedback ${exam?'recorded':correct?'correct':'wrong'}"><p class="eyebrow">${exam?'ANSWER RECORDED':correct?'CORRECT':'NOT CORRECT'}</p><h1>${exam?'How did that answer feel?':correct?'Good answer.':'Review this one.'}</h1>${exam?'':`<p><b>Your answer:</b> ${esc(sel.join(', ')||'No response')}</p><p><b>Correct answer:</b> ${esc(a.correct.join(', '))}</p>`}<h2>Did you know it?</h2><div class="postAnswerConfidence">${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-rating="${c}">${c}</button>`).join('')}</div><p class="muted">This changes mastery and when the concept returns.</p></section></main>`);const np=feedback.np;return shell(`<main class="shell feedbackScreen"><section class="card feedback ${exam?'recorded':correct?'correct':'wrong'}"><p class="eyebrow">${exam?'EXAM RESPONSE SAVED':correct?'CORRECT':'NOT CORRECT'}</p><h1>${exam?'Response saved.':correct?'Good answer.':'Review this one.'}</h1><p><b>Confidence:</b> ${esc(feedback.confidence)}</p>${exam?'':`<p><b>Your answer:</b> ${esc(sel.join(', ')||'No response')}</p><p><b>Correct answer:</b> ${esc(a.correct.join(', '))}</p><details class="explanationPanel"><summary>Why this answer is correct</summary><p>${esc(a.reason)}</p></details><details class="explanationPanel"><summary>Why the alternatives do not fit</summary>${Object.entries(a.distractorReasons).map(([k,v])=>`<p><b>${esc(k)}:</b> ${esc(v)}</p>`).join('')}</details><details class="explanationPanel"><summary>Memory cue and exam trap</summary><p><b>Memory cue:</b> ${esc(a.memoryCue)}</p><p><b>Exam distinction:</b> ${esc(a.examTrap)}</p></details><details class="explanationPanel"><summary>Microsoft and MSP examples</summary><p>${esc(a.microsoftExample)}</p><p>${esc(a.mspExample)}</p></details><details class="explanationPanel"><summary>What happens next</summary><p>${correct&&feedback.confidence==='I knew it'?'Review at the scheduled interval.':'This concept will return sooner in a different form.'}</p>${np?.misconceptions?.length?`<p><b>Tracked confusion:</b> ${esc(np.misconceptions.at(-1)?.replaceAll('_',' '))}</p>`:''}</details><button data-action="save-cue">Save memory cue</button>`}<button class="primary wide" data-action="continue">Continue</button></section></main>`)}
function dashboard'''
if not flow_re.search(text):
    raise SystemExit("Answer/feedback functions were not found")
text = flow_re.sub(new_flow, text, count=1)

# Post-answer rating handler.
needle = "if(t.dataset.option){selected=[decodeURIComponent(t.dataset.option)];render();return}"
replacement = needle + "if(t.dataset.rating){commitAnswer(t.dataset.rating as Confidence);return}"
if needle not in text:
    raise SystemExit("Option handler was not found")
text = text.replace(needle, replacement, 1)

# Remove pre-answer confidence controls if any survived another patch.
text = re.sub(r"if\(t\.dataset\.confidence\)\{confidence=t\.dataset\.confidence as Confidence;render\(\);return\}", "", text, count=1)

# Special buttons now only set an uncertainty flag; they do not reveal teaching before submission.
special_re = re.compile(r"if\(t\.dataset\.special\)\{.*?save\(\);render\(\);return\}", re.S)
special_new = "if(t.dataset.special){preAnswerFlag=t.dataset.special===preAnswerFlag?'':t.dataset.special;const ac=state.activeSession!.activities[state.activeSession!.index];state.events.push(emit('question_flagged',[ac.conceptId],{flag:preAnswerFlag||null},ac.unitId));save();render();return}"
if not special_re.search(text):
    raise SystemExit("Special-action handler was not found")
text = special_re.sub(special_new, text, count=1)

# Submit once, then move to post-answer self-assessment. No answer-revealing hints before feedback.
submit_re = re.compile(r"if\(a==='submit'\)\{.*?finishAnswer\(correct\)\}", re.S)
submit_new = "if(a==='submit'){const s=state.activeSession!,ac=s.activities[s.index],correct=ac.correct.length===selected.length&&ac.correct.every(x=>selected.includes(x));finishAnswer(correct)}"
if not submit_re.search(text):
    raise SystemExit("Submit handler was not found")
text = submit_re.sub(submit_new, text, count=1)

# Version and cache bump.
text = text.replace("2.1.1", "2.2.0").replace("2.1.0", "2.2.0")
app_path.write_text(text, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
css += r'''
.questionScreen .confidence{display:none!important}
.questionScreen .flagPanel{margin:12px 0 0}
.questionScreen .flagActions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:4px 0 12px}
.questionScreen .flagActions button{min-height:44px;background:#111c2c;border:1px solid #34445a;color:#d4dce8}
.questionScreen .flagActions button.selected{border-color:#7fc5ff;background:#17395b}
.postAnswerConfidence{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.postAnswerConfidence button{min-height:52px;font-weight:750}
.explanationPanel{border:1px solid #2b3b52;border-radius:14px;background:#0e1725;margin:10px 0;padding:2px 14px}
.explanationPanel summary{min-height:50px;display:flex;align-items:center;font-weight:750;cursor:pointer}
.explanationPanel p{line-height:1.55}
.feedbackScreen .feedback{padding-bottom:20px}
body:has(.questionScreen) nav,body:has(.feedbackScreen) nav{display:none!important}
@media(max-width:520px){.questionScreen .flagActions{grid-template-columns:1fr}.postAnswerConfidence{grid-template-columns:1fr 1fr}}
'''
css_path.write_text(css, encoding="utf-8")

public_dir = app_path.parent.parent / "public"
sw_path = public_dir / "sw.js"
if sw_path.exists():
    sw = sw_path.read_text(encoding="utf-8").replace("2.1.1", "2.2.0").replace("2.1.0", "2.2.0")
    sw = re.sub(r"(CACHE(?:_NAME)?\s*=\s*['\"]).*?(['\"])", r"\1security-plus-v2.2.0\2", sw, count=1)
    sw_path.write_text(sw, encoding="utf-8")
manifest_path = public_dir / "manifest.webmanifest"
if manifest_path.exists():
    manifest_path.write_text(manifest_path.read_text(encoding="utf-8").replace("2.1.1", "2.2.0").replace("2.1.0", "2.2.0"), encoding="utf-8")

print("Post-answer confidence and progressive explanation flow applied; version 2.2.0")
