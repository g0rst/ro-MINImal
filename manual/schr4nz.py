#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""schr4nz's manual, apart from the others: German and English, dressed as an industrial safety sheet (steel grey,
warning yellow and black, stencil type, a gas mask). Tables come from the firmware's code (manual/codefacts.py).

    python3 manual/schr4nz.py      ->  docs/schr4nz.html
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
ST = F["style"]["sch"]
NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][ST["root"] % 12]


def L(de, en):
    return {"de": de, "en": en}


UI = {
    "sub": L(f"schranz · hard techno · {ST['bpm']} bpm · der vierte stil in ro:MINImal",
             f"schranz · hard techno · {ST['bpm']} bpm · the fourth style inside ro:MINImal"),
    "toc": L("inhalt", "contents"),
    "emu": L("▶ im fm-1-emulator: ro:MINImal laden, HOME 2 s halten, dann GLO 2 s halten",
             "▶ in the fm-1 emulator: load ro:MINImal, hold HOME 2 s, then hold GLO 2 s"),
    "greet": L("Für alle, die um sechs Uhr morgens noch stehen. <b>Schranz bis zum Schluss.</b>",
               "For everyone still standing at six in the morning. <b>Schranz till the end.</b>"),
    "th_track": L(["taste", "spur", "rolle"], ["key", "track", "role"]),
    "th_knob": L(["regler", "name", "werk"], ["knob", "name", "factory"]),
    "th_mix": L(["spur", "pegel", "pan", "delay", "hall", "duck"], ["track", "level", "pan", "delay", "reverb", "duck"]),
    "black": L("schwarz", "black"),
}

ROLE = [
    L("memeteks TEK-KICK, kurz und hart verzerrt: vier auf den Boden, manchmal ein Doppel in den Takt",
      "memetek's TEK-KICK, short and driven hard: four on the floor, now and then a double into the bar"),
    L("das Rumpeln: die Kick ohne Attack durch einen Hall, auf den Sechzehnteln danach, gefiltert, gesättigt, von der Kick gepumpt",
      "the rumble: the kick without its attack through a reverb, on the sixteenths after it, filtered, saturated, pumped by the kick"),
    L("das Maschinengewehr: geschlossen auf jeder Sechzehntel neben der Kick, offen auf dem Offbeat",
      "the machine gun: closed on every sixteenth beside the kick, open on the off-beat"),
    L("der Schranz-Loop: FM-Percussion auf unharmonischem Verhältnis, 3-3-2 gegen die Vier",
      "the schranz loop: FM percussion at an inharmonic ratio, 3-3-2 against the four"),
    L("Rauschen als Clap auf 2 und 4, leicht verzerrt", "noise as a clap on 2 and 4, a little driven"),
    L("der Alarm: ein Rechteck mit Sirenen-Vibrato, kommt stumm", "the alarm: a square with a siren's vibrato, comes muted"),
]

S = []


def sec(de, en, *blocks):
    S.append((L(de, en), blocks))


sec("Was das ist", "What it is",
    ("p", L("<b>schr4nz</b> ist der vierte Stil in ro:MINImal: Schranz, harter Techno aus Deutschland um 2000, der gerade "
            "zurückkommt. Das Wort hat Chris Liebing geprägt. Dieselbe Maschine, dasselbe Panel, andere Stimmen, andere "
            f"Regeln. Er startet mit {ST['bpm']} BPM, gerade wie eine Presse, in {NOTE}-Moll.",
            "<b>schr4nz</b> is the fourth style in ro:MINImal: Schranz, the hard German techno of around 2000 that is "
            "coming back right now. Chris Liebing coined the word. The same machine, the same panel, other voices, other "
            f"rules. It starts at {ST['bpm']} BPM, straight as a press, in {NOTE} minor.")),
    ("tape", L("Ein Versuch, kein Produkt. Wird die Rechenzeit des FM-1 knapp, fliegt er zusammen mit FRE3tek raus.",
               "An experiment, not a product. Should the FM-1 run short of time, it goes along with FRE3tek.")))

