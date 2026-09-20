from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
index = root / 'index.html'
html = index.read_text(encoding='utf-8')

marker = '</style>'
if marker not in html:
    raise SystemExit('Main style block not found')

css = r'''
/* Mechatronics UI theme v2 — all application chrome is tinted; .notes-editor is the only white work surface. */
:root{
  --bg:#d8e5ed;
  --panel:#d7e5ed;
  --ink:#173047;
  --muted:#5d7689;
  --line:#a9c1cf;
  --danger:#a92525;
  --ok:#167864;
  --shadow:0 10px 28px rgba(24,55,78,.13);
  --mech-navy:#0d2236;
  --mech-navy-2:#16364e;
  --mech-steel:#cbdde7;
  --mech-steel-2:#dce9f0;
  --mech-steel-3:#e5eef3;
  --mech-cyan:#22c7df;
  --mech-blue:#2878d7;
}

html{background:#cbdbe5}
body{
  background:
    radial-gradient(circle at 12% 4%,rgba(34,199,223,.15),transparent 28rem),
    radial-gradient(circle at 92% 3%,rgba(40,120,215,.12),transparent 31rem),
    linear-gradient(180deg,#dce8ef 0,#d3e1e9 52%,#cadbe5 100%);
  color:var(--ink);
}

header{
  background:linear-gradient(115deg,#0c2032,#163c56);
  border-bottom:1px solid #3d627c;
  box-shadow:0 5px 18px rgba(7,25,39,.23);
  color:#edf8ff;
}
header h1{color:#f4fbff;letter-spacing:.01em}
header .statusbar{color:#76e2c4}
header button,
header input,
header select{
  background:#1b405a;
  color:#eef8ff;
  border-color:#54748a;
  box-shadow:none;
}
header button:hover{background:#25516d;border-color:#6b91a8}
header button.primary{
  background:linear-gradient(135deg,#1767c8,#13a9c4);
  color:#fff;
  border-color:#42cce0;
  box-shadow:0 4px 12px rgba(20,142,190,.25);
}
header input[type=date]{color-scheme:dark}

/* Main application surfaces: deliberately blue/steel, not near-white. */
main{background:transparent}
aside,.content,.notes-shell{
  background:#d4e2eb;
  border-color:#a9c0ce;
  box-shadow:var(--shadow);
}
aside{
  background:linear-gradient(180deg,#cfdee8,#c8d9e4);
}
.content{
  background:linear-gradient(180deg,#d5e4ec,#ccdde7);
}
aside h2,.weektitle{color:#153149}
.hint,.course-meta,.cloud-detail,.notes-course,.notes-save{color:#567184}

.viewbar{
  background:#c8dbe6;
  border:1px solid #aac1cf;
  border-radius:10px;
  padding:8px 10px;
}

button{
  background:#d4e3ec;
  color:#173047;
  border-color:#9fb9c8;
  box-shadow:0 1px 2px rgba(35,67,91,.06);
}
button:hover{background:#c6dbe7;border-color:#7da9bd}
button.primary{
  background:linear-gradient(135deg,#155fb5,#168fae);
  color:#fff;
  border-color:#257fa9;
}

input:not([type=checkbox]):not([type=radio]):not([type=color]),
select,
textarea{
  background:#dce8ef;
  color:#173047;
  border-color:#9fb9c8;
}
input:not([type=checkbox]):not([type=radio]):not([type=color]):focus,
select:focus,
textarea:focus{
  background:#e2edf3;
  outline:2px solid rgba(34,199,223,.20);
  border-color:#489db9;
}

/* Calendar frame + cells. Events keep their category colors. */
.calendar-wrap{
  background:#c5d8e4;
  border-color:#9fb9c8;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.22);
}
.calendar{background:#cbdde7}
.timehead,.dayhead{
  background:linear-gradient(180deg,#c5d9e5,#b9d0dd);
  color:#17354e;
  border-bottom-color:#91aebe;
}
.dayhead.weekend{background:linear-gradient(180deg,#bfd2df,#b4cad7)}
.times{
  background:#cbdde7;
  border-right-color:#a7bfcd;
}
.time-label{color:#567184}
.daycol{
  border-right-color:#afc5d2;
  background:
    repeating-linear-gradient(to bottom,
      #dce8ef 0,
      #dce8ef 23px,
      #c7d9e3 24px);
}
.daycol.weekend{
  background:
    repeating-linear-gradient(to bottom,
      #d4e2ea 0,
      #d4e2ea 23px,
      #bfd2de 24px);
}
.event{box-shadow:0 2px 6px rgba(22,49,70,.13)}
.event:hover{outline-color:rgba(22,96,138,.32)}
.event .status-comment-top{
  background:rgba(221,234,241,.95);
  border-color:rgba(120,83,45,.30);
}
.status-comment-list{
  background:#eadfca;
  border-color:#d3b47a;
}
.badge{
  background:rgba(207,224,234,.90);
  border-color:rgba(37,70,94,.22);
}

/* Lists and statistics surfaces. */
#listView{
  background:#ccdde7;
  border:1px solid #a8bfcd;
  border-radius:10px;
  overflow:hidden;
}
.list{background:#d7e5ed}
.list th{
  background:#bcd2df;
  color:#17354e;
}
.list td{background:#d8e6ee}
.list tbody tr:nth-child(even) td{background:#cfdee8}
.list th,.list td{border-bottom-color:#afc4d0}
.list tr:hover td{background:#c5d9e4}
.tag{background:#bed4e0;color:#29475e}

/* Sidebar/cloud/info surfaces. */
.cloud-box,.subbox,.info,.first-run{
  background:#c6dae5;
  border-color:#9fb9c8;
}
.cloud-box{box-shadow:inset 0 1px 0 rgba(255,255,255,.24)}
.first-run{color:#174b67}
.warning{
  background:#eadfca;
  border-color:#c9aa6e;
  color:#75500f;
}

/* Modal/form surfaces. */
.modal-back{background:rgba(7,24,38,.62)}
.modal{
  background:#cedee8;
  border:1px solid #9fb9c8;
}
.field input,.field select,.field textarea{
  background:#dce8ef;
  border-color:#9ab5c5;
  color:#173047;
}
.course-row{
  background:#c5d9e4;
  border-color:#9fb9c8;
}
.course-row input[type=text]{background:#dce8ef;border-color:#98b4c4}
.course-row input[type=color]{background:#c4d8e3;border-color:#98b4c4}
.new-course{border-color:#a6becb}

.legend{color:#567184}
.toast{background:#102d43}

/* Generic later feature-pack surfaces: steel tint instead of white.
   Explicit exclusions preserve event category backgrounds and the notes writing canvas. */
body :where(
  .stats-card,.stat-card,.quick-links-card,.mobile-view-card,
  [class*="stats-card"],[class*="stat-card"],
  [class*="stats-panel"],[class*="stat-panel"],
  [class*="quick-link"],[class*="view-card"],
  [class*="settings-card"],[class*="summary-card"]
){
  background-color:#cbdde7;
  border-color:#9fb9c8;
}
#statsPage,#mobileViewPage{
  background:#d3e2ea;
  color:#173047;
}

/* Notes: chrome follows theme. Only the actual editable writing area stays white. */
.notes-page{color:#173047}
.notes-shell{background:#cfdee8}
.notes-card{
  background:#c7d9e4;
  border-color:#9fb9c8;
}
.notes-toolbar{
  background:#bdd2df;
  border-color:#96b2c3;
}
.notes-toolbar button,
.notes-toolbar select,
.notes-toolbar input[type=color]{
  background:#d8e6ee;
  color:#173047;
  border-color:#91afc0;
}
.notes-toolbar button:hover{background:#c9dce7}
.notes-color-panel{
  background:#d2e2eb;
  color:#173047;
  border-color:#9fb9c8;
}
.notes-color-auto,.notes-color-more{
  background:#dce8ef;
  color:#173047;
}

/* DO NOT broaden this rule. The editor is intentionally the only white surface.
   No !important text color is used, so saved inline note colors/fonts remain authoritative. */
.notes-editor{
  background:#fff;
  color:#111827;
  border-color:#9fb8c7;
}
.notes-editor:focus{
  background:#fff;
  border-color:#4fa5c1;
  outline-color:rgba(34,199,223,.19);
}

/* Keep native color swatches and category/event colors intact. */
.swatch,input[type=color]{box-shadow:none}

/* Scrollbars — industrial blue. */
*{scrollbar-color:#7899ac #cfdee8}
*::-webkit-scrollbar{width:11px;height:11px}
*::-webkit-scrollbar-track{background:#cfdee8}
*::-webkit-scrollbar-thumb{background:#7899ac;border:3px solid #cfdee8;border-radius:999px}
*::-webkit-scrollbar-thumb:hover{background:#587d93}
'''.strip()

if '/* Mechatronics UI theme v2' not in html:
    html = html.replace(marker, css + '\n' + marker, 1)

index.write_text(html, encoding='utf-8')
print('Mechatronics UI theme v2 applied')
