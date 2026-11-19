#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""suom1saundi's own manual, apart from ro:MINImal's: Finnish, German and Klingon (the words: manual/suomi_text.py), in suom1saundi's trashy dress (as in
github.com/g0rst/suom1saundi: comic type, a checkerboard, a ticker, stickers) with UFOs, 8-bit pixels and nonsense.

    python3 manual/suomi.py        ->  docs/suomi.html

suom1saundi is an experiment inside ro:MINImal, not a product: the manual says so. Its tables (tracks, knobs, factory
values, engines, start settings) come from the firmware's code (manual/codefacts.py). The way between the two
styles is not told here: a riddle only."""
import html
import pathlib
import re

import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from codefacts import facts, pct, pan  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = facts()
from suomi_text import CONTROLS, DESC, PANEL, ROLE, S, UI  # noqa: E402

LANGS = ("fi", "de", "tlh")
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ST = F["style"]["suomi"]
KEY = f"{NOTE_NAMES[ST['root'] % 12]}"
LI = {"fi": 0, "de": 1, "tlh": 2}


# -------------------------------------------------------------------------------- generated from the code ---
def gen(name, lang):
    trk = F["tracks"]["suomi"]
    if name == "tracks":
        rows = [(f"{UI['black'][lang]} {t + 1}", f"<b>{trk[t]}</b>", ROLE[t][0], ROLE[t][1 + LI[lang]]) for t in range(6)]
        return table(UI["th_track"][lang], rows)
    if name == "knobs":
        out = []
        for t in range(6):
            nm = trk[t]
            vals = F["su_def"][t]
            q = [24, vals[8], 40 if t == 0 else 0, 0]
            rows = []
            for page, names, vs in (("", F["sound"]["suomi"][t], vals[:4]), ("²", F["sound2"]["suomi"][t], q)):
                for k, (n, v) in enumerate(zip(names, vs)):
                    d = DESC.get(nm, {}).get(n, ("", "", ""))
                    rows.append((f"EDIT{page}&nbsp;K{k + 1}", f"<b>{n}</b>", str(v - 24) if n == "PITCH" else str(v),
                                 html.escape(d[LI[lang]])))
            out.append(f'<h3 id="{lang}-{nm.lower()}">{nm}</h3>' + table(UI["th_knob"][lang], rows))
        return "".join(out)
    if name == "mix":
        rows = [(f"<b>{trk[t]}</b>", pct(F["su_def"][t][4]), pan(F["su_def"][t][5]), pct(F["su_def"][t][6]),
                 pct(F["su_def"][t][7]), str(F["su_glide"][t])) for t in range(6)]
        return f'<h3>{UI["mix_head"][lang]}</h3>' + table(UI["th_mix"][lang], rows)
    if name == "engines":
        rows = []
        for e in range(len(F["eng_def"])):
            d = F["eng_def"][e]
            rows.append((f"<b>{F['engines']['suomi'][e]}</b>",
                         "<br>".join(f"{n}&nbsp;{v}" for n, v in zip(F["eng_sound"][e][0], d[:4])),
                         "<br>".join(f"{n}&nbsp;{v - 24 if n == 'PITCH' else v}" for n, v in zip(F["eng_sound"][e][1], d[8:12])),
                         pct(d[4])))
        return table(UI["th_eng"][lang], rows)
    if name == "pages":
        pg = F["pages"]
        rows = [("HOME", f"{pg[0]} · {pg[15]}", "TEMPO, SWING, DRIFT, DUCK · " + UI["pg_home"][lang]),
                ("EDIT", f"{pg[1]} · {pg[11]}", "SOUND, SOUND 2"),
                ("ENV", pg[2], "LEVEL, PAN, DELAY, REVERB"),
                ("FX", f"{pg[3]} · {pg[6]} · {pg[14]} · {pg[16]}", "DELAY, REVERB · SIDECHAIN · SLICE · SLICE LFO"),
                ("GLO", f"{pg[4]} · {pg[12]}", UI["pg_glo"][lang]),
                ("SEQ", f"{pg[5]} · {pg[7]} · {pg[8]}", "EUCLID · LINK · TIMING"),
                ("LFO", f"{pg[9]} · {pg[10]} · {pg[13]}", "LFO 1 · LFO 2 · MOD")]
        return table(UI["th_page"][lang], [(f"<b>{a}</b>", b, c) for a, b, c in rows])
    if name == "controls":
        return table(UI["th_ctl"][lang], [(f"<b>{c}</b>", d[lang]) for c, d in CONTROLS])
    raise KeyError(name)


def table(head, rows):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


# ------------------------------------------------------------------------------------------- pixel art ---
UFO = ["    .ooo.    ", "   .ooooo.   ", "  GGGGGGGGG  ", " GGGGGGGGGGGG", "GLGGLGGLGGLGG", "  ddddddddd  ", "   d     d   "]
COW = ["  wwwww ", " wkwwkww", "wwwwwwww", "wkkwwwkw", " w w w w"]
COL = {"o": "#b4ffc8", ".": "#5aaa78", "G": "#3cdc50", "L": "#fff078", "d": "#1e6e32", "w": "#ffffff", "k": "#111111"}


def sprite_rects(rows):
    return "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{COL[c]}"/>' for y, r in enumerate(rows)
                   for x, c in enumerate(r) if c != " ")


def sprite(rows, px, cls=""):
    w, h = len(rows[0]), len(rows)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{COL[c]}"{" class=\"lt\"" if c == "L" else ""}/>'
                    for y, r in enumerate(rows) for x, c in enumerate(r) if c != " ")
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w * px}" height="{h * px}" shape-rendering="crispEdges" '
            f'aria-hidden="true">{rects}</svg>')


# ---------------------------------------------------------------------------------------------- the page ---
CSS = """
:root{--hot:#ff1fd1;--lime:#b6ff00;--cyan:#00f0ff;--yel:#fff200;--acid:#aaff3c;--ink:#12001a;--paper:#fffdf2}
*{box-sizing:border-box}
html{background:var(--ink)}
body{margin:0;color:var(--ink);font:17px/1.55 "Comic Sans MS","Comic Neue","Chalkboard SE","Marker Felt",cursive;
 background:
  radial-gradient(#fff 1px,transparent 1.5px) 0 0/97px 89px,
  radial-gradient(var(--acid) 1px,transparent 1.5px) 40px 30px/131px 113px,
  repeating-conic-gradient(from 45deg,#1a0030 0 25%,#0b0012 0 50%) 0 0/48px 48px fixed}
a{color:#c800ff;font-weight:700}
a:hover{background:var(--yel);color:#000}
.ticker{position:sticky;top:0;z-index:9;overflow:hidden;white-space:nowrap;background:var(--acid);color:#000;
 border-bottom:4px dashed #000;font:400 12px/2.4 "Press Start 2P",ui-monospace,monospace}
.ticker span{display:inline-block;padding-left:100%;animation:tick 34s linear infinite}
@keyframes tick{to{transform:translateX(-100%)}}
header.top{text-align:center;padding:30px 14px 18px;color:#fff;position:relative;overflow:hidden;min-height:330px}
.sky{position:absolute;inset:0;pointer-events:none}
.fly{position:absolute;top:22px;left:-140px;animation:fly 19s linear infinite}
.fly .bob{animation:bob 1.3s ease-in-out infinite alternate}
@keyframes fly{to{transform:translateX(calc(100vw + 280px))}}
@keyframes bob{to{transform:translateY(14px) rotate(4deg)}}
.lt{animation:lt .5s steps(1) infinite}
@keyframes lt{50%{fill:#ff1fd1}}
.abduct{position:absolute;right:6%;bottom:8px;width:120px;height:170px}
.abduct .beam{position:absolute;left:28px;top:44px;width:64px;height:110px;
 background:linear-gradient(rgba(170,255,60,.55),rgba(170,255,60,.05));clip-path:polygon(35% 0,65% 0,100% 100%,0 100%);
 animation:beam 1.2s steps(2) infinite}
@keyframes beam{50%{opacity:.35}}
.abduct .u{position:absolute;left:21px;top:0}
.abduct .cow{position:absolute;left:44px;top:96px;animation:cow 3.6s ease-in infinite}
@keyframes cow{0%{transform:translateY(40px) rotate(0)}70%{transform:translateY(-34px) rotate(200deg);opacity:1}100%{transform:translateY(-50px) rotate(260deg);opacity:0}}
.logo{position:relative;font:900 clamp(40px,10.5vw,118px)/.9 Bangers,Impact,"Arial Black",sans-serif;margin:46px 0 0;
 letter-spacing:-.01em;background:linear-gradient(90deg,var(--hot),var(--yel),var(--acid),var(--cyan),var(--hot));
 background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:rb 6s linear infinite;
 filter:drop-shadow(5px 5px 0 #000) drop-shadow(-3px -3px 0 #ff00aa);transform:rotate(-3deg)}
@keyframes rb{to{background-position:300% 0}}
.pix{position:relative;margin:10px 0 0;font:400 13px/1.6 "Press Start 2P",ui-monospace,monospace;color:var(--acid);text-shadow:3px 3px 0 #000}
.tag{position:relative;display:inline-block;margin-top:14px;background:var(--hot);color:#fff;padding:6px 14px;transform:rotate(2deg);
 border:3px solid #fff;box-shadow:6px 6px 0 var(--acid);font-weight:700}
.langs{position:relative;margin:18px 0 0;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.langs a{background:#000;color:var(--acid);border:3px solid var(--acid);padding:6px 12px;text-decoration:none;box-shadow:4px 4px 0 var(--hot);
 font:400 11px/1.6 "Press Start 2P",ui-monospace,monospace}
.langs a[aria-current="true"]{background:var(--acid);color:#000}
.emu{position:relative;display:inline-block;margin:22px 0 4px;background:var(--hot);color:#fff;font:900 24px Bangers,Impact,sans-serif;padding:12px 22px;
 border:4px solid #000;box-shadow:8px 8px 0 #000;text-decoration:none;transform:rotate(-2deg)}
.emu:hover{background:var(--acid);color:#000;transform:rotate(2deg) scale(1.05)}
main{max-width:980px;margin:0 auto 60px;padding:0 12px}
.paper{background:var(--paper);border:5px solid #000;box-shadow:12px 12px 0 var(--hot),-8px -8px 0 var(--cyan);
 padding:20px clamp(14px,4vw,42px) 40px;position:relative}
.paper:before{content:"";position:absolute;inset:-5px -5px auto -5px;height:16px;
 background:repeating-linear-gradient(45deg,#000 0 14px,var(--yel) 14px 28px)}
.toc{background:#000;color:#fff;padding:12px 16px;border:3px dotted var(--cyan);transform:rotate(-.6deg);margin:26px 0}
.toc b{color:var(--yel);font:400 12px "Press Start 2P",ui-monospace,monospace}
.toc ol{margin:8px 0 0;columns:2 230px}
.toc a{color:var(--cyan)}
h2{font:900 30px/1.15 Bangers,Impact,"Arial Black",sans-serif;margin:46px 0 14px;color:#fff;background:#000;
 display:inline-block;padding:4px 14px;transform:rotate(-1.2deg);box-shadow:6px 6px 0 var(--hot)}
h2:nth-of-type(3n+2){box-shadow:6px 6px 0 var(--acid);transform:rotate(1deg)}
h2:nth-of-type(3n){box-shadow:6px 6px 0 var(--cyan)}
h2 svg{vertical-align:-2px;margin-right:8px}
h3{font:900 22px/1.2 Bangers,Impact,"Arial Black",sans-serif;margin:28px 0 6px;color:#c800ff;text-shadow:2px 2px 0 var(--lime)}
p,li{max-width:72ch}
.tw{overflow-x:auto;margin:10px 0 18px}
table{border-collapse:collapse;min-width:100%;font-size:15.5px;background:#fff}
th{background:#000;color:var(--yel);font:400 11px "Press Start 2P",ui-monospace,monospace;text-align:left;padding:9px 10px}
td{border:2px solid #000;padding:6px 10px;vertical-align:top}
tbody tr:nth-child(odd){background:#f3ffe4}
tbody tr:hover{background:var(--yel)}
.sticker{display:block;background:var(--acid);border:3px solid #000;padding:12px 16px;margin:18px 0;max-width:62ch;
 transform:rotate(-1.4deg);box-shadow:7px 7px 0 #000;font-weight:700}
.sticker:nth-of-type(even){background:var(--cyan);transform:rotate(1.2deg)}
.note{border-left:8px solid var(--hot);padding:4px 12px;background:#fff0fb}
pre.panel{background:#000;color:var(--acid);padding:14px;overflow:auto;border-left:8px solid var(--hot);font:12px/1.45 ui-monospace,Menlo,monospace}
.blink{animation:bl 1s steps(1) infinite;color:var(--yel)}
@keyframes bl{50%{opacity:0}}
.construct{margin:30px auto 0;text-align:center;font:400 11px/1.8 "Press Start 2P",monospace;color:#000;
 background:repeating-linear-gradient(-45deg,var(--yel) 0 18px,#000 18px 36px);padding:12px}
.construct span{background:var(--yel);padding:4px 10px}
footer{color:#fff;text-align:center;font-size:14px;padding:0 12px 40px}
footer .counter{display:inline-block;background:#000;color:var(--acid);font:400 16px "Press Start 2P",monospace;
 border:2px inset #777;padding:4px 8px;letter-spacing:.2em}
footer a{color:var(--acid)}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def fmt(t):
    return t.replace("{bpm}", str(ST["bpm"])).replace("{key}", KEY)


def render(lang):
    toc, body = [], []
    small = '<svg viewBox="0 0 13 7" width="39" height="21" aria-hidden="true"><use href="#ufo"/></svg>'
    for i, (head, blocks) in enumerate(S):
        hid = f"{lang}-{i + 1}"
        toc.append(f'<li><a href="#{hid}">{head[lang]}</a></li>')
        body.append(f'<h2 id="{hid}">{small}{head[lang]}</h2>')
        for b in blocks:
            if b[0] == "p":
                body.append(f"<p>{fmt(b[1][lang])}</p>")
            elif b[0] == "note":
                body.append(f'<p class="note">{fmt(b[1][lang])}</p>')
            elif b[0] == "pre":
                body.append(f'<pre class="panel">{html.escape(b[1])}</pre>')
            elif b[0] == "ol":
                body.append("<ol>" + "".join(f"<li>{fmt(x[lang])}</li>" for x in b[1]) + "</ol>")
            elif b[0] == "sticker":
                body.append(f'<aside class="sticker">{fmt(b[1][lang])}</aside>')
            elif b[0] == "ul":
                body.append("<ul>" + "".join(f"<li>{fmt(x[lang])}</li>" for x in b[1]) + "</ul>")
            elif b[0] == "gen":
                body.append(gen(b[1], lang))
    return (f'<nav class="toc"><b>{UI["toc"][lang]}</b><ol>{"".join(toc)}</ol></nav>' + "".join(body))


def page():
    emu = ("https://joakimeriksson.github.io/fm1-emu/?package=https%3A%2F%2Fg0rst.github.io%2Fro-MINImal%2F"
           "suom1saundi.fwsc&amp;name=suom1saundi")
    arts = []
    for l in LANGS:
        arts.append(f'''<div class="lang" id="m-{l}" lang="{l}"{"" if l == "fi" else " hidden"}>
<div class="ticker" aria-hidden="true"><span>{html.escape(UI["ticker"][l])}</span></div>
<header class="top">
  <div class="sky" aria-hidden="true">
    <div class="fly"><div class="bob">{sprite(UFO, 9)}</div></div>
    <div class="abduct"><div class="beam"></div><div class="u">{sprite(UFO, 6)}</div><div class="cow">{sprite(COW, 4)}</div></div>
  </div>
  <p class="logo">suom1saundi</p>
  <p class="pix">{UI["pix"][l]}</p>
  <div class="tag">{UI["tag"][l]} {F["commit"]} <span class="blink">{UI["new"][l]}</span></div>
  <nav class="langs" aria-label="kieli"><a href="#fi" data-l="fi">suomi</a><a href="#de" data-l="de">deutsch</a><a href="#tlh" data-l="tlh">tlhIngan Hol</a><a href="index.html">⌂ {UI["home"][l]}</a></nav>
  <a class="emu" href="{emu}">{UI["emu"][l]}</a>
</header>
<main><div class="paper">
{render(l)}
<div class="construct"><span>{UI["construct"][l]}</span></div>
</div></main>
<footer><p><span class="counter">000{(int(F["commit"], 16) % 9000 + 1000) if F["commit"] else 6666}</span> {UI["counter"][l]}</p>
<p>{UI["build"][l]} {F["date"]} · {F["commit"]} · <a href="https://github.com/g0rst/ro-MINImal">github.com/g0rst/ro-MINImal</a> · MIT</p></footer>
</div>''')
    return f'''<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>suom1saundi – käyttöohje · Handbuch · lo'meH paq</title>
<!-- written by manual/suomi.py from the firmware's code: do not edit by hand -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&family=Press+Start+2P&display=swap">
<style>{CSS}</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><symbol id="ufo" viewBox="0 0 13 7" shape-rendering="crispEdges">{sprite_rects(UFO)}</symbol></defs></svg>
{"".join(arts)}
<script>
(function () {{
  var langs = ["fi", "de", "tlh"];
  function pick() {{
    var h = location.hash.replace("#", "").split("-")[0];
    if (langs.indexOf(h) >= 0) return h;
    var n = (navigator.language || "fi").toLowerCase();
    return n.slice(0, 3) === "tlh" ? "tlh" : n.slice(0, 2) === "de" ? "de" : "fi";
  }}
  function show() {{
    var l = pick();
    langs.forEach(function (k) {{ document.getElementById("m-" + k).hidden = k !== l; }});
    document.documentElement.lang = l;
    Array.prototype.forEach.call(document.querySelectorAll(".langs a[data-l]"), function (a) {{
      a.setAttribute("aria-current", a.getAttribute("data-l") === l ? "true" : "false");
    }});
  }}
  window.addEventListener("hashchange", function () {{ var lang = location.hash.indexOf("-") < 0; show(); if (lang) window.scrollTo(0, 0); }});
  show();
}})();
</script>
</body>
</html>
'''


def main():
    out = page()
    dest = ROOT / "docs" / "suomi.html"
    dest.write_text(out, encoding="utf-8")
    words = {l: len(re.sub(r"<[^>]+>", " ", render(l)).split()) for l in LANGS}
    print(f"{dest}: {len(out)} bytes; words {words}")


if __name__ == "__main__":
    main()
