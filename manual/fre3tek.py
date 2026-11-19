#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""FRE3tek's manual, apart from the others: German and English, dressed as a photocopied teknival flyer (black on
grey paper, stencil type, tape, one dark red). Tables come from the firmware's code (manual/codefacts.py).

    python3 manual/fre3tek.py      ->  docs/fre3tek.html
"""
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from codefacts import facts, pct, pan  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = facts()
LANGS = ("de", "en")
ST = F["style"]["tek"]
NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][ST["root"] % 12]


def L(de, en):
    return {"de": de, "en": en}


UI = {
    "sub": L(f"free tekno · acid · mental · tribe · {ST['bpm']} bpm · ein versuch in ro:MINImal",
             f"free tekno · acid · mental · tribe · {ST['bpm']} bpm · an experiment inside ro:MINImal"),
    "toc": L("inhalt", "contents"),
    "emu": L("▶ im fm-1-emulator: ro:MINImal laden, HOME 2 s halten", "▶ in the fm-1 emulator: load ro:MINImal, hold HOME 2 s"),
    "greet": L("Respekt an alle Soundsystems, die Leute an den Reglern und die, die bis zum Morgen tanzen. "
               "<b>Free all Anarchists!</b>",
               "Respect to every sound system, the people at the faders and those who dance till the morning. "
               "<b>Free all Anarchists!</b>"),
    "th_track": L(["taste", "spur", "rolle"], ["key", "track", "role"]),
    "th_knob": L(["regler", "name", "werk"], ["knob", "name", "factory"]),
    "th_mix": L(["spur", "pegel", "pan", "delay", "hall", "duck"], ["track", "level", "pan", "delay", "reverb", "duck"]),
    "black": L("schwarz", "black"),
    "build": L("aus dem code gebaut", "built from the code"),
}

ROLE = [
    L("Die Kick ist der Bass: verzerrt, lange tonale Fahne, vier auf den Boden, auf die Tonart gestimmt",
      "The kick is the bass: distorted, a long tonal tail, four on the floor, tuned to the key"),
    L("303-Linie: ein kurzes Motiv immer wieder, Akzent fest im Motiv, Slide in die Oktave",
      "a 303 line: a short motif over and over, the accent fixed in it, a slide into the octave"),
    L("offene Hats auf dem Offbeat, darunter ein Sechzehntel-Ride mit Chance", "open hats on the off-beat, a sixteenth ride under them at a chance"),
    L("zwei FM-Toms, polyrhythmisch: fünf oder sieben in zwölf oder sechzehn", "two FM toms, polyrhythmic: five or seven in twelve or sixteen"),
    L("das Mental-Kreischen: eine Säge mit Vibrato", "the mental scream: a saw with vibrato"),
    L("Rauschen als Riser und Fall, die Sirene vor dem Drop", "noise as riser and fall, the siren before the drop"),
]

S = []


def sec(de, en, *blocks):
    S.append((L(de, en), blocks))


sec("Was das ist", "What it is",
    ("p", L("<b>FRE3tek</b> ist der dritte Stil in ro:MINImal: Free Tekno, wie er auf Free Partys und Teknivals läuft, roh, schnell "
            "und repetitiv, mit Acid, Mental und Tribe. Dieselbe Maschine, dasselbe Panel, andere Stimmen und andere Regeln. "
            f"Er startet mit {ST['bpm']} BPM, gerade, in {NOTE} phrygisch.",
            "<b>FRE3tek</b> is the third style in ro:MINImal: free tekno as it runs at free parties and teknivals, raw, fast and "
            "repetitive, with acid, mental and tribe. The same machine, the same panel, other voices and other rules. "
            f"It starts at {ST['bpm']} BPM, straight, in {NOTE} phrygian.")),
    ("tape", L("Ein Versuch, kein Produkt. Wird die Rechenzeit des FM-1 knapp, fliegt er zusammen mit suom1saundi raus.",
               "An experiment, not a product. Should the FM-1 run short of time, it goes along with suom1saundi.")))

sec("Rein und raus", "In and out",
    ("ol", [L("<b>HOME</b> 2 Sekunden halten. Ein kurzer Tipp blättert wie immer die Seiten, kürzer gehalten passiert nichts.",
              "Hold <b>HOME</b> for 2 seconds. A short tap turns the pages as ever; a shorter hold does nothing."),
            L("Das Bild zieht sich zusammen wie eine alte Röhre, die Musik schmatzt weg. Eine Boxenwand pumpt viermal im Takt, "
              "dann knallt der Name rein, die 3 in Dunkelrot.",
              "The picture collapses like an old tube, the music smacks out. A wall of speakers pumps four times, then the name "
              "slams in, its 3 dark red."),
            L("Neuer Groove in FRE3tek. Die Musik startet mit dem Überblenden von vorn.", "A new groove in FRE3tek. The music starts again with the fade."),
            L("<b>HOME</b> 2 Sekunden halten: zurück in den Stil, aus dem du kamst. Jeder Druck überspringt die Show.",
              "Hold <b>HOME</b> 2 seconds: back to the style you came from. Any touch skips the show.")]))

sec("Warnung", "Warning",
    ("ul", [L("Lief bisher nur im Simulator und Emulator, <b>nicht auf einem echten FM-1</b>.", "Has run in the simulator and emulator only, <b>not on a real FM-1</b>."),
            L("Custom-Firmware kann ein Gerät unbrauchbar machen. Kenne den Weg zurück zur M-VAVE-Firmware.",
              "Custom firmware can brick a device. Know the way back to M-VAVE's firmware."),
            L("Laut ist gut, taub ist schlecht: Gehörschutz an der Anlage.", "Loud is good, deaf is not: ear plugs at the rig.")]))

sec("Die sechs Spuren", "The six tracks", ("gen", "tracks"))

sec("Klänge ab Werk", "Factory sounds",
    ("p", L("Aus dem Code gelesen. <b>EDIT</b> öffnet SOUND, nochmal <b>EDIT</b> SOUND 2. Die Kick, die Säure und die Hats sind "
            "die Stimmen von suom1saundi, TRIBE ist die FM-Percussion von ro:MINImal, gestimmt wie Toms.",
            "Read from the code. <b>EDIT</b> opens SOUND, <b>EDIT</b> again SOUND 2. The kick, the acid and the hats are "
            "suom1saundi's voices, TRIBE is ro:MINImal's FM percussion tuned as toms.")),
    ("gen", "knobs"), ("gen", "mix"),
    ("p", L("SCREAM ist die Engine 8-BIT als Säge (WAVE SAW) mit viel VIBRATO, SIREN die Engine NOISE als Riser über einen Takt. "
            "Auf GROOVE 2 lassen sich beide gegen STAB, CLICK oder die anderen tauschen.",
            "SCREAM is the 8-BIT engine as a saw (WAVE SAW) with a lot of VIBRATO, SIREN the NOISE engine as a riser over a bar. "
            "On GROOVE 2 both can be swapped for STAB, CLICK or the others.")))

sec("Die Regeln", "The rules",
    ("ul", [L("<b>KICK</b>: jeder Viertel, auf die Tonart gestimmt; manchmal ein Doppel vor dem Takt. In C pausiert sie gern die "
              "letzten vier Steps: der Drop.", "<b>KICK</b>: every quarter, tuned to the key; now and then a double before the bar. In "
              "C it likes to pause for the last four steps: the drop."),
            L("<b>ACID</b>: ein kurzes Motiv aus drei oder vier Tönen (Grundton, Oktave, Quinte), immer wieder: das ist Tekno. "
              "Der Akzent sitzt fest an einer Stelle des Motivs; ist es drei lang, wandert er gegen die Kick. In die Oktave "
              "wird geslidet.",
              "<b>ACID</b>: a short motif of three or four notes (root, octave, fifth), again and again: that is tekno. The "
              "accent sits on one place of the motif; three long, it walks against the kick. It slides up to the octave."),
            L("<b>HAT</b>: offen auf jedem Offbeat, betont; dazwischen ein Ride mit 25 oder 50 %.", "<b>HAT</b>: open on every off-beat, accented; between them a ride at 25 or 50 %."),
            L("<b>TRIBE</b>: zwei Toms, tief auf dem Grundton, hoch auf der Quinte, Euclid fünf oder sieben in zwölf oder "
              "sechzehn. 12 gegen 16: das Muster trifft die Kick erst nach drei Takten wieder.",
              "<b>TRIBE</b>: two toms, low on the root, high on the fifth, euclidean five or seven in twelve or sixteen. 12 "
              "against 16: the figure meets the kick again only after three bars."),
            L("<b>B</b> variiert, <b>C</b> rollt die Toms zum Takt hoch und lässt die Kick fallen, <b>D</b> geht in die Nachbartonart.",
              "<b>B</b> varies, <b>C</b> rolls the toms up to the bar and drops the kick, <b>D</b> moves to a related key.")]))

sec("Live spielen", "Playing live",
    ("ul", [L("<b>Drop</b>: SEL auf KICK – die Kick ist weg, die Pumpe bleibt. Nochmal SEL: Kick zurück.",
              "<b>Drop</b>: SEL on KICK – the kick is gone, the pump stays. SEL again: the kick is back."),
            L("<b>Säure auf</b>: ACID, EDIT, CUTOFF langsam hoch; LFO 1 auf CUTOFF, RATE 4 BAR für die lange Spannung.",
              "<b>Acid up</b>: ACID, EDIT, CUTOFF slowly up; LFO 1 on CUTOFF, RATE 4 BAR for the long tension."),
            L("<b>Beat Repeat</b>: SEL halten und weiße Taste 1 bis 4 – Viertel bis Zweiunddreißigstel, solange du hältst.",
              "<b>Beat repeat</b>: hold SEL and white key 1 to 4 – a quarter down to a thirty-second, as long as you hold."),
            L("<b>Sirene</b>: SIREN mit SEL reinholen, SWEEP nach rechts, RESO hoch.", "<b>Siren</b>: bring SIREN in with SEL, SWEEP to the right, RESO up."),
            L("<b>Mental</b>: SCREAM rein, VIBRATO voll, DRIVE hoch, DRIFT auf 80.", "<b>Mental</b>: SCREAM in, VIBRATO full, DRIVE up, DRIFT to 80."),
            L("<b>Summe</b>: GROOVE 2 FILTER nach links für das Abtauchen, wieder in die Mitte für den Einschlag.",
              "<b>The sum</b>: GROOVE 2 FILTER to the left to dive, back to the middle for the impact.")]))

sec("Rezepte", "Recipes",
    ("ul", [L("<b>Tekk-Bums</b>: KICK DECAY 110, DRIVE 120, SWEEP 40. Der Bass ist die Kick.", "<b>Tekk boom</b>: KICK DECAY 110, DRIVE 120, SWEEP 40. The bass is the kick."),
            L("<b>Tribe-Wald</b>: TRIBE ALGORITHM 12, SEQ HITS 7, TIMING TRACK −2.", "<b>Tribe forest</b>: TRIBE ALGORITHM 12, SEQ HITS 7, TIMING TRACK −2."),
            L("<b>Acid-Spirale</b>: ACID RESO 120, ENVMOD 100, LFO 2 auf DECAY, SHAPE RAND.", "<b>Acid spiral</b>: ACID RESO 120, ENVMOD 100, LFO 2 on DECAY, SHAPE RAND."),
            L("<b>Morgengrauen</b>: TEMPO 165, KICK DECAY 70, HAT CHIP hoch, AIR 50 %.", "<b>Dawn</b>: TEMPO 165, KICK DECAY 70, HAT CHIP up, AIR 50 %.")]))

sec("Dobrou noc", "Dobrou noc",
    ("p", L("<b>SAVE</b> 2 Sekunden halten: speichert, die Röhre geht aus, die Musik schmatzt weg, und in Dunkelrot steht "
            "„DOBROU NOC“ – gute Nacht auf Tschechisch, ein Gruß an die Free-Tekno-Szene dort. Dann dunkel und still, bis du "
            "ausschaltest oder etwas berührst.",
            "Hold <b>SAVE</b> for 2 seconds: it saves, the tube goes out, the music smacks away, and in dark red it says "
            "“DOBROU NOC” – good night in Czech, a greeting to the free tekno scene there. Then dark and silent until you "
            "switch off or touch something.")))

sec("Kleingedrucktes", "Small print",
    ("ul", [L("Im Simulator gezählt: im schlimmsten Fall etwa so viel Rechenzeit wie suom1saundi, grob 40–70 % des FM-1, mit "
              "GRAIN auf zwei Spuren bis zu 90 %. Am Gerät nicht gemessen.",
              "Counted in the simulator: at worst about as much time as suom1saundi, roughly 40–70 % of the FM-1, with GRAIN on "
              "two tracks up to 90 %. Not measured on the device."),
            L("Ohne suom1saundi gebaut (ROMI_SUOMI=0) gibt es FRE3tek nicht: er spielt dessen Stimmen.",
              "Built without suom1saundi (ROMI_SUOMI=0) there is no FRE3tek: it plays its voices."),
            L("Gebaut auf fm1-base und felucca-bsp. MIT-Lizenz. Nicht mit M-VAVE verbunden.", "Built on fm1-base and felucca-bsp. MIT licence. Not affiliated with M-VAVE.")]))


def table(head, rows):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def gen(name, lang):
    trk = F["tracks"]["tek"]
    if name == "tracks":
        return table(UI["th_track"][lang], [(f"{UI['black'][lang]} {t + 1}", f"<b>{trk[t]}</b>", ROLE[t][lang]) for t in range(6)])
    if name == "knobs":
        out = []
        for t in range(4):
            d = F["tek_def"][t]
            q = [24, d[8], 50 if t == 0 else 0, 0]
            rows = [(f"EDIT K{k + 1}", f"<b>{n}</b>", str(v)) for k, (n, v) in enumerate(zip(F["sound"]["tek"][t], d[:4]))]
            rows += [(f"EDIT² K{k + 1}", f"<b>{n}</b>", str(v - 24 if n == "PITCH" else v))
                     for k, (n, v) in enumerate(zip(F["sound2"]["tek"][t], q))]
            out.append(f"<h3>{trk[t]}</h3>" + table(UI["th_knob"][lang], rows))
        return "".join(out)
    if name == "mix":
        rows = [(f"<b>{trk[t]}</b>", pct(F["tek_def"][t][4]), pan(F["tek_def"][t][5]), pct(F["tek_def"][t][6]),
                 pct(F["tek_def"][t][7]), pct(F["tek_sc"][t])) for t in range(4)]
        return "<h3>mix</h3>" + table(UI["th_mix"][lang], rows)
    raise KeyError(name)


CSS = """
:root{--paper:#e9e7e0;--ink:#0d0d0c;--red:#8b0f1a;--soft:#55524c}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:17px/1.55 "Special Elite","Courier New",ui-monospace,monospace;background:var(--paper);
 background-image:
  repeating-radial-gradient(circle at 17% 23%,rgba(0,0,0,.06) 0 1px,transparent 1px 3px),
  repeating-linear-gradient(0deg,rgba(0,0,0,.035) 0 1px,transparent 1px 4px),
  radial-gradient(ellipse at 50% 0,rgba(255,255,255,.4),transparent 70%)}
