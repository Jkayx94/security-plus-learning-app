from pathlib import Path
p=Path('src/content/security-plus-v3.2.ts');s=p.read_text(encoding='utf-8')
for key in ['Role-based','Attribute-based','Rule-based','Mandatory','Discretionary']:
    s=s.replace("'"+key+"':",'["'+key+'"]:')
    s=s.replace(key+':','["'+key+'"]:')
s=s.replace('user’s','the user').replace("user's",'the user').replace('organisation’s','the organisation').replace("organisation's",'the organisation')
p.write_text(s,encoding='utf-8')
app=Path('src/app.ts');a=app.read_text(encoding='utf-8')
a=a.replace('function cosmeticsView(){return achievementsView()}\n','')
if 'function makeActivity(' not in a:
    marker='function scoreQuestion('
    compat="function makeActivity(r:any,why:string):Activity{const question=contentPack.questions.find(q=>q.conceptId===r?.conceptId&&q.review.approvedForLearn);if(!question)throw Error('No reviewed question is available for this concept.');return toActivity(question,why)}\n"
    a=a.replace(marker,compat+marker,1)
duplicate='<section class="bossArena"><div class="bossVisual ${s.bossType}" aria-hidden="true"><span class="bossCore">◆</span><b>${s.bossType===\'final\'?\'RISK TITAN\':s.bossType===\'domain\'?\'IDENTITY GATEKEEPER\':s.bossType===\'objective\'?\'CERTIFICATE GUARDIAN\':\'ROGUE PROCESS\'}</b></div>${bossConsole(s)}<section class="bossArena"><div class="bossVisual ${s.bossType}" aria-hidden="true"><span class="bossCore">◆</span><b>${s.bossType===\'final\'?\'RISK TITAN\':s.bossType===\'domain\'?\'IDENTITY GATEKEEPER\':s.bossType===\'objective\'?\'CERTIFICATE GUARDIAN\':\'ROGUE PROCESS\'}</b></div>${bossConsole(s)}'
single='<section class="bossArena"><div class="bossVisual ${s.bossType}" aria-hidden="true"><span class="bossCore">◆</span><b>${s.bossType===\'final\'?\'RISK TITAN\':s.bossType===\'domain\'?\'IDENTITY GATEKEEPER\':s.bossType===\'objective\'?\'CERTIFICATE GUARDIAN\':\'ROGUE PROCESS\'}</b></div>${bossConsole(s)}'
a=a.replace(duplicate,single)
app.write_text(a,encoding='utf-8')
