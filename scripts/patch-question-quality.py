from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: patch-question-quality.py <app.ts>")

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

replacement = r'''function makeActivity(r:any,why:string):Activity{
  const u=unitFor(r.conceptId),isA=r.recordClass==='acronym',answer=isA?((r.officialTerms||[])[0]||r.name):r.name;
  const acronym=isA?r.name.split(' - ')[0]:'';
  const siblingPool=concepts.filter(x=>x.conceptId!==r.conceptId&&x.parentId===r.parentId);
  const relatedIds=new Set(r.relatedConcepts||[]);
  const relatedPool=concepts.filter(x=>x.conceptId!==r.conceptId&&relatedIds.has(x.conceptId));
  const fallbackPool=concepts.filter(x=>x.conceptId!==r.conceptId&&x.objective===r.objective&&x.conceptType===r.conceptType);
  const distractorRecords=[...siblingPool,...relatedPool,...fallbackPool].filter((x,i,a)=>a.findIndex(y=>y.conceptId===x.conceptId)===i).sort(()=>Math.random()-.5).slice(0,3);
  const acronymDistractors=acronyms.filter(x=>x.conceptId!==r.conceptId).sort(()=>Math.random()-.5).slice(0,3).map(x=>(x.officialTerms||[])[0]||x.name);
  const options=[answer,...(isA?acronymDistractors:distractorRecords.map(x=>x.name))].sort(()=>Math.random()-.5);
  const branchParts=String(r.objectiveBranch||'').split('>').map((x:string)=>x.trim()).filter(Boolean);
  const parentPath=branchParts.length>1?branchParts.slice(0,-1).join(' > '):`${r.domain} > Objective ${r.objective}`;
  const prompt=isA?`What is the approved Security+ expansion of ${acronym}?`:`Which approved Security+ term completes this objective path?\n${parentPath} > ____`;
  const type=isA?'acronym-expansion':'objective-path-recognition';
  return {id:id(),conceptId:r.conceptId,unitId:u.unitId,type,prompt,options,correct:[answer],reason:isA?`${acronym} expands to ${answer} in the approved acronym list.`:`${r.name} is the approved assessable concept at ${r.objectiveBranch} in objective ${r.objective}.`,distractorReasons:Object.fromEntries(options.filter(x=>x!==answer).map(x=>[x,`${x} is a different approved term and does not complete this exact objective path.`])),memoryCue:isA?`${acronym} → ${answer}`:`${parentPath} → ${r.name}`,examTrap:isA?'Read the full expansion; similar acronyms are not interchangeable.':'Match the exact objective path. Do not infer a scenario that was not supplied.',microsoftExample:`A Microsoft environment may use or encounter ${r.name} when working within ${parentPath.toLowerCase()}.`,mspExample:`An MSP technician may encounter ${r.name} while supporting work mapped to ${parentPath.toLowerCase()}.`,selectionReason:why,confusionWith:distractorRecords[0]?.conceptId};
}
'''

pattern = re.compile(r"function makeActivity\(r:any,why:string\):Activity\{.*?\nfunction score", re.S)
if not pattern.search(text):
    raise SystemExit("makeActivity function was not found")
text = pattern.sub(replacement + "function score", text, count=1)

render_pattern = re.compile(r"function render\(\)\{app\.innerHTML=(.*?)\}\napp\.addEventListener", re.S)
match = render_pattern.search(text)
if not match:
    raise SystemExit("render function was not found")
render_expr = match.group(1)
new_render = f"function render(){{app.innerHTML={render_expr};if(view==='session'||view==='feedback')document.querySelector('nav')?.remove()}}\napp.addEventListener"
text = render_pattern.sub(new_render, text, count=1)

text = text.replace("'2.1.0'", "'2.1.1'").replace('"2.1.0"', '"2.1.1"')
path.write_text(text, encoding="utf-8")

public_dir = path.parent.parent / "public"
sw_path = public_dir / "sw.js"
if sw_path.exists():
    sw = sw_path.read_text(encoding="utf-8")
    sw = sw.replace("2.1.0", "2.1.1")
    sw = re.sub(r"(CACHE(?:_NAME)?\s*=\s*['\"]).*?(['\"])", r"\1security-plus-v2.1.1\2", sw, count=1)
    sw_path.write_text(sw, encoding="utf-8")
manifest_path = public_dir / "manifest.webmanifest"
if manifest_path.exists():
    manifest_path.write_text(manifest_path.read_text(encoding="utf-8").replace("2.1.0", "2.1.1"), encoding="utf-8")

print("Generated question safeguards applied; version and cache set to 2.1.1")