sec("Musiktheorie, kurz", "Theory, briefly",
    ("ul", [L("<b>Tempo</b>: Schranz lief um 150 BPM, heute oft schneller. Gerade, kein Swing: die Lokomotive.",
              "<b>Tempo</b>: schranz ran at about 150 BPM, often faster today. Straight, no swing: the locomotive."),
            L("<b>Wenig Melodie</b>: höchstens ein einzelner Stab oder ein Sweep, alles andere ist Percussion. Deshalb steht "
              "alles auf einem Ton, dem Grundton der Kick; der Alarm hält sich an dessen Akkord.",
              "<b>Little melody</b>: a single stab or a sweep at most, the rest is percussion. So all of it sits on one note, "
              "the kick's root; the alarm keeps to its chord."),
            L("<b>Loops</b>: stark komprimiert, gefiltert, verzerrt. Hier: die Summe durch memeteks Master, der Drive härter "
              "(×5) und der Crusher feiner (12 Bit, halbe Rate) als in FRE3tek: es mahlt, es zischt nicht.",
              "<b>Loops</b>: heavily compressed, filtered, distorted. Here: the sum through memetek's master, the drive harder "
              "(×5) and the crusher finer (12 bits, half the rate) than FRE3tek's: it grinds, it does not fizz."),
            L("<b>Das Rumpeln</b>, wie Produzenten es bauen: die Kick kopieren, den Attack weg, durch einen Hall 100 % "
              "nass, auf Sechzehntel legen, Tief- und Hochpass, Sättigung, Sidechain von der Kick. Darüber eine zweite "
              "Schicht mit Bandpass und Verzerrung für die Mitten. Genau so macht es RUMBLE, in Echtzeit statt gerendert.",
              "<b>The rumble</b>, as producers build it: copy the kick, take off its attack, through a reverb 100 % wet, "
              "onto the sixteenths, low- and high-pass, saturation, sidechain from the kick. Over it a second layer, "
              "band-passed and distorted, for the mids. RUMBLE does just that, live instead of rendered."),
            L("<b>3-3-2</b>: der Loop setzt Gruppen von drei Sechzehnteln gegen die Vier. Das reibt, und es treibt.",
              "<b>3-3-2</b>: the loop sets groups of three sixteenths against the four. It grinds, and it drives.")]))

sec("Rein und raus", "In and out",
    ("ol", [L("Nur aus <b>FRE3tek</b>: dort <b>GLO</b> 2 Sekunden halten. (Nach FRE3tek kommt man aus ro:MINImal mit HOME "
              "2 s; suom1saundi erreicht man nur aus ro:MINImal.)",
              "Only from <b>FRE3tek</b>: there, hold <b>GLO</b> for 2 seconds. (FRE3tek is HOME 2 s from ro:MINImal; "
              "suom1saundi is reached only from ro:MINImal.)"),
            L("Die Röhre zieht sich zusammen, die Musik schmatzt weg. Warnstreifen fahren ein, eine Gasmaske taucht aus dem "
              "Dunkel auf und atmet im Takt: die Gläser blitzen gelb, der Filter pufft. Dann presst sich der Name herunter, "
              "die 4 in Gelb.",
              "The tube collapses, the music smacks out. Warning stripes slide in, a gas mask comes up out of the dark and "
              "breathes in time: the lenses flash yellow, the filter puffs. Then the name presses down, its 4 yellow."),
            L("Neuer Groove in schr4nz. Die Musik startet mit dem Überblenden.", "A new groove in schr4nz. The music starts with the fade."),
            L("<b>GLO</b> 2 Sekunden halten: zurück zu FRE3tek. <b>HOME</b> 2 Sekunden: heim zu ro:MINImal. Jeder Druck "
              "überspringt die Show.",
              "Hold <b>GLO</b> 2 seconds: back to FRE3tek. Hold <b>HOME</b> 2 seconds: home to ro:MINImal. Any touch skips "
              "the show.")]))

