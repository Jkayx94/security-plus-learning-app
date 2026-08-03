from pathlib import Path

path = Path('src/app.ts')
text = path.read_text(encoding='utf-8')

if 'function awardOnce(' in text:
    print('awardOnce helper already present')
    raise SystemExit(0)

anchor = "function level(){return Math.max(1,Math.floor(state.xp/250)+1)}\n"
helper = """function awardOnce(key:string,coins:number,eventType:string,payload:Record<string,unknown>):boolean{\n  if(state.rewardedEventIds.includes(key))return false;\n  state.rewardedEventIds.push(key);\n  state.coins+=coins;\n  state.events.push(emit(eventType,[],{...payload,rewardKey:key,coins}));\n  return true;\n}\n"""

if anchor not in text:
    raise SystemExit('Could not find insertion anchor for awardOnce helper')

text = text.replace(anchor, anchor + helper, 1)
path.write_text(text, encoding='utf-8')
print('Inserted awardOnce helper into src/app.ts')
