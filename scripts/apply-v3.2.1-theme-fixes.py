from pathlib import Path
import sys

app_path = Path(sys.argv[1])
styles_path = app_path.with_name('styles.css')
styles = styles_path.read_text(encoding='utf-8')
marker = '/* v3.2.1 complete theme rendering */'

if marker not in styles:
    styles += r'''

/* v3.2.1 complete theme rendering */
html[data-theme="theme-blue"] body{
  background:radial-gradient(circle at top,#16345a 0,#090d14 46%);
}
html[data-theme="theme-blue"] header,
html[data-theme="theme-blue"] nav{
  background:#0b1728f2;
  border-color:#2d527c;
}
html[data-theme="theme-blue"] .primary{
  background:#1777d3;
  border-color:#78c2ff;
}
html[data-theme="theme-blue"] .eyebrow,
html[data-theme="theme-blue"] .pill{
  color:#8fc9ff;
}
html[data-theme="theme-blue"] .progress i{
  background:linear-gradient(90deg,#3ba0ff,#62dfb6);
}

html[data-theme="theme-purple"] body{
  background:radial-gradient(circle at top,#3b205c 0,#110b1b 48%);
}
html[data-theme="theme-purple"] header,
html[data-theme="theme-purple"] nav{
  background:#190f27f2;
  border-color:#65458a;
}
html[data-theme="theme-purple"] .card,
html[data-theme="theme-purple"] .profileSummary{
  background:#21142f;
  border-color:#604080;
}
html[data-theme="theme-purple"] button{
  background:#2a1940;
  border-color:#7653a0;
}
html[data-theme="theme-purple"] .primary{
  background:#7545b7;
  border-color:#c09af1;
}
html[data-theme="theme-purple"] .eyebrow,
html[data-theme="theme-purple"] .pill{
  color:#d2adff;
}
html[data-theme="theme-purple"] .progress i{
  background:linear-gradient(90deg,#b16cff,#ff82c8);
}

html[data-theme="theme-green"] body{
  background:radial-gradient(circle at top,#153f36 0,#07130f 48%);
}
html[data-theme="theme-green"] header,
html[data-theme="theme-green"] nav{
  background:#091d18f2;
  border-color:#2f6b59;
}
html[data-theme="theme-green"] .card,
html[data-theme="theme-green"] .profileSummary{
  background:#10251f;
  border-color:#356b5c;
}
html[data-theme="theme-green"] button{
  background:#163229;
  border-color:#467d6d;
}
html[data-theme="theme-green"] .primary{
  background:#19785f;
  border-color:#69d8b6;
}
html[data-theme="theme-green"] .eyebrow,
html[data-theme="theme-green"] .pill{
  color:#84e5c4;
}
html[data-theme="theme-green"] .progress i{
  background:linear-gradient(90deg,#38d39f,#c7e85b);
}

html[data-theme="theme-oled"],
html[data-theme="theme-oled"] body{
  background:#000;
}
html[data-theme="theme-oled"] header,
html[data-theme="theme-oled"] nav{
  background:#000f;
  border-color:#303030;
}
html[data-theme="theme-oled"] .card,
html[data-theme="theme-oled"] .profileSummary,
html[data-theme="theme-oled"] .bossArena,
html[data-theme="theme-oled"] .explanationPanel{
  background:#050505;
  border-color:#353535;
  box-shadow:none;
}
html[data-theme="theme-oled"] button{
  background:#0a0a0a;
  border-color:#404040;
}
html[data-theme="theme-oled"] .primary{
  background:#e8e8e8;
  border-color:#fff;
  color:#000;
}
html[data-theme="theme-oled"] .eyebrow,
html[data-theme="theme-oled"] .pill{
  color:#fff;
}
html[data-theme="theme-oled"] .progress i{
  background:#fff;
}

.cosmeticsScreen::before{
  content:"Active theme: " attr(data-active-theme);
  display:none;
}
'''
    styles_path.write_text(styles, encoding='utf-8')