sec("Warnung", "Warning",
    ("ul", [L("Lief bisher nur im Simulator und Emulator, <b>nicht auf einem echten FM-1</b>.", "Has run in the simulator and emulator only, <b>not on a real FM-1</b>."),
            L("Custom-Firmware kann ein Gerät unbrauchbar machen. Kenne den Weg zurück zur M-VAVE-Firmware.",
              "Custom firmware can brick a device. Know the way back to M-VAVE's firmware."),
            L("Gehörschutz. Wirklich.", "Ear plugs. Really.")]))

sec("Die sechs Spuren", "The six tracks", ("gen", "tracks"))

sec("Klänge ab Werk", "Factory sounds",
    ("p", L("Aus dem Code gelesen. <b>EDIT</b> öffnet SOUND, nochmal <b>EDIT</b> SOUND 2. Kick und Hats sind memeteks Stimmen, "
            "die Kick kürzer und härter gefahren als in FRE3tek. RUMBLE: TONE ist der Tiefpass (40 bis 450 Hz), SMEAR die "
            "Länge des Halls (0,2 bis 2 s), GRIT die verzerrte zweite Schicht in den Mitten, DECAY die Länge der Kick-Kopie; "
            "ATTACK auf SOUND 2 blendet sie ein (ohne Attack). METAL ist die FM-Percussion von ro:MINImal auf dem Verhältnis 4,07: kein Ton, Blech.",
            "Read from the code. <b>EDIT</b> opens SOUND, <b>EDIT</b> again SOUND 2. Kick and hats are memetek's voices, the "
            "kick shorter and harder than in FRE3tek. RUMBLE: TONE is the low-pass (40 to 450 Hz), SMEAR the "
            "reverb's length (0.2 to 2 s), GRIT the distorted second layer in the mids, DECAY the kick copy's length; ATTACK "
            "on SOUND 2 fades it in (no attack). METAL is ro:MINImal's FM "
            "percussion at ratio 4.07: no note, sheet metal.")),
    ("gen", "knobs"), ("gen", "mix"),
    ("p", L("CLAP ist die Engine NOISE ganz links (CLAP), ALARM die Engine 8-BIT als Rechteck mit viel VIBRATO. Auf GROOVE 2 "
            "lassen sich beide tauschen.",
            "CLAP is the NOISE engine all the way left (CLAP), ALARM the 8-BIT engine as a square with a lot of VIBRATO. On "
            "GROOVE 2 both can be swapped.")))

sec("Die Regeln", "The rules",
    ("ul", [L("<b>KICK</b>: jede Viertel, auf die Tonart gestimmt; jedes vierte Mal ein Doppel auf der letzten Sechzehntel.",
              "<b>KICK</b>: every quarter, tuned to the key; one time in four a double on the last sixteenth."),
            L("<b>RUMBLE</b>: pro Viertel dieselbe Figur, beim Laden die drei Sechzehntel nach der Kick, sonst eine von vier "
              "(zwei, Offbeat und letzte, nur der Offbeat); der Offbeat betont.",
              "<b>RUMBLE</b>: the same figure each quarter, on loading the three sixteenths after the kick, else one of four "
              "(two, off-beat and last, the off-beat alone); the off-beat accented."),
            L("<b>HAT</b>: geschlossen auf den Sechzehnteln neben der Kick, offen und betont auf dem Offbeat; in B ab und zu "
              "ein Geist auf der Kick.",
              "<b>HAT</b>: closed on the sixteenths beside the kick, open and accented on the off-beat; in B now and then a "
              "ghost on the kick."),
            L("<b>METAL</b>: einer von vier Loops (3-3-3-3-2-2, dagegen, dicht verknotet, 3-3-2 vom Offbeat), Grundton, "
              "Grundton, Quinte.",
              "<b>METAL</b>: one of four loops (3-3-3-3-2-2, against it, densely knotted, 3-3-2 off the beat), root, root, fifth."),
            L("<b>CLAP</b> auf 2 und 4, <b>ALARM</b> eine Melodie auf den Tönen des Akkords, stumm bis du sie holst.",
              "<b>CLAP</b> on 2 and 4, <b>ALARM</b> a melody on the chord's tones, muted until you bring it.")]))

