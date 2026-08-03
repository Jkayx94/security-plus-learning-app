from pathlib import Path
p=Path('src/content/security-plus-v3.2.ts');s=p.read_text(encoding='utf-8')
for key in ['Role-based','Attribute-based','Rule-based','Mandatory','Discretionary']:
    s=s.replace("'"+key+"':",'["'+key+'"]:')
    s=s.replace(key+':','["'+key+'"]:')
s=s.replace('user’s','the user').replace("user's",'the user').replace('organisation’s','the organisation').replace("organisation's",'the organisation')
p.write_text(s,encoding='utf-8')
