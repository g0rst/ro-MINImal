#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""p5ydub's manual, apart from the others: German and English, dressed as a sand-coloured tour sheet (earth tones,
an Om, no neon). Tables come from the firmware's code (manual/codefacts.py).

    python3 manual/p5ydub.py      ->  docs/p5ydub.html
"""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from codefacts import facts, pct, pan  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = facts()
ST = F["style"]["psy"]
NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][ST["root"] % 12]
SCALE = F["scales"][ST["scale"]]
TRACKS, SOUND, DEF = F["tracks"]["psy"], F["sound"]["psy"], F["psy_def"]
e = html.escape

ROLE = [
    ("suom1saundis POTKU, rund: vier auf den Boden, vor dem Takt manchmal ein Geist",
     "suom1saundi's POTKU, round: four on the floor, now and then a ghost before the bar"),
    ("der Dub-Bass (BASSO): lange Wurzeltöne auf den Offbeats, ab und zu ein Schritt der Pentatonik (Terz, Quarte, Quinte, "
     "kleine Septime), gleitend; die Kick drückt ihn nur sanft (Duck 90 statt 127): er atmet, er pumpt nicht",
     "the dub bass (BASSO): long root notes on the off-beats, now and then a step of the pentatonic (third, fourth, fifth, "
     "flat seventh), sliding; the kick ducks it only softly (duck 90, not 127): it breathes, it does not pump"),
    ("offener Hat auf dem Offbeat, wenige geschlossene dazwischen; fast alles geht ins Delay",
     "open hat on the off-beat, a few closed ones between; nearly all of it goes into the delay"),
    ("die Blase (HAPPO): eine Pentatonik-Phrase auf eigener Länge (12, 14, 15 oder 16), sparsam, durch das Echo",
     "the bubble (HAPPO): a pentatonic phrase on a loop of its own (12, 14, 15 or 16), sparse, through the echo"),
    ("Moll-Dreiklänge als kurze Stabs auf dem Offbeat; der Rest ist Delay (Send 110) und Hall (84)",
     "minor triads as short stabs on the off-beat; the rest is delay (send 110) and reverb (84)"),
    ("ein Glockenton (Sinus, PIIP) durch das Echo, leise", "a bell tone (sine, PIIP) through the echo, quiet"),
]

THEORY = [
    ("<b>Tempo:</b> um 138 BPM (Dub-Techno liegt bei 145, Dubstep bei 140); einstellbar von 90 bis 160.",
     "<b>Tempo:</b> about 138 BPM (dub techno sits at 145, dubstep at 140); settable from 90 to 160."),
    ("<b>Skala:</b> Moll-Pentatonik für Bass und Blase; die meiste Dub-Musik beruht auf ihr, sagt die "
     "Faustregel in den Foren. Die Grundskala ist phrygisch: die ♭2 gibt die dunkle Spannung, und eine ♭II-Fläche "
     "(i – ♭II – ♭VII – i) ist der Standardzug.",
     "<b>Scale:</b> the minor pentatonic for the bass and the bubble; most dub is built on it, as the forums put it. The "
     "base scale is phrygian: its flat second is the dark tension, and an i – ♭II – ♭VII – i turn is the stock move."),
    ("<b>Akkorde:</b> schlichte Moll-Dreiklänge, kurz, auf dem Offbeat. Die Länge machen Delay und Hall.",
     "<b>Chords:</b> plain minor triads, short, on the off-beat. The length is made by the delay and the reverb."),
    ("<b>Delay:</b> der eigentliche Klang. Punktierte Achtel (3/16), Feedback 78 %, abgedunkelt; zwei bis drei Sends "
     "verschiedener Länge sind der klassische Weg. Hier: HAT, BUBBLE, CHORD und PING schicken stark hinein.",
     "<b>Delay:</b> the sound itself. A dotted eighth (3/16), feedback 78 %, darkened; two or three sends of different "
     "lengths are the classic way. Here HAT, BUBBLE, CHORD and PING send hard into it."),
    ("<b>Hall:</b> groß und gedämpft, als Federhall gedacht (Lee Perrys Perkussion lief durch einen).",
     "<b>Reverb:</b> big and damped, meant as a spring (Lee Perry ran his percussion through one)."),
]

SOURCES = [
    ("KVR: making dub basslines", "https://www.kvraudio.com/forum/viewtopic.php?p=8146770"),
    ("Ableton-Forum: Tips and Tricks, Making Dub with Live", "https://forum.ableton.com/viewtopic.php?p=401548"),
    ("Attack Magazine: Basic Channel style dub techno", "https://www.attackmagazine.com/technique/beat-dissected/basic-channel-style-dub-techno/"),
    ("Production Expert: 6 dub production tips", "https://www.production-expert.com/production-expert-1/6-dub-production-tips"),
]


def table(head, rows):
    h = "".join(f"<th>{e(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


def page(i, lang):
    de = lang == "de"
    t = lambda p: p[i]  # noqa: E731
    out = []
    out.append(f'<section class="lang" id="{lang}" lang="{lang}">')
    out.append("<h1>p<span>5</span>ydub</h1>")
    out.append(f"<p class='sub'>{'psytrance + dub · %d bpm · der fünfte stil in ro:MINImal' % ST['bpm'] if de else 'psytrance + dub · %d bpm · the fifth style inside ro:MINImal' % ST['bpm']}</p>")
    out.append("<p class='om' aria-hidden='true'>ॐ</p>")
    out.append(f"<h2>{'Der Weg hinein' if de else 'The way in'}</h2><ol>")
    out.append("<li>" + ("Nur aus <b>suom1saundi</b>: dort <b>HOME</b> 2 Sekunden halten. (suom1saundi erreichst du aus ro:MINImal mit "
                         "GLO 2 s; FRE3tek mit HOME 2 s bleibt ro:MINImal.)" if de else
                         "Only from <b>suom1saundi</b>: there, hold <b>HOME</b> for 2 seconds. (You reach suom1saundi from ro:MINImal "
                         "with GLO 2 s; FRE3tek, with HOME 2 s, stays ro:MINImal's.)") + "</li>")
    out.append("<li>" + ("Die Röhre zieht sich zusammen, ein Om wird Strich für Strich in Erdtönen auf Sand gezeichnet, die "
                         "Sonne dahinter und Ringe, die im Takt atmen; der Name kommt, sein letztes B hallt nach. Jingle: eine "
                         "angeschlagene Klangschale mit ihrem Dub-Echo (punktierte Achtel) über einem runden Bassschlag." if de else
                         "The tube collapses, an Om is drawn stroke by stroke in earth tones on sand, the sun behind it and rings that "
                         "breathe in time; the name comes, its last B echoing on. Jingle: a struck singing bowl with its dub echo "
                         "(a dotted eighth) over a round bass thud.") + "</li>")
    out.append("<li>" + ("<b>HOME</b> 2 Sekunden: zurück zu suom1saundi. <b>GLO</b> 2 Sekunden: heim zu ro:MINImal. Jeder Druck "
                         "überspringt die Show. Gute Nacht (SAVE halten): „SHANTI“." if de else
                         "<b>HOME</b> 2 seconds: back to suom1saundi. <b>GLO</b> 2 seconds: home to ro:MINImal. Any touch skips the "
                         "show. Good night (SAVE held): “SHANTI”.") + "</li></ol>")
    out.append(f"<h2>{'Die sechs Spuren' if de else 'The six tracks'}</h2>")
    keys = ["1", "2", "3", "4", "5", "6"]
    out.append(table(["taste", "spur", "rolle"] if de else ["key", "track", "role"],
                     [[f"{e(k)} ({'schwarz' if de else 'black'})", f"<b>{e(TRACKS[n])}</b>", t(ROLE[n])] for n, k in enumerate(keys)]))
    out.append(f"<h2>{'Die Regler' if de else 'The knobs'}</h2>")
    rows = []
    for n in range(4):
        rows.append([f"<b>{e(TRACKS[n])}</b>"] + [f"{e(SOUND[n][j])} <i>{DEF[n][j]}</i>" for j in range(4)])
    out.append(table(["", "K1", "K2", "K3", "K4"], rows))
    out.append("<p class='small'>" + ("Werkseinstellung kursiv. Spur 5 und 6 starten als CHORD (Engine STAB) und PING (Engine PIIP); "
                                      "die Engines lassen sich auf GROOVE 2 (HOME zweimal) wechseln: " if de else
                                      "Factory values in italics. Tracks 5 and 6 start as CHORD (engine STAB) and PING (engine PIIP); the "
                                      "engines can be changed on GROOVE 2 (HOME twice): ") + e(", ".join(F["engines"]["psy"])) + ".</p>")
    out.append(f"<h2>{'Mischung und Start' if de else 'Mix and start'}</h2>")
    out.append(table([x for x in (["spur", "pegel", "pan", "delay", "hall"] if de else ["track", "level", "pan", "delay", "reverb"])],
                     [[f"<b>{e(TRACKS[n])}</b>", pct(DEF[n][4]), pan(DEF[n][5]), pct(DEF[n][6]), pct(DEF[n][7])] for n in range(4)]))
    out.append("<p>" + (f"Start: {ST['bpm']} BPM, Swing {ST['swing']} %, Drift {ST['drift']} %, Duck {ST['duck']} %, Grundton {NOTE}, "
                        f"Skala {SCALE}, Delay-Feedback {pct(ST['dly_fb'])}, Hall {pct(ST['rev_size'])} (Dämpfung {pct(ST['rev_damp'])}), "
                        f"Delay 3/16." if de else
                        f"Start: {ST['bpm']} BPM, swing {ST['swing']} %, drift {ST['drift']} %, duck {ST['duck']} %, root {NOTE}, "
                        f"scale {SCALE}, delay feedback {pct(ST['dly_fb'])}, reverb {pct(ST['rev_size'])} (damping {pct(ST['rev_damp'])}), "
                        f"delay 3/16.") + "</p>")
    out.append(f"<h2>{'Warum es so klingt' if de else 'Why it sounds like this'}</h2><ul>")
    out += [f"<li>{t(x)}</li>" for x in THEORY]
    out.append("</ul>")
    out.append(f"<h2>{'Bildschirmschoner' if de else 'Screensaver'}</h2><p>" +
               ("Nach 2 Minuten ohne Berührung: wie in allen Stilen pumpt der Name mit der Kick, und mit 30 % Chance pumpt "
                "stattdessen das Maskottchen des Stils: hier das Om, bei schr4nz die Gasmaske, bei FRE3tek ein Lautsprecher, bei "
                "suom1saundi das UFO, bei ro:MINImal ein Konus." if de else
                "After 2 minutes untouched: as in every style the name pumps with the kick, and with a 30 % chance the style's mascot "
                "pumps instead: here the Om, in schr4nz the gas mask, in FRE3tek a speaker, in suom1saundi the UFO, in ro:MINImal "
                "a cone.") + "</p>")
    out.append(f"<h2>{'Quellen' if de else 'Sources'}</h2><ul>")
    out += [f"<li><a href='{u}'>{e(n)}</a></li>" for n, u in SOURCES]
    out.append("</ul>")
    out.append(f"<p class='small'>{'Gebaut aus dem Code' if de else 'Built from the code'}: {e(F['commit'])} {e(F['date'])}. "
               f"<a href='index.html'>ro:MINImal</a> · <a href='#{'en' if de else 'de'}'>{'english' if de else 'deutsch'}</a></p>")
    out.append("</section>")
    return "\n".join(out)


CSS = """
:root{--sand:#e9ddc3;--ink:#4a3426;--terra:#b5593c;--ochre:#c98f2b;--olive:#6b6b3a;--line:#d4c6a8}
*{box-sizing:border-box}body{margin:0;background:var(--sand);color:var(--ink);font:17px/1.6 Georgia,'Noto Serif',serif}
section.lang{display:none;max-width:720px;margin:0 auto;padding:40px 20px 80px}
section.lang:target,body:not(:has(:target)) #de{display:block}
h1{font:700 clamp(46px,14vw,84px)/1 Georgia,serif;letter-spacing:-.02em;margin:0}h1 span{color:var(--terra)}
.sub{color:var(--olive);letter-spacing:.06em;margin:6px 0 0;text-transform:lowercase}
.om{font-size:120px;line-height:1;margin:18px 0 0;color:var(--ochre);text-shadow:0 0 0 var(--ink)}
h2{margin:34px 0 8px;font-size:22px;border-bottom:2px solid var(--line);padding-bottom:4px}
table{width:100%;border-collapse:collapse;font-size:15px;margin:8px 0}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--olive);font-weight:400;text-transform:lowercase}i{color:var(--terra);font-style:normal;font-weight:700}
a{color:var(--terra)}.small{font-size:14px;color:var(--olive)}
"""

doc = ("<!DOCTYPE html>\n<html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
       f"<title>p5ydub</title><style>{CSS}</style></head><body>\n" + page(0, "de") + "\n" + page(1, "en") + "\n</body></html>\n")
(ROOT / "docs" / "p5ydub.html").write_text(doc, encoding="utf-8")
print(f"docs/p5ydub.html: {len(doc)} bytes")
