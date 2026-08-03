from pathlib import Path
import sys

app_path = Path(sys.argv[1])
source = app_path.read_text(encoding='utf-8')

# Boss hits belong to the active battle state in both genuine and isolated Test Mode.
# Genuine learning evidence, XP, rewards and history remain protected by testOnly checks.
anchor = "if(!testOnly){state.xp+=xp;"
replacement = "if(session?.bossId&&correct)session.bossCorrect=(session.bossCorrect||0)+1;\nif(!testOnly){state.xp+=xp;"
if anchor not in source:
    raise SystemExit('Could not find reward branch for boss hit repair')
source = source.replace(anchor, replacement, 1)

legacy_hit = "if(session?.bossId&&correct)session.bossCorrect=(session.bossCorrect||0)+1}else{"
if legacy_hit not in source:
    raise SystemExit('Could not find legacy genuine-only boss hit update')
source = source.replace(legacy_hit, "}else{", 1)

# Test Mode shield cosmetics must be rendered from the isolated equipped shield.
old_shield = "const id=state.testMode.enabled&&state.testMode.previewShield?state.testMode.previewShield:state.cosmetics.equippedShield;"
new_shield = "const id=state.testMode.enabled?(state.testMode.previewShield||state.testMode.equippedShield||state.cosmetics.equippedShield):state.cosmetics.equippedShield;"
if old_shield not in source:
    raise SystemExit('Could not find shield renderer')
source = source.replace(old_shield, new_shield, 1)

app_path.write_text(source, encoding='utf-8')

styles_path = app_path.with_name('styles.css')
styles = styles_path.read_text(encoding='utf-8')
marker = '/* v3.2.1 boss-hit and complete cosmetic preview repair */'
if marker not in styles:
    styles += r'''

/* v3.2.1 boss-hit and complete cosmetic preview repair */
.profileShield.shield-gold-style,
html[data-cosmetic="shield-gold-style"] .profileShield{
  border-color:#e4b64f;
  background:linear-gradient(145deg,#342713,#171006);
  box-shadow:0 0 0 2px #e4b64f55,0 10px 28px #0008;
  clip-path:polygon(50% 0,96% 18%,88% 74%,50% 100%,12% 74%,4% 18%);
  min-height:92px;
}
.profileShield.shield-gold-style span,
html[data-cosmetic="shield-gold-style"] .profileShield span{color:#ffd66f;transform:rotate(45deg)}
html[data-cosmetic="avatar-sentinel"] header>button:first-child{
  font-size:0;
  border-color:#64d8ff;
  background:radial-gradient(circle at 50% 35%,#244f74,#0a1421 68%);
}
html[data-cosmetic="avatar-sentinel"] header>button:first-child::before{
  content:"◈";
  font-size:1.7rem;
  color:#8be6ff;
  text-shadow:0 0 12px #4cc9ff;
}
'''
    styles_path.write_text(styles, encoding='utf-8')