sec("Live spielen", "Playing live",
    ("ul", [L("<b>Mixer</b>: ENV 0,6 s halten. Schwarze Taste 1 bis 6 haut eine Spur rein oder raus, gehalten nur solange. "
              "Der Klassiker: Taste 1 halten – die Kick weg, das Rumpeln steht allein im Raum, loslassen – Einschlag.",
              "<b>Mixer</b>: hold ENV 0.6 s. Black key 1 to 6 slams a track in or out, held only while held. The classic: "
              "hold key 1 – the kick gone, the rumble alone in the room, let go – impact."),
            L("<b>Gruppe</b>: im Mixer weiße Tasten 3, 4, 5 (HAT, METAL, CLAP) auf die Gruppe, schwarze Taste 7 nimmt alle "
              "Tops auf einmal raus.",
              "<b>Group</b>: in the mixer, white keys 3, 4, 5 (HAT, METAL, CLAP) onto the group, black key 7 takes all the "
              "tops out at once."),
            L("<b>Filterfahrt</b>: GROOVE 2 FILTER nach links, vier Takte halten, zurück zur Mitte.",
              "<b>Filter ride</b>: GROOVE 2 FILTER to the left, hold four bars, back to the middle."),
            L("<b>Alarm</b>: ALARM reinholen, DRIVE hoch, ein LFO auf VIBRATO.", "<b>Alarm</b>: bring ALARM in, DRIVE up, an LFO on VIBRATO."),
            L("<b>Rumpeln auf</b>: RUMBLE TONE hoch und SMEAR hoch, langsam, über acht Takte.",
              "<b>Rumble up</b>: RUMBLE TONE up and SMEAR up, slowly, over eight bars.")]))

sec("Rezepte", "Recipes",
    ("ul", [L("<b>Stahlwerk</b>: KICK DRIVE 127, DECAY 50, METAL FM 110.", "<b>Steelworks</b>: KICK DRIVE 127, DECAY 50, METAL FM 110."),
            L("<b>Bunker</b>: RUMBLE TONE 60, SMEAR 110, GRIT 30, DUCK 100.", "<b>Bunker</b>: RUMBLE TONE 60, SMEAR 110, GRIT 30, DUCK 100."),
            L("<b>2003</b>: TEMPO 155, HAT DECAY 30, CLAP DRIVE 90.", "<b>2003</b>: TEMPO 155, HAT DECAY 30, CLAP DRIVE 90."),
            L("<b>Neues Hart</b>: TEMPO 160, RUMBLE DECAY 70, ALARM rein.", "<b>New hard</b>: TEMPO 160, RUMBLE DECAY 70, ALARM in.")]))

sec("Gute Nacht", "Good night",
    ("p", L("<b>SAVE</b> 2 Sekunden halten: speichert, die Röhre geht aus, und in Gelb steht „GUTE NACHT“ – Schranz kommt aus "
            "Deutschland, also auf Deutsch. Dann dunkel und still.",
            "Hold <b>SAVE</b> for 2 seconds: it saves, the tube goes out, and in yellow it says “GUTE NACHT” – schranz comes "
            "from Germany, so in German. Then dark and silent.")))

sec("Kleingedrucktes", "Small print",
    ("ul", [L("Im Simulator gezählt: im schlimmsten Fall knapp so viel Rechenzeit wie FRE3tek, grob 40–80 % des FM-1, mit "
              "GRAIN auf zwei Spuren bis an die Grenze. Am Gerät nicht gemessen.",
              "Counted in the simulator: at worst about as much as FRE3tek, roughly 40–80 % of the FM-1, with GRAIN on two "
              "tracks up to the limit. Not measured on the device."),
            L("Ohne suom1saundi gebaut (ROMI_SUOMI=0) gibt es schr4nz nicht.", "Built without suom1saundi (ROMI_SUOMI=0) there is no schr4nz."),
            L("Kick und Hats nach memetek, mit Erlaubnis des Autors. Gebaut auf fm1-base und felucca-bsp. MIT-Lizenz. Nicht "
              "mit M-VAVE verbunden.",
              "Kick and hats after memetek, by its author's leave. Built on fm1-base and felucca-bsp. MIT licence. Not "
              "affiliated with M-VAVE.")]))


