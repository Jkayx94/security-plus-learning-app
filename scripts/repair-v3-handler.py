from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: repair-v3-handler.py <app.ts>')

path=Path(sys.argv[1])
text=path.read_text(encoding='utf-8')
pattern=re.compile(r"(app\.addEventListener\('change',e=>\{const t=e\.target as HTMLInputElement;if\(t\.id==='import'.*?fr\.readAsText\(f\)\}\}\);)fr\.onload=.*?fr\.readAsText\(f\)\}\}\);\nasync function boot",re.S)
match=pattern.search(text)
if match:
    text=pattern.sub(match.group(1)+'\nasync function boot',text,count=1)
    path.write_text(text,encoding='utf-8')
    print('Removed duplicated import-handler tail')
elif "fr.readAsText(f)}});fr.onload=" in text:
    raise SystemExit('Duplicate import handler detected but safe repair pattern did not match')
else:
    print('Import handler already clean')
