from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("setIndex={i=>{setQIndex(i);", "setIndex={(i: number)=>{setQIndex(i);")
text = text.replace("setIndex={(i)=>{setQIndex(i);", "setIndex={(i: number)=>{setQIndex(i);")

replacement = r'''function Question({q,number,total,state,setState,next}:any){
 const [attempt,setAttempt]=useState(1);const [selected,setSelected]=useState('');const [feedback,setFeedback]=useState<any>(null);const [confidence,setConfidence]=useState<Confidence|''>('');const started=useRef(Date.now());const [locked,setLocked]=useState(false);
 const shuffledOptions=useMemo(()=>{const options=[...q.answerOptions];for(let i=options.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[options[i],options[j]]=[options[j],options[i]]}return options},[q.questionId]);
 const submit=()=>{if(!selected)return;const correct=selected===q.correctAnswer;if(correct){finish(true)}else if(attempt<3){setFeedback({kind:'hint',text:q.hints[`level${attempt}`]});setAttempt(attempt+1);setSelected('')}else if(attempt===3){setFeedback({kind:'guided',text:q.hints.level3});setAttempt(4);setSelected('')}else finish(false)};
 const finish=(correct:boolean)=>{const used=Math.max(0,attempt-1);const days=correct?(attempt===1?(confidence==='Educated guess'||confidence==='No idea'?1:7):attempt===2?5:attempt===3?2:1):1;const score=correct?(attempt===1?85:attempt===2?65:attempt===3?45:30):15;const record={questionId:q.questionId,selected,correct,attempt,hintsUsed:used,confidence,responseTimeSeconds:Math.round((Date.now()-started.current)/1000),misconceptionTags:correct?[]:q.misconceptionTags,nextReview:addDays(days),timestamp:new Date().toISOString()};setState((s:AppState)=>({...s,answers:[...s.answers,record],events:[...s.events,{eventId:crypto.randomUUID(),activityType:'question_completed',...record}],records:s.records.map(r=>q.conceptIds.includes(r.conceptId)?{...r,stage:correct?(r.stage==='unseen'?'introduced':'recognised'):r.stage,masteryScore:Math.max(r.masteryScore,score),intervalDays:days,nextReview:addDays(days),attempts:r.attempts+1,correct:r.correct+(correct?1:0),firstAttemptCorrect:r.firstAttemptCorrect+(correct&&attempt===1?1:0),hintsUsed:r.hintsUsed+used,misconceptions:correct?r.misconceptions:[...new Set([...r.misconceptions,...q.misconceptionTags])]}:r)}));setFeedback({kind:correct?'correct':'wrong',selected});setLocked(true)};
 const wrong=Object.entries(q.incorrectOptionRationales||{});
 return <main className="shell question"><div className="row"><span>Question {number} of {total}</span><span>{locked?'Feedback':`Attempt ${attempt} of 4`}</span></div><div className="progress"><i style={{width:`${(number/total)*100}%`}}/></div><section className="card"><span className="pill">{q.difficulty}</span><h1>{q.prompt}</h1>{!locked&&<><div className="answers">{shuffledOptions.map((o:string)=><button key={o} className={selected===o?'selected':''} onClick={()=>setSelected(o)}><span>{o}</span></button>)}</div><div className="confidence"><b>Confidence (optional)</b><div>{(['Knew it','Reasoned it out','Educated guess','No idea'] as Confidence[]).map(c=><button className={confidence===c?'selected':''} onClick={()=>setConfidence(c)} key={c}>{c}</button>)}</div></div></>}{feedback?.kind==='hint'&&<section className="feedback hint"><b>Not quite — try again</b><p>{feedback.text}</p></section>}{feedback?.kind==='guided'&&<section className="feedback guided"><b>One final guided attempt</b><p>{feedback.text}</p></section>}{locked&&<section className={`feedback ${feedback.kind}`}><h2>{feedback.kind==='correct'?'Correct':'Not correct this time'}</h2><p><b>Your answer:</b> {feedback.selected}</p><p><b>Correct answer:</b> {q.correctAnswer}</p><div className="cue"><b>Why</b><p>{q.fullRationale}</p></div>{wrong.length>0&&<details open><summary>Why the other answers do not fit</summary>{wrong.map(([k,v])=><p key={k}><b>{k}:</b> {String(v)}</p>)}</details>}{q.misconceptionTags?.length>0&&<p className="muted"><b>Watch for:</b> {q.misconceptionTags.map((x:string)=>x.replaceAll('_',' ')).join(', ')}</p>}</section>}</section><div className="actions">{locked?<button className="primary wide" onClick={next}>Continue<ChevronRight/></button>:<button className="primary wide" disabled={!selected} onClick={submit}>{attempt===4?'Submit final response':'Check answer'}</button>}</div></main>}
'''

pattern = r"function Question\(\{q,number,total,state,setState,next\}:any\)\{.*?\nfunction Dashboard\(\{state\}:any\)\{"
match = re.search(pattern, text, flags=re.S)
if not match:
    raise SystemExit("Question component was not found")
text = text[:match.start()] + replacement + "\nfunction Dashboard({state}:any){" + text[match.end():]
path.write_text(text, encoding="utf-8")