def table(head, rows):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def gen(name, lang):
    trk = F["tracks"]["sch"]
    if name == "tracks":
        return table(UI["th_track"][lang], [(f"{UI['black'][lang]} {t + 1}", f"<b>{trk[t]}</b>", ROLE[t][lang]) for t in range(6)])
    if name == "knobs":
        out = []
        for t in range(4):
            d = F["sch_def"][t]
            q = [24, d[8], 70 if t == 0 else 30 if t == 3 else 0, 0]
            rows = [(f"EDIT K{k + 1}", f"<b>{n}</b>", str(v)) for k, (n, v) in enumerate(zip(F["sound"]["sch"][t], d[:4]))]
            rows += [(f"EDIT² K{k + 1}", f"<b>{n}</b>", str(v - 24 if n == "PITCH" else v))
                     for k, (n, v) in enumerate(zip(F["sound2"]["sch"][t], q))]
            out.append(f"<h3>{trk[t]}</h3>" + table(UI["th_knob"][lang], rows))
        return "".join(out)
    if name == "mix":
        rows = [(f"<b>{trk[t]}</b>", pct(F["sch_def"][t][4]), pan(F["sch_def"][t][5]), pct(F["sch_def"][t][6]),
                 pct(F["sch_def"][t][7]), pct(F["sch_sc"][t])) for t in range(4)]
        return "<h3>mix</h3>" + table(UI["th_mix"][lang], rows)
    raise KeyError(name)