.wrap{max-width:860px;margin:0 auto;padding:22px 16px 80px}
.top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;text-transform:lowercase}
.langs a{color:var(--ink);text-decoration:none;border:2px solid var(--ink);padding:3px 10px;margin-left:6px}
.langs a[aria-current="true"]{background:var(--ink);color:var(--paper)}
header.flyer{position:relative;margin:26px 0 10px;padding:22px 18px 26px;border:6px solid var(--ink);background:#f3f1ea;
 transform:rotate(-.8deg);box-shadow:8px 8px 0 var(--ink)}
header.flyer:before,header.flyer:after{content:"";position:absolute;width:110px;height:30px;background:rgba(230,215,150,.75);
 top:-16px;transform:rotate(-6deg)}
header.flyer:before{left:18px}
header.flyer:after{right:22px;transform:rotate(5deg)}
h1{margin:0;font:400 clamp(54px,15vw,132px)/.9 "Black Ops One","Stardos Stencil",Impact,sans-serif;letter-spacing:.02em}
h1 .r{color:var(--red)}
.sub{margin:10px 0 0;font-size:15px;text-transform:uppercase;letter-spacing:.08em}
.stack{display:flex;gap:6px;margin-top:18px}
.stack i{display:block;width:44px;height:44px;border:3px solid var(--ink);border-radius:2px;
 background:radial-gradient(circle,var(--ink) 0 5px,#777 6px 13px,var(--ink) 14px 15px,transparent 16px)}
.stack i:nth-child(odd){animation:pump .333s steps(1) infinite}
@keyframes pump{50%{transform:scale(1.06)}}
.emu{display:inline-block;margin-top:16px;color:var(--paper);background:var(--red);padding:6px 12px;text-decoration:none;
 border:3px solid var(--ink);transform:rotate(1deg)}
.toc{margin:28px 0;padding:12px 16px;border:3px dashed var(--ink);columns:2 220px}
.toc b{display:block;font-family:"Black Ops One",Impact,sans-serif;font-weight:400;text-transform:uppercase}
.toc a{display:block;color:var(--ink)}
section{margin:44px 0 0}
h2{display:inline-block;margin:0 0 12px;padding:4px 12px 2px;background:var(--ink);color:var(--paper);
 font:400 28px/1.15 "Black Ops One",Impact,sans-serif;text-transform:uppercase;transform:rotate(-1deg)}
section:nth-of-type(even) h2{transform:rotate(1deg);box-shadow:5px 5px 0 var(--red)}
h2 .n{color:var(--red);margin-right:10px}
section:nth-of-type(even) h2 .n{color:var(--paper)}
h3{font:400 20px "Black Ops One",Impact,sans-serif;margin:24px 0 6px;text-transform:uppercase}
p,li{max-width:70ch}
.tape{position:relative;display:block;margin:20px 0;padding:14px 16px;background:#fbfaf4;border:2px solid var(--ink);
 transform:rotate(-1.5deg);max-width:60ch}
.tape:before{content:"";position:absolute;left:40%;top:-14px;width:90px;height:24px;background:rgba(230,215,150,.8);transform:rotate(3deg)}
.tw{overflow-x:auto;margin:8px 0 16px}
table{border-collapse:collapse;min-width:100%;background:#f7f6f0}
th{background:var(--ink);color:var(--paper);text-align:left;padding:6px 10px;font-weight:400;text-transform:uppercase;font-size:14px}
td{border:2px solid var(--ink);padding:5px 10px;vertical-align:top}
b{color:var(--ink)}
.greet{margin:56px 0 0;padding:16px;border-top:6px solid var(--ink);border-bottom:6px solid var(--ink);text-align:center;font-size:18px}
.greet b{color:var(--red);font-family:"Black Ops One",Impact,sans-serif;font-weight:400;font-size:24px;letter-spacing:.04em}
footer{margin-top:24px;font-size:13px;color:var(--soft);text-align:center}
footer a{color:var(--ink)}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def render(lang):
    toc, body = [], []
    for i, (head, blocks) in enumerate(S):
        hid = f"{lang}-{i + 1}"
        toc.append(f'<a href="#{hid}">{i + 1:02d} · {head[lang]}</a>')
        body.append(f'<section><h2 id="{hid}"><span class="n">{i + 1:02d}</span>{head[lang]}</h2>')
        for b in blocks:
            if b[0] == "p":
                body.append(f"<p>{b[1][lang]}</p>")
            elif b[0] == "tape":
                body.append(f'<aside class="tape">{b[1][lang]}</aside>')
            elif b[0] in ("ul", "ol"):
                body.append(f"<{b[0]}>" + "".join(f"<li>{x[lang]}</li>" for x in b[1]) + f"</{b[0]}>")
            elif b[0] == "gen":
                body.append(gen(b[1], lang))
        body.append("</section>")
    return f'<nav class="toc"><b>{UI["toc"][lang]}</b>{"".join(toc)}</nav>' + "".join(body)


def page():
    emu = ("https://joakimeriksson.github.io/fm1-emu/?package=https%3A%2F%2Fg0rst.github.io%2Fro-MINImal%2F"
           "rominimal.fwsc&amp;name=ro%3AMINImal")
    arts = []
    for l in LANGS:
        arts.append(f'''<article id="m-{l}" lang="{l}"{"" if l == "de" else " hidden"}>
<header class="flyer">
  <h1>FRE<span class="r">3</span>TEK</h1>
  <p class="sub">{UI["sub"][l]}</p>
  <div class="stack" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <a class="emu" href="{emu}">{UI["emu"][l]}</a>
</header>
{render(l)}
<p class="greet">{UI["greet"][l]}</p>
</article>''')
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FRE3tek – Handbuch · Manual</title>
<!-- written by manual/fre3tek.py from the firmware's code: do not edit by hand -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Special+Elite&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="top"><span>ro:MINImal · FRE3tek · {F["date"]} · build {F["commit"]}</span>
<nav class="langs"><a href="#de" data-l="de">deutsch</a><a href="#en" data-l="en">english</a></nav></div>
{"".join(arts)}
<footer>{F["date"]} · {F["commit"]} · <a href="https://github.com/g0rst/ro-MINImal">github.com/g0rst/ro-MINImal</a> · MIT</footer>
</div>
<script>
(function () {{
  var langs = ["de", "en"];
  function pick() {{
    var h = location.hash.replace("#", "").split("-")[0];
    if (langs.indexOf(h) >= 0) return h;
    return (navigator.language || "de").slice(0, 2).toLowerCase() === "de" ? "de" : "en";
  }}
  function show() {{
    var l = pick();
    langs.forEach(function (k) {{ document.getElementById("m-" + k).hidden = k !== l; }});
    document.documentElement.lang = l;
    Array.prototype.forEach.call(document.querySelectorAll(".langs a"), function (a) {{
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
    dest = ROOT / "docs" / "fre3tek.html"
    dest.write_text(out, encoding="utf-8")
    words = {l: len(re.sub(r"<[^>]+>", " ", render(l)).split()) for l in LANGS}
    print(f"{dest}: {len(out)} bytes; words {words}")


if __name__ == "__main__":
    main()
