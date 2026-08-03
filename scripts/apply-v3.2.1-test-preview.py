from pathlib import Path
import re,sys
p=Path(sys.argv[1]);s=p.read_text(encoding='utf-8')
# Add TEST PREVIEW to achievements and cosmetics without altering real state.
s=s.replace("function achievementsView(){return shell(`<main class=\"shell\"><h1>Achievements</h1>","function achievementsView(){return shell(`<main class=\"shell\">${state.testMode.enabled?'<p class=\"eyebrow\">TEST PREVIEW</p>':''}<h1>Achievements</h1>")
s=s.replace("function cosmeticsView(){return shell(`<main class=\"shell\"><h1>Cosmetics</h1>","function cosmeticsView(){return shell(`<main class=\"shell\">${state.testMode.enabled?'<p class=\"eyebrow\">TEST PREVIEW</p>':''}<h1>Cosmetics</h1>")
# Show real and test balances separately in test mode.
s=s.replace("<p>${state.coins} coins available</p>","<p>${state.testMode.enabled?`Real coins: ${state.coins} · Test coins: ${state.testMode.unlimitedCoins?'Unlimited':state.testMode.coins}`:`${state.coins} coins available`}</p>")
# Waiting worker update action.
s=s.replace("if(a==='update-now'){location.reload();return}","if(a==='update-now'){navigator.serviceWorker?.getRegistration().then(r=>r?.waiting?.postMessage({type:'SKIP_WAITING'}));return}")
p.write_text(s,encoding='utf-8')
