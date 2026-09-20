from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
html = index.read_text(encoding='utf-8')

marker = '</style>'
if marker not in html:
    raise SystemExit('Main style block not found')

css = r'''
/* Mechatronics UI theme — visual shell only. Note content/formatting is intentionally untouched. */
:root{
  --bg:#e7eff5;
  --panel:#f2f7fa;
  --ink:#173047;
  --muted:#637b8e;
  --line:#bfd1dd;
  --ok:#167864;
  --shadow:0 10px 28px rgba(24,55,78,.10);
  --mech-navy:#0d2236;
  --mech-steel:#dbe8f0;
  --mech-steel-2:#edf4f8;
  --mech-cyan:#22c7df;
  --mech-blue:#2878d7;
}

html{background:#dce7ee}
body{
  background:
    radial-gradient(circle at 14% 5%,rgba(34,199,223,.10),transparent 25rem),
    radial-gradient(circle at 93% 2%,rgba(40,120,215,.08),transparent 28rem),
    linear-gradient(180deg,#edf4f8 0,#e5eef4 52%,#dfe9f0 100%);
  color:var(--ink);
}

header{
  background:linear-gradient(115deg,rgba(12,31,49,.98),rgba(17,52,76,.97));
  border-bottom:1px solid #31506a;
  box-shadow:0 5px 18px rgba(7,25,39,.18);
  color:#edf8ff;
}
header h1{color:#f4fbff;letter-spacing:.01em}
header .statusbar{color:#72e0c1}
header button,
header input,
header select{
  background:#18364f;
  color:#eef8ff;
  border-color:#42627b;
}
header button:hover{background:#214761}
header button.primary{
  background:linear-gradient(135deg,#1868c8,#12a9c5);
  color:#fff;
  border-color:#41cbe0;
  box-shadow:0 4px 12px rgba(20,142,190,.22);
}
header input[type=date]{color-scheme:dark}

aside,.content,.notes-shell{
  background:rgba(244,248,251,.94);
  border-color:#c1d2dd;
  box-shadow:var(--shadow);
}
aside{
  background:linear-gradient(180deg,#edf4f8,#e5eef4);
}
aside h2,.weektitle{color:#173047}
.hint,.course-meta,.cloud-detail,.notes-course,.notes-save{color:#60798c}

button{
  background:#f7fafc;
  color:#173047;
  border-color:#bed0dc;
  box-shadow:0 1px 2px rgba(35,67,91,.04);
}
button:hover{background:#e5f1f7;border-color:#91b8cb}
button.primary{
  background:linear-gradient(135deg,#155fb5,#168fae);
  color:#fff;
  border-color:#257fa9;
}

input:not([type=checkbox]):not([type=radio]):not([type=color]),
select,
textarea{
  background:#f8fbfd;
  color:#173047;
  border-color:#b8ccd9;
}
input:not([type=checkbox]):not([type=radio]):not([type=color]):focus,
select:focus,
textarea:focus{
  outline:2px solid rgba(34,199,223,.17);
  border-color:#55a8c4;
}

.calendar-wrap{
  background:#e9f1f6;
  border-color:#b8ccd9;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.65);
}
.timehead,.dayhead{
  background:linear-gradient(180deg,#dceaf2,#d2e3ed);
  color:#18364f;
  border-bottom-color:#aec5d3;
}
.dayhead.weekend{background:linear-gradient(180deg,#d6e3ec,#cddde7)}
.times{
  background:#e6eff5;
  border-right-color:#bdcfda;
}
.time-label{color:#617a8d}
.daycol{
  border-right-color:#c7d7e1;
  background:
    repeating-linear-gradient(to bottom,
      #f2f7fa 0,
      #f2f7fa 23px,
      #dfe9f0 24px);
}
.daycol.weekend{
  background:
    repeating-linear-gradient(to bottom,
      #edf3f7 0,
      #edf3f7 23px,
      #d8e4ec 24px);
}
.event{
  box-shadow:0 2px 6px rgba(22,49,70,.11);
}
.event:hover{
  outline-color:rgba(22,96,138,.28);
}

.list th{
  background:#dbe8f0;
  color:#18364f;
}
.list th,.list td{border-bottom-color:#c6d6e0}
.list tr:hover{background:#e7f1f6}
.tag{background:#dce9f1;color:#29475e}

.cloud-box,.subbox,.info{
  background:#e6f0f5;
  border-color:#bdd0dc;
}
.first-run{
  background:#e0f0f7;
  border-color:#9bc8da;
  color:#174b67;
}
.warning{
  background:#fff7e5;
  border-color:#e9ce85;
  color:#825510;
}

.modal-back{background:rgba(7,24,38,.55)}
.modal{
  background:#f1f6f9;
  border:1px solid #bfd1dc;
}
.field input,.field select,.field textarea{
  background:#fbfdfe;
  border-color:#b9ccd8;
  color:#173047;
}
.course-row{
  background:#edf4f8;
  border-color:#bfd0dc;
}
.course-row input[type=text]{background:#fbfdfe;border-color:#b8cbd8}

.legend{color:#60798c}
.badge{background:rgba(248,252,254,.84);border-color:rgba(37,70,94,.18)}
.toast{background:#102d43}

/* Notes: theme the chrome, preserve the editable page and every saved inline text color/font. */
.notes-page{color:#173047}
.notes-card{
  background:#e9f1f6;
  border-color:#bfd1dc;
}
.notes-toolbar{
  background:#dce9f1;
  border-color:#b7ccd9;
}
.notes-toolbar button,
.notes-toolbar select,
.notes-toolbar input[type=color]{
  background:#f8fbfd;
  color:#173047;
  border-color:#afc6d5;
}
.notes-toolbar button:hover{background:#e6f2f7}
.notes-color-panel{color:#173047}

/* Important: do not use !important on note text color.
   Inline colors saved in notes must continue to win naturally. */
.notes-editor{
  background:#fff;
  color:#111827;
  border-color:#b8cad6;
}
.notes-editor:focus{
  border-color:#62a9c3;
  outline-color:rgba(34,199,223,.17);
}

/* Feature surfaces added by later packs: give generic cards the same steel palette. */
.stats-card,.stat-card,.quick-links-card,.mobile-view-card,
[class*="stats-card"],[class*="stat-card"]{
  background:#edf4f8;
  border-color:#bfd1dc;
}

/* Scrollbars — subtle industrial blue. */
*{scrollbar-color:#91adbd #e4edf3}
*::-webkit-scrollbar{width:11px;height:11px}
*::-webkit-scrollbar-track{background:#e4edf3}
*::-webkit-scrollbar-thumb{background:#91adbd;border:3px solid #e4edf3;border-radius:999px}
*::-webkit-scrollbar-thumb:hover{background:#6f94a9}
'''.strip()

if '/* Mechatronics UI theme' not in html:
    html = html.replace(marker, css + '\n' + marker, 1)

index.write_text(html, encoding='utf-8')
print('Mechatronics UI theme applied')
