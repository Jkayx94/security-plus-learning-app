from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: repair-v3-handler.py <app.ts>')

path=Path(sys.argv[1])
text=path.read_text(encoding='utf-8')
marker="});fr.onload="
boot="\nasync function boot"
if marker in text:
    start=text.index(marker)
    end=text.index(boot,start)
    text=text[:start+3]+text[end:]
    path.write_text(text,encoding='utf-8')
    print('Removed duplicated import-handler tail')
else:
    print('Import handler already clean')
