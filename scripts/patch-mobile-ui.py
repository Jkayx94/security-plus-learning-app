from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: patch-mobile-ui.py <app.ts> <styles.css>")

app_path = Path(sys.argv[1])
css_path = Path(sys.argv[2])
app = app_path.read_text(encoding="utf-8")

old = """${exam?'':`<div class=\"branchButtons\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"teach\">Teach me</button><button data-special=\"forgot\">I forgot</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"guessed\">I guessed</button><button data-special=\"different\">Explain differently</button><button data-special=\"ms\">Microsoft example</button><button data-special=\"msp\">MSP example</button><button data-special=\"compare\">Compare concepts</button><button data-special=\"ai\">Ask AI</button></div><div class=\"confidence\"><b>Confidence</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>"""

new = """${exam?'':`<div class=\"confidence\"><b>How confident are you?</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide submitAnswer\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>${exam?'':`<details class=\"flagPanel\"><summary>⚑ Flag how this felt</summary><div class=\"branchButtons flagActions\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"guessed\">I guessed</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"teach\">Teach me</button></div></details>`}"""

if old not in app:
    raise SystemExit("Expected question layout fragment was not found; refusing an unsafe patch")

app_path.write_text(app.replace(old, new), encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
old_shell = ".shell{width:min(760px,100%);margin:auto;padding:18px 14px}"
new_shell = ".shell{width:min(760px,100%);margin:auto;padding:18px 14px calc(112px + env(safe-area-inset-bottom))}"
if old_shell not in css:
    raise SystemExit("Expected shell CSS was not found; refusing an unsafe patch")

css = css.replace(old_shell, new_shell)
css += """
.submitAnswer{position:static;margin:14px 0 10px;box-shadow:none}
.flagPanel{margin:8px 0 24px;border:1px solid #2a3950;border-radius:12px;background:#0d1522;padding:2px 10px}
.flagPanel summary{cursor:pointer;min-height:46px;display:flex;align-items:center;justify-content:center;font-weight:700;color:#aebdd0;font-size:.92rem}
.flagPanel summary::marker{content:""}
.flagActions{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:4px 0 10px}
.flagActions button{background:#111c2c;border:1px solid #34445a;color:#d4dce8;font-weight:600;min-height:44px;font-size:.9rem}
.feedback .wide{position:static;margin:16px 0 20px}
body:has(.question) nav,body:has(.feedback) nav{display:none!important}
body:has(.question) .shell,body:has(.feedback) .shell{padding-bottom:calc(36px + env(safe-area-inset-bottom))!important}
.question,.feedback{min-height:auto;overflow:visible}
@media(max-width:420px){.flagActions{grid-template-columns:1fr}.confidence button{min-height:42px;font-size:.88rem}}
"""
css_path.write_text(css, encoding="utf-8")
print("Mobile UI patch applied")
