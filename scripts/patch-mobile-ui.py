from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: patch-mobile-ui.py <app.ts> <styles.css>")

app_path = Path(sys.argv[1])
css_path = Path(sys.argv[2])
app = app_path.read_text(encoding="utf-8")

old = """${exam?'':`<div class=\"branchButtons\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"teach\">Teach me</button><button data-special=\"forgot\">I forgot</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"guessed\">I guessed</button><button data-special=\"different\">Explain differently</button><button data-special=\"ms\">Microsoft example</button><button data-special=\"msp\">MSP example</button><button data-special=\"compare\">Compare concepts</button><button data-special=\"ai\">Ask AI</button></div><div class=\"confidence\"><b>Confidence</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>"""

new = """${exam?'':`<div class=\"confidence\"><b>How confident are you?</b>${(['I knew it','Fairly sure','Guessed','No idea'] as Confidence[]).map(c=>`<button data-confidence=\"${c}\" class=\"${confidence===c?'selected':''}\">${c}</button>`).join('')}</div>${guidance?`<div class=\"hint\"><b>Guidance</b><p>${esc(guidance)}</p></div>`:''}`}</section><button class=\"primary wide submitAnswer\" data-action=\"submit\" ${selected.length?'':'disabled'}>Submit answer</button>${exam?'':`<details class=\"helpPanel\"><summary>Need help or a different explanation?</summary><p class=\"muted\">These are learning tools, not answer choices.</p><div class=\"branchButtons helpActions\"><button data-special=\"dontknow\">I don’t know</button><button data-special=\"teach\">Teach me</button><button data-special=\"forgot\">I forgot</button><button data-special=\"confusing\">I’m confusing this</button><button data-special=\"guessed\">I guessed</button><button data-special=\"different\">Explain differently</button><button data-special=\"ms\">Microsoft example</button><button data-special=\"msp\">MSP example</button><button data-special=\"compare\">Compare concepts</button><button data-special=\"ai\">Ask AI</button></div></details>`}"""

if old not in app:
    raise SystemExit("Expected question layout fragment was not found; refusing an unsafe patch")

app_path.write_text(app.replace(old, new), encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
old_shell = ".shell{width:min(760px,100%);margin:auto;padding:18px 14px}"
new_shell = ".shell{width:min(760px,100%);margin:auto;padding:18px 14px calc(128px + env(safe-area-inset-bottom))}"
if old_shell not in css:
    raise SystemExit("Expected shell CSS was not found; refusing an unsafe patch")

css = css.replace(old_shell, new_shell)
css += """
.submitAnswer{position:sticky;bottom:calc(78px + env(safe-area-inset-bottom));z-index:8;margin-top:12px;box-shadow:0 10px 28px #000b}
.helpPanel{margin:12px 0 18px;border:1px solid #2a3950;border-radius:14px;background:#0d1522;padding:4px 12px}
.helpPanel summary{cursor:pointer;min-height:48px;display:flex;align-items:center;font-weight:700;color:#b9c7da}
.helpPanel summary::marker{color:#8fc9ff}
.helpPanel .muted{margin:0 0 10px;font-size:.88rem}
.helpActions button{background:transparent;border-style:dashed;color:#c4cfde;font-weight:600;min-height:44px}
.helpActions button:hover,.helpActions button:focus-visible{background:#152238}
.feedback .wide{margin-top:14px}
@media(max-height:700px){nav button{min-height:52px}.submitAnswer{bottom:calc(70px + env(safe-area-inset-bottom))}}
"""
css_path.write_text(css, encoding="utf-8")
print("Mobile UI patch applied")