CSS = """
:root{--steel:#2b2f33;--plate:#3a3f44;--ink:#e8e6df;--yel:#ffcc00;--blk:#0d0e0f;--soft:#9aa0a6}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:16px/1.6 "IBM Plex Mono",ui-monospace,monospace;background:var(--steel);
 background-image:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 3px),
  radial-gradient(circle at 12px 12px,rgba(0,0,0,.35) 0 3px,transparent 4px);
 background-size:auto,48px 48px}
.wrap{max-width:860px;margin:0 auto;padding:0 16px 80px}
.haz{height:22px;background:repeating-linear-gradient(-45deg,var(--yel) 0 16px,var(--blk) 16px 32px)}
.top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;padding:10px 0;color:var(--soft)}
.langs a{color:var(--ink);text-decoration:none;border:2px solid var(--yel);padding:3px 10px;margin-left:6px}
.langs a[aria-current="true"]{background:var(--yel);color:var(--blk)}
header.sheet{position:relative;margin:18px 0 10px;padding:26px 20px 24px;background:var(--plate);border:3px solid var(--blk);
 box-shadow:inset 0 0 0 6px var(--plate),inset 0 0 0 9px var(--yel)}
header.sheet .rv{position:absolute;width:10px;height:10px;border-radius:50%;background:#777;box-shadow:inset -2px -2px 0 #444}
.mask{float:right;width:120px;height:140px;margin:0 0 6px 16px}
.mask .lens{animation:flash .4s steps(1) infinite}
@keyframes flash{0%{fill:#ffcc00}25%{fill:#3a3410}}
h1{margin:0;font:400 clamp(56px,15vw,128px)/.9 "Saira Stencil One","Black Ops One",Impact,sans-serif;letter-spacing:.02em}
h1 .y{color:var(--yel)}
.sub{margin:12px 0 0;font-size:14px;text-transform:uppercase;letter-spacing:.12em;color:var(--soft)}
.emu{display:inline-block;margin-top:18px;color:var(--blk);background:var(--yel);padding:7px 12px;text-decoration:none;font-weight:600}
.toc{margin:26px 0;padding:12px 16px;border-left:8px solid var(--yel);background:rgba(0,0,0,.2);columns:2 220px}
.toc b{display:block;font-family:"Saira Stencil One",Impact,sans-serif;font-weight:400;text-transform:uppercase;color:var(--yel)}
.toc a{display:block;color:var(--ink)}
section{margin:44px 0 0}
h2{margin:0 0 12px;padding:6px 12px 4px;background:var(--blk);color:var(--ink);border-left:12px solid var(--yel);
 font:400 26px/1.15 "Saira Stencil One",Impact,sans-serif;text-transform:uppercase}
h2 .n{color:var(--yel);margin-right:12px}
h3{font:400 19px "Saira Stencil One",Impact,sans-serif;margin:24px 0 6px;text-transform:uppercase;color:var(--yel)}
p,li{max-width:72ch}
b{color:#fff}
.tape{display:block;margin:20px 0;padding:14px 16px;background:var(--yel);color:var(--blk);font-weight:600;max-width:62ch;
 border:3px solid var(--blk);box-shadow:6px 6px 0 var(--blk)}
.tape b{color:var(--blk)}
.tw{overflow-x:auto;margin:8px 0 16px}
table{border-collapse:collapse;min-width:100%;background:rgba(0,0,0,.25)}
th{background:var(--yel);color:var(--blk);text-align:left;padding:6px 10px;font-weight:600;text-transform:uppercase;font-size:13px}
td{border:1px solid #555b61;padding:5px 10px;vertical-align:top}
.greet{margin:56px 0 0;padding:18px;text-align:center;font-size:17px;border:3px solid var(--yel);
 background:repeating-linear-gradient(-45deg,rgba(255,204,0,.08) 0 16px,transparent 16px 32px)}
.greet b{display:block;margin-top:6px;color:var(--yel);font-family:"Saira Stencil One",Impact,sans-serif;font-weight:400;font-size:28px}
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
<header class="sheet">
  <svg class="mask" viewBox="0 0 120 140" aria-hidden="true"><rect x="0" y="34" width="120" height="8" fill="#1b1d1f"/><ellipse cx="60" cy="66" rx="48" ry="62" fill="#55595e"/><ellipse cx="60" cy="68" rx="43" ry="57" fill="#3d4146"/><circle cx="39" cy="54" r="17" fill="#8a8f94"/><circle cx="81" cy="54" r="17" fill="#8a8f94"/><circle class="lens" cx="39" cy="54" r="13" fill="#3a3410"/><circle class="lens" cx="81" cy="54" r="13" fill="#3a3410"/><rect x="31" y="45" width="5" height="3" fill="#ddd"/><rect x="73" y="45" width="5" height="3" fill="#ddd"/><rect x="48" y="74" width="24" height="16" fill="#6b7075"/><circle cx="20" cy="98" r="8" fill="#6b7075"/><circle cx="100" cy="98" r="8" fill="#6b7075"/><circle cx="60" cy="106" r="19" fill="#a3a8ad"/><circle cx="60" cy="106" r="15" fill="#7b8085"/><g fill="#24272a"><rect x="48" y="96" width="24" height="2"/><rect x="48" y="101" width="24" height="2"/><rect x="48" y="106" width="24" height="2"/><rect x="48" y="111" width="24" height="2"/><rect x="48" y="116" width="24" height="2"/></g></svg>
  <h1>SCHR<span class="y">4</span>NZ</h1>
  <p class="sub">{UI["sub"][l]}</p>
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
<title>schr4nz – Handbuch · Manual</title>
<!-- written by manual/schr4nz.py from the firmware's code: do not edit by hand -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Stencil+One&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="haz"></div>
<div class="wrap">
<div class="top"><span>ro:MINImal · schr4nz · {F["date"]} · build {F["commit"]}</span>
<nav class="langs"><a href="#de" data-l="de">deutsch</a><a href="#en" data-l="en">english</a></nav></div>
{"".join(arts)}
<footer>{F["date"]} · {F["commit"]} · <a href="https://github.com/g0rst/ro-MINImal">github.com/g0rst/ro-MINImal</a> · MIT</footer>
</div>
<div class="haz"></div>
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
    dest = ROOT / "docs" / "schr4nz.html"
    dest.write_text(out, encoding="utf-8")
    words = {l: len(re.sub(r"<[^>]+>", " ", render(l)).split()) for l in LANGS}
    print(f"{dest}: {len(out)} bytes; words {words}")


if __name__ == "__main__":
    main()
