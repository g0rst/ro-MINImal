#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Builds the ro:MINImal manual: one self-contained page in English, German and Romanian. (It does not speak of
suom1saundi: that has a manual of its own, apart, manual/suomi.py.) The tables of factory values come from the firmware's code
(manual/codefacts.py), so they cannot drift from it.

    python3 manual/build.py        ->  docs/manual.html

The text lives here, once per language, block by block, so the three versions cannot drift apart in structure.
[[NAME]] marks a control as printed on the FM-1. The screens are the firmware's own (tests/run_tests.sh writes
them; manual/screen-*.png are copies).
"""
import base64
import html
import pathlib
import re

from codefacts import facts, pct, pan

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("en", "de", "ro")
F = facts()


def T(en, de, ro):
    return {"en": en, "de": de, "ro": ro}


SAME = lambda s: {l: s for l in LANGS}  # noqa: E731

TITLE = T("manual", "handbuch", "manual")
SUB = T("firmware for the m-vave fm-1 · rominimal and microhouse",
        "firmware für den m-vave fm-1 · rominimal und microhouse",
        "firmware pentru m-vave fm-1 · rominimal și microhouse")
EMU = T("try it in the fm-1 emulator, no device needed", "im fm-1-emulator testen, ohne gerät",
        "încearcă în emulatorul fm-1, fără aparat")
SIDES = {
    "a": T("start", "anfang", "început"),
    "b": T("steps and sound", "steps und klang", "pași și sunet"),
    "c": T("pattern logic", "pattern-logik", "logica pattern-ului"),
    "d": T("patterns, keys, recipes", "patterns, tasten, rezepte", "pattern-uri, clape, rețete"),
}

# Each block: (kind, ...). Kinds: h (side, number, title), p, ol, ul, table (head, rows), grid (rows, caption),
# img (name, caption), note.
B = []
h = lambda side, n, t: B.append(("h", side, n, t))  # noqa: E731
p = lambda t: B.append(("p", t))  # noqa: E731
ol = lambda *items: B.append(("ol", items))  # noqa: E731
ul = lambda *items: B.append(("ul", items))  # noqa: E731
table = lambda head, *rows: B.append(("table", head, rows))  # noqa: E731
grid = lambda rows, cap: B.append(("grid", rows, cap))  # noqa: E731
img = lambda name, cap: B.append(("img", name, cap))  # noqa: E731
note = lambda t: B.append(("note", t))  # noqa: E731
pre = lambda t: B.append(("pre", t))  # noqa: E731

# ------------------------------------------------------------------ side a ---
h("a", 1, T("what it is", "was es ist", "ce este"))
p(T("ro:MINImal is a firmware for the M-VAVE FM-1. It turns the keyboard into a six-track groove machine for "
    "rominimal and microhouse: few elements, long loops, small movements. Every track has its own loop length, "
    "every step its own chance. The bar does not repeat exactly.",
    "ro:MINImal ist eine Firmware für den M-VAVE FM-1. Sie macht aus dem Keyboard eine Groove-Maschine mit sechs "
    "Spuren für Rominimal und Microhouse: wenige Elemente, lange Loops, kleine Bewegungen. Jede Spur hat ihre "
    "eigene Looplänge, jeder Step seine eigene Chance. Der Takt wiederholt sich nicht genau.",
    "ro:MINImal este un firmware pentru M-VAVE FM-1. Transformă claviatura într-o mașină de groove cu șase piste "
    "pentru rominimal și microhouse: puține elemente, bucle lungi, mișcări mici. Fiecare pistă are lungimea ei "
    "de buclă, fiecare pas are șansa lui. Măsura nu se repetă exact."))

h("a", 2, T("before you flash", "vor dem flashen", "înainte de instalare"))
note(T("This firmware has run in the simulator only. It has not yet been built for or run on a real FM-1. "
       "Custom firmware can make an FM-1 unusable: the chip holds one firmware and has no recovery button, and "
       "newer units do not accept every custom firmware. Know the way back to M-VAVE's own firmware before you "
       "install anything.",
       "Diese Firmware lief bisher nur im Simulator. Sie wurde noch nicht für einen echten FM-1 gebaut oder "
       "darauf gestartet. Custom-Firmware kann einen FM-1 unbrauchbar machen: Der Chip hält genau eine Firmware "
       "und hat keinen Recovery-Taster, und neuere Geräte nehmen nicht jede Custom-Firmware an. Kenne den Weg "
       "zurück zur Firmware von M-VAVE, bevor du etwas installierst.",
       "Acest firmware a rulat doar în simulator. Nu a fost încă compilat pentru un FM-1 real și nu a rulat pe "
       "unul. Un firmware custom poate face un FM-1 inutilizabil: cipul ține un singur firmware și nu are buton "
       "de recuperare, iar aparatele mai noi nu acceptă orice firmware custom. Află cum te întorci la firmware-ul "
       "M-VAVE înainte să instalezi ceva."))

h("a", 3, T("install", "installieren", "instalare"))
p(T("Without a device: the page of the project (g0rst.github.io/ro-MINImal) opens the firmware in the FM-1 emulator, "
    "in the browser, with the same code as on the device. On a phone it runs well, on an old computer it may stutter. "
    "Sound on first, then [[PLAY STOP]].",
    "Ohne Gerät: Die Projektseite (g0rst.github.io/ro-MINImal) öffnet die Firmware im FM-1-Emulator, im Browser, mit "
    "demselben Code wie auf dem Gerät. Auf einem Handy läuft sie gut, auf einem alten Computer kann sie stocken. Erst "
    "den Ton einschalten, dann [[PLAY STOP]].",
    "Fără aparat: pagina proiectului (g0rst.github.io/ro-MINImal) deschide firmware-ul în emulatorul FM-1, în browser, "
    "cu același cod ca pe aparat. Pe un telefon merge bine, pe un calculator vechi poate sacada. Întâi pornește "
    "sunetul, apoi [[PLAY STOP]]."))
ol(T("Download rominimal.fwsc from the page of the project. It is built from the code on every change; SHA256SUMS "
     "beside it lets you check the file.",
     "rominimal.fwsc von der Projektseite laden. Es wird bei jeder Änderung aus dem Code gebaut; mit SHA256SUMS daneben "
     "lässt sich die Datei prüfen.",
     "Descarcă rominimal.fwsc de pe pagina proiectului. Se construiește din cod la fiecare schimbare; SHA256SUMS de "
     "lângă el verifică fișierul."),
   T("Install it with a tool that installs FM-1 firmware packages, such as the FM-1 Firmware Hub "
     "(fm1.designburgapps.com). The firmware describes itself to such tools (firmware.json beside it).",
     "Mit einem Werkzeug installieren, das FM-1-Firmware-Pakete installiert, etwa dem FM-1 Firmware Hub "
     "(fm1.designburgapps.com). Die Firmware beschreibt sich solchen Werkzeugen selbst (firmware.json daneben).",
     "Instalează-l cu un instrument care instalează pachete de firmware FM-1, de exemplu FM-1 Firmware Hub "
     "(fm1.designburgapps.com). Firmware-ul se descrie singur acestor instrumente (firmware.json alături)."),
   T("Switch on. The name flies in, the screen fades to the steps, a groove waits for [[PLAY STOP]].",
     "Einschalten. Der Name fliegt herein, das Bild blendet zu den Steps über, ein Groove wartet auf [[PLAY STOP]].",
     "Pornește. Numele intră în zbor, imaginea trece la pași, un groove așteaptă [[PLAY STOP]]."))
note(T("The way back: M-VAVE's own firmware, through the FM-1 Firmware Hub or M-VAVE's updater. Your projects live in "
       "a part of the flash of their own and are not part of the firmware.",
       "Der Weg zurück: die Firmware von M-VAVE, über den FM-1 Firmware Hub oder den Updater von M-VAVE. Deine Projekte "
       "liegen in einem eigenen Teil des Flash und gehören nicht zur Firmware.",
       "Drumul înapoi: firmware-ul M-VAVE, prin FM-1 Firmware Hub sau updater-ul M-VAVE. Proiectele tale stau într-o "
       "parte separată a flash-ului și nu fac parte din firmware."))

h("a", 4, T("the first minute", "die erste minute", "primul minut"))
ol(T("Press [[PLAY STOP]]. A groove runs. The firmware makes a new one at every start.",
     "[[PLAY STOP]] drücken. Ein Groove läuft. Die Firmware erzeugt bei jedem Start einen neuen.",
     "Apasă [[PLAY STOP]]. Pornește un groove. Firmware-ul face unul nou la fiecare pornire."),
   T("Press one of the six black keys on the left: KICK, SUB, HAT, PERC, STAB, CLICK. That track is selected.",
     "Eine der sechs schwarzen Tasten links drücken: KICK, SUB, HAT, PERC, STAB, CLICK. Diese Spur ist gewählt.",
     "Apasă una dintre cele șase clape negre din stânga: KICK, SUB, HAT, PERC, STAB, CLICK. Pista este selectată."),
   T("Tap white keys. The 16 white keys are the 16 steps of that track.",
     "Weiße Tasten tippen. Die 16 weißen Tasten sind die 16 Steps dieser Spur.",
     "Atinge clapele albe. Cele 16 clape albe sunt cei 16 pași ai pistei."),
   T("Press NEW (the fourth black key from the right) for a new pattern on this track. Press [[ARP]] for one small "
     "change.",
     "NEW drücken (die vierte schwarze Taste von rechts) für ein neues Pattern auf dieser Spur. [[ARP]] drücken für "
     "eine kleine Änderung.",
     "Apasă NEW (a patra clapă neagră de la dreapta) pentru un pattern nou pe această pistă. Apasă [[ARP]] pentru o "
     "singură schimbare mică."),
   T("Press [[HOME]] and turn [[KNOB1]] for tempo, [[KNOB2]] for swing, [[KNOB3]] for drift.",
     "[[HOME]] drücken und drehen: [[KNOB1]] Tempo, [[KNOB2]] Swing, [[KNOB3]] Drift.",
     "Apasă [[HOME]] și rotește [[KNOB1]] pentru tempo, [[KNOB2]] pentru swing, [[KNOB3]] pentru drift."),
   T("Press [[SAVE]]. The project stays in the device.",
     "[[SAVE]] drücken. Das Projekt bleibt im Gerät.",
     "Apasă [[SAVE]]. Proiectul rămâne în aparat."))

h("a", 5, T("the panel", "das panel", "panoul"))
pre(SAME("""  MASTER   SELECT     ┌──────────┐    KNOB1   KNOB2   KNOB3   KNOB4
                      │  screen  │
  PRESETS  ALGORITHM  │          │    [FX]  [SEL] [ENV] [LFO] [EDIT] [GLO]
                      └──────────┘    [HOME][SAVE][ARP] [SEQ] [PLAY] [REC]
  [OCT-] [OCT+]

  black:  KICK SUB HAT PERC STAB CLICK │ CLEAR ◀ ▶ NEW UNDO
  white:  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16"""))
table(T(["control", "what it does"], ["bedienelement", "funktion"], ["control", "ce face"]),
      ("[[MASTER]]", T("volume", "Lautstärke", "volum")),
      ("[[SELECT]]", T("selects the track; on the TIMING page it steps from hit to hit",
                       "wählt die Spur; auf der Seite TIMING springt es von Schlag zu Schlag",
                       "alege pista; pe pagina TIMING sare de la o lovitură la alta")),
      ("[[PRESETS]]", T("pattern A, or one of its variations B to D", "Pattern A oder eine seiner Spielarten B bis D",
                        "pattern-ul A sau una dintre variantele lui, B până la D")),
      ("[[ALGORITHM]]", T("loop length of the track, 1 to 16 steps", "Looplänge der Spur, 1 bis 16 Steps",
                          "lungimea buclei pistei, 1 până la 16 pași")),
      ("[[KNOB1]] – [[KNOB4]]", T("the four values shown on the screen", "die vier Werte im Display",
                                  "cele patru valori de pe ecran")),
      ("[[OCT−]] [[OCT+]]", T("previous and next track; in keys mode the octave",
                              "vorige und nächste Spur; im Tastenmodus die Oktave",
                              "pista anterioară și următoare; în modul clape, octava")),
      ("[[HOME]]", T("page GROOVE; pressed again: GROOVE 2 (the engines of tracks 5 and 6)",
                     "Seite GROOVE; nochmal gedrückt: GROOVE 2 (die Engines der Spuren 5 und 6)",
                     "pagina GROOVE; apăsat din nou: GROOVE 2 (engine-urile pistelor 5 și 6)")),
      ("[[EDIT]]", T("page SOUND of the track; pressed again: SOUND 2", "Seite SOUND der Spur; nochmal: SOUND 2",
                     "pagina SOUND a pistei; apăsat din nou: SOUND 2")),
      ("[[ENV]]", T("page MIX of the track", "Seite MIX der Spur", "pagina MIX a pistei")),
      ("[[FX]]", T("page FX; again: SIDECHAIN; a third time: SLICE; a fourth: SLICE LFO. Held: the effects back to the "
                   "style's start (delay, reverb, sidechain; the track's sidechain amount, SLICE and its LFO)",
                   "Seite FX; nochmal: SIDECHAIN; ein drittes Mal: SLICE; ein viertes: SLICE LFO. Gehalten: die "
                   "Effekte zurück auf den Start des Stils (Delay, Reverb, Sidechain; Sidechain-Anteil, SLICE und "
                   "SLICE LFO der Spur)",
                   "pagina FX; din nou: SIDECHAIN; a treia oară: SLICE; a patra: SLICE LFO. Ținut: efectele înapoi "
                   "la începutul stilului (delay, reverb, sidechain; cota de sidechain, SLICE și LFO-ul lui ale "
                   "pistei)")),
      ("[[GLO]]", T("page GLOBAL; pressed again: GLOBAL 2 (MODE LAZY/HARD)", "Seite GLOBAL; nochmal gedrückt: GLOBAL 2 (MODE LAZY/HARD)",
                    "pagina GLOBAL; apăsat din nou: GLOBAL 2 (MODE LAZY/HARD)")),
      ("[[SEQ]]", T("back to the steps; pages EUCLID, LINK, TIMING in turn",
                    "zurück zu den Steps; Seiten EUCLID, LINK, TIMING der Reihe nach",
                    "înapoi la pași; paginile EUCLID, LINK, TIMING pe rând")),
      ("[[SEL]]", T("tap: mute the track. Hold: solo. Held, the track keys mute their tracks",
                    "kurz: Spur stumm. Halten: Solo. Gehalten schalten die Spurtasten ihre Spuren stumm",
                    "scurt: pista pe mut. Ținut: solo. Ținut, clapele pistelor le pun pe mut")),
      ("[[ARP]]", T("tap: mutate, one small change; hold: FILL (steps with FILL play, !FILL rest)",
                    "kurz: Mutate, eine kleine Änderung; halten: FILL (Steps mit FILL spielen, !FILL schweigen)",
                    "scurt: mutate, o schimbare mică; ținut: FILL (pașii cu FILL cântă, !FILL tac)")),
      ("[[LFO]]", T("page LFO 1 of the track; again: LFO 2; a third time: MOD. Held: the track's sound back to its "
                    "start (sound, mix, LFOs, MOD, SLICE; the steps stay; undo takes it back)",
                    "Seite LFO 1 der Spur; nochmal: LFO 2; ein drittes Mal: MOD. Gehalten: der Klang der Spur zurück "
                    "auf den Start (Sound, Mix, LFOs, MOD, SLICE; die Steps bleiben; Undo holt ihn zurück)",
                    "pagina LFO 1 a pistei; din nou: LFO 2; a treia oară: MOD. Ținut: sunetul pistei înapoi la "
                    "început (sunet, mix, LFO-uri, MOD, SLICE; pașii rămân; undo îl aduce înapoi)")),
      ("[[REC]]", T("keys mode: the keys play the track", "Tastenmodus: die Tasten spielen die Spur",
                    "modul clape: clapele cântă pista")),
      ("[[SAVE]]", T("save; held 2 s: save and good night", "speichern; 2 s gehalten: speichern und gute Nacht",
                    "salvează; ținut 2 s: salvează și noapte bună")),
      ("[[PLAY STOP]]", T("start and stop", "Start und Stopp", "pornire și oprire")),
      (T("16 white keys", "16 weiße Tasten", "16 clape albe"),
       T("the steps of the selected track", "die Steps der gewählten Spur", "pașii pistei selectate")),
      (T("black keys 1 – 6", "schwarze Tasten 1 – 6", "clapele negre 1 – 6"),
       SAME("KICK, SUB, HAT, PERC, STAB, CLICK")),
      (T("black keys 7 – 11", "schwarze Tasten 7 – 11", "clapele negre 7 – 11"),
       T("clear the track, shift it left, shift it right, the track new (held: the whole groove), undo",
         "Spur leeren, nach links schieben, nach rechts schieben, Spur neu (gehalten: ganzer Groove), Undo",
         "golește pista, mut-o la stânga, mut-o la dreapta, pista nouă (ținut: tot groove-ul), undo")))

h("a", 6, T("the screen", "das display", "ecranul"))
img("groove", T("Six lanes, one per track. The selected track is marked white.",
                "Sechs Zeilen, eine pro Spur. Die gewählte Spur ist weiß markiert.",
                "Șase rânduri, câte unul pe pistă. Pista selectată este marcată cu alb."))
ul(T("A filled cell is a step that plays. A tall cell has an accent.",
     "Ein gefülltes Kästchen ist ein Step, der spielt. Ein hohes Kästchen hat einen Akzent.",
     "O celulă plină este un pas care cântă. O celulă înaltă are accent."),
   T("The darker the cell, the lower its chance (stepless, 1 to 100 %). A short bar before a sub or stab cell: it "
     "slides from the note before.",
     "Je dunkler das Kästchen, desto geringer die Chance (stufenlos, 1 bis 100 %). Ein kurzer Strich vor einem "
     "Sub- oder Stab-Kästchen: Es gleitet vom Ton davor.",
     "Cu cât celula e mai închisă, cu atât șansa e mai mică (continuu, 1–100 %). O liniuță scurtă înaintea unei "
     "celule de sub sau stab: alunecă de la nota dinainte."),
   T("A cell split by lines is a ratchet: two to four hits in one step.",
     "Ein durch Linien geteiltes Kästchen ist ein Ratchet: zwei bis vier Schläge in einem Step.",
     "O celulă împărțită de linii este un ratchet: două până la patru lovituri într-un pas."),
   T("An orange mark in a cell: the step has its own sound (a lock).",
     "Eine orange Marke im Kästchen: Der Step hat seinen eigenen Klang (Lock).",
     "Un semn portocaliu în celulă: pasul are sunetul lui (lock)."),
   T("A cell that sits off the grid plays early or late.",
     "Ein Kästchen neben dem Raster spielt früher oder später.",
     "O celulă care stă lângă grilă cântă mai devreme sau mai târziu."),
   T("Small dots: steps beyond the loop length of the track.",
     "Kleine Punkte: Steps jenseits der Looplänge der Spur.",
     "Puncte mici: pași dincolo de lungimea buclei pistei."),
   T("A struck-through name is muted. An orange square beside a name: the track is linked to another.",
     "Ein durchgestrichener Name ist stumm. Ein oranges Quadrat neben dem Namen: Die Spur ist verknüpft.",
     "Un nume tăiat este pe mut. Un pătrat portocaliu lângă nume: pista este legată de alta."),
   T("Orange in the grid is the playhead. The lower part shows what [[KNOB1]] to [[KNOB4]] turn.",
     "Orange im Raster ist der Playhead. Der untere Teil zeigt, was [[KNOB1]] bis [[KNOB4]] drehen.",
     "Portocaliul din grilă este poziția de redare. Partea de jos arată ce rotesc [[KNOB1]] până la [[KNOB4]]."))

# ------------------------------------------------------------------ side b ---
h("b", 1, T("six tracks", "sechs spuren", "șase piste"))
p(T("The roles are fixed. Press [[EDIT]] and the four knobs shape the selected track.",
    "Die Rollen sind fest. [[EDIT]] drücken, dann formen die vier Knöpfe die gewählte Spur.",
    "Rolurile sunt fixe. Apasă [[EDIT]] și cele patru butoane modelează pista selectată."))
table(T(["track", "sound", "KNOB1", "KNOB2", "KNOB3", "KNOB4"], ["spur", "klang", "KNOB1", "KNOB2", "KNOB3", "KNOB4"],
        ["pistă", "sunet", "KNOB1", "KNOB2", "KNOB3", "KNOB4"]),
      ("KICK", T("sine with a falling pitch, a click, soft clipping",
                 "Sinus mit fallender Tonhöhe, Click, weiche Sättigung",
                 "sinus cu înălțime care coboară, un click, saturație moale"), "TUNE", "DECAY", "PUNCH", "DRIVE"),
      ("SUB", T("sine with a short FM attack; notes glide. No bass boost of its own: the low end is GROOVE 2 BASS. An octave over the root (F2), so small "
                "speakers carry it; SOUND 2 PITCH -12 for the deep sub",
                "Sinus mit kurzem FM-Anschlag; Noten gleiten. Kein eigener Bass-Boost: das Fundament regelt GROOVE 2 BASS. Eine Oktave über dem Grundton (F2), damit "
                "ihn auch kleine Boxen tragen; SOUND 2 PITCH -12 für den tiefen Sub",
                "sinus cu un atac FM scurt; notele alunecă. Fără bass boost propriu: fundamentul îl reglează GROOVE 2 BASS. O octavă peste fundamentală (F2), ca să-l "
                "ducă și boxele mici; SOUND 2 PITCH -12 pentru sub-ul adânc"), "DECAY", "FM", "RATIO", "GLIDE"),
      ("HAT", T("metallic FM against noise; an accent opens it", "metallisches FM gegen Rauschen; ein Akzent öffnet",
                "FM metalic contra zgomot; accentul îl deschide"), "DECAY", "TONE", "METAL", "OPEN"),
      ("PERC", T("one FM pair with a pitch bend: rim, wood, tom, blip",
                 "ein FM-Paar mit Pitch-Bend: Rim, Holz, Tom, Blip",
                 "o pereche FM cu pitch bend: rim, lemn, tom, blip"), "DECAY", "FM", "RATIO", "BEND"),
      ("STAB", T("a three-note chord through a closing filter; CHORD: TRIAD, 7TH, 9TH, SUS, 5TH, built in the key (on III or VI "
                   "major, as the scale has it)",
                 "ein Dreiklang durch ein schließendes Filter; CHORD: TRIAD, 7TH, 9TH, SUS, 5TH, in der Tonart gebaut (auf III "
                   "oder VI Dur, wie die Skala es hat)",
                 "un acord de trei note printr-un filtru care se închide; CHORD: TRIAD, 7TH, 9TH, SUS, 5TH, construit în "
                   "tonalitate (pe III sau VI major, cum o are gama)"), "DECAY", "BRIGHT", "CHORD", "DETUNE"),
      ("CLICK", T("a grain of noise through a resonant filter, somewhere in the stereo field",
                  "ein Rauschkorn durch ein Resonanzfilter, irgendwo im Stereofeld",
                  "un grăunte de zgomot printr-un filtru rezonant, undeva în câmpul stereo"),
       "DECAY", "FREQ", "RESO", "SCATTER"))

p(T("[[EDIT]] twice opens SOUND 2, which shapes the voice. [[KNOB1]] PITCH moves the whole track up to 24 semitones "
    "either way. [[KNOB2]] is the attack for hat, stab and click (from a click to a swell), and for the other three "
    "a time that was fixed: the kick's CLICK, the sub's FM.TIME, the percussion's B.TIME (its bend). [[KNOB3]] is "
    "DRIVE, a saturation from warm to broken (the kick has its own on SOUND; here it has P.TIME, how fast its pitch "
    "falls). [[KNOB4]] CRUSH lowers the bit depth and the sample rate. Out of the box everything sounds as it did "
    "before the page existed. All of it can be locked per step and moved by the LFOs.",
    "[[EDIT]] zweimal öffnet SOUND 2, das die Stimme formt. [[KNOB1]] PITCH verschiebt die ganze Spur um bis zu 24 "
    "Halbtöne. [[KNOB2]] ist der Einsatz (Attack) bei Hat, Stab und Click (vom Knacken bis zum Anschwellen), bei den "
    "anderen drei eine bisher feste Zeit: CLICK der Kick, FM.TIME des Sub, B.TIME der Percussion (ihr Bend). "
    "[[KNOB3]] ist DRIVE, eine Sättigung von warm bis kaputt (die Kick hat ihre auf SOUND; hier P.TIME, wie schnell "
    "ihre Tonhöhe fällt). [[KNOB4]] CRUSH senkt Bittiefe und Samplerate. Ab Werk klingt alles wie vor dieser Seite. "
    "Alles lässt sich pro Step locken und mit den LFOs bewegen.",
    "[[EDIT]] de două ori deschide SOUND 2, care modelează vocea. [[KNOB1]] PITCH mută toată pista cu până la 24 de "
    "semitonuri. [[KNOB2]] este atacul pentru hat, stab și click (de la un click la o umflare), iar pentru celelalte "
    "trei un timp care era fix: CLICK al kick-ului, FM.TIME al sub-ului, B.TIME al percuției (bend-ul ei). "
    "[[KNOB3]] este DRIVE, o saturație de la cald la distrus (kick-ul o are pe SOUND; aici are P.TIME, cât de repede "
    "îi scade înălțimea). [[KNOB4]] CRUSH scade adâncimea de biți și rata de eșantionare. Din fabrică totul sună ca "
    "înainte de această pagină. Totul se poate bloca pe pas și mișca prin LFO-uri."))
table(T(["track", "KNOB1", "KNOB2", "KNOB3", "KNOB4"], ["spur", "KNOB1", "KNOB2", "KNOB3", "KNOB4"],
        ["pistă", "KNOB1", "KNOB2", "KNOB3", "KNOB4"]),
      ("KICK", "PITCH", "CLICK", "P.TIME", "CRUSH"),
      ("SUB", "PITCH", "FM.TIME", "DRIVE", "CRUSH"),
      ("HAT", "PITCH", "ATTACK", "DRIVE", "CRUSH"),
      ("PERC", "PITCH", "B.TIME", "DRIVE", "CRUSH"),
      ("STAB", "PITCH", "ATTACK", "DRIVE", "CRUSH"),
      ("CLICK", "PITCH", "ATTACK", "DRIVE", "CRUSH"))

p(T("NEW (the fourth black key from the right) renews the selected track, and only it, in the groove the others "
    "make: the kick tuned to the key, the sub between the kicks starting on the root, the hats on the off-beat, the "
    "percussion turned off the kick, the stab a phrase in the scale. Its colour (for hat, percussion, stab and "
    "click) changes too, within ranges that suit it; level, pan and sends stay. Hold NEW for half a second for a "
    "whole new groove: a new density, then every track in turn. UNDO takes it back.",
    "NEW (die vierte schwarze Taste von rechts) erneuert die gewählte Spur, und nur sie, passend zum Groove der "
    "anderen: die Kick auf die Tonart gestimmt, der Sub zwischen den Kicks und auf dem Grundton beginnend, die Hats "
    "auf dem Offbeat, die Percussion von der Kick weggedreht, der Stab als Phrase in der Skala. Auch ihre "
    "Klangfarbe (bei Hat, Percussion, Stab und Click) ändert sich, in passenden Grenzen; Pegel, Pan und Sends "
    "bleiben. NEW eine halbe Sekunde halten: ein ganz neuer Groove, erst eine neue Dichte, dann alle Spuren der "
    "Reihe nach. UNDO nimmt es zurück.",
    "NEW (a patra clapă neagră de la dreapta) reînnoiește pista selectată, și doar pe ea, în groove-ul celorlalte: "
    "kick-ul acordat în tonalitate, sub-ul între kick-uri începând pe fundamentală, hat-urile pe contratimp, "
    "percuția rotită departe de kick, stab-ul o frază în gamă. Se schimbă și culoarea ei (la hat, percuție, stab și "
    "click), în limite potrivite; nivelul, pan-ul și send-urile rămân. Ține NEW o jumătate de secundă pentru un "
    "groove complet nou: o densitate nouă, apoi toate pistele pe rând. UNDO anulează."))

h("b", 2, T("steps", "steps", "pași"))
p(T("Tap a white key: the step turns on or off. Hold a white key and turn: the knobs edit that step alone.",
    "Weiße Taste tippen: Der Step geht an oder aus. Weiße Taste halten und drehen: Die Knöpfe ändern nur diesen Step.",
    "Atinge o clapă albă: pasul pornește sau se oprește. Ține o clapă albă și rotește: butoanele schimbă doar acel pas."))
img("step", T("A step held: note, chance, accent, ratchet.", "Ein gehaltener Step: Note, Chance, Akzent, Ratchet.",
              "Un pas ținut: notă, șansă, accent, ratchet."))
table(T(["hold a step and", "result"], ["step halten und", "ergebnis"], ["ține un pas și", "rezultat"]),
      (T("turn [[KNOB1]]", "[[KNOB1]] drehen", "rotește [[KNOB1]]"),
       T("note, up to 24 semitones up or down", "Note, bis zu 24 Halbtöne hoch oder runter",
         "nota, până la 24 de semitonuri în sus sau în jos")),
      (T("turn [[KNOB2]]", "[[KNOB2]] drehen", "rotește [[KNOB2]]"),
       T("chance, stepless: 1 % a click, 1 to 100 %", "Chance, stufenlos: 1 % pro Raste, 1 bis 100 %",
         "șansa, continuu: 1 % pe treaptă, 1–100 %")),
      (T("turn [[KNOB3]]", "[[KNOB3]] drehen", "rotește [[KNOB3]]"),
       T("accent on or off; on SUB and STAB: OFF, ACC, SLIDE, ACC+SLIDE. A slide glides from the note before "
         "without a new attack",
         "Akzent an oder aus; bei SUB und STAB: OFF, ACC, SLIDE, ACC+SLIDE. Ein Slide gleitet vom Ton davor, ohne "
         "neuen Anschlag",
         "accent pornit sau oprit; la SUB și STAB: OFF, ACC, SLIDE, ACC+SLIDE. Un slide alunecă de la nota "
         "dinainte, fără atac nou")),
      (T("turn [[KNOB4]]", "[[KNOB4]] drehen", "rotește [[KNOB4]]"),
       T("ratchet: 1 to 4 hits in the step", "Ratchet: 1 bis 4 Schläge im Step", "ratchet: 1 până la 4 lovituri în pas")),
      (T("turn [[SELECT]]", "[[SELECT]] drehen", "rotește [[SELECT]]"),
       T("the step plays earlier or later", "der Step spielt früher oder später", "pasul cântă mai devreme sau mai târziu")),
      (T("turn [[ALGORITHM]]", "[[ALGORITHM]] drehen", "rotește [[ALGORITHM]]"),
       T("trig condition: 1:2 … 8:8 (bar A of every B), FILL, !FILL, PRE, !PRE, 1ST, !1ST. A notch in the cell's "
         "corner marks it",
         "Trig-Bedingung: 1:2 … 8:8 (Takt A von je B), FILL, !FILL, PRE, !PRE, 1ST, !1ST. Eine Kerbe in der Ecke "
         "des Kästchens zeigt sie",
         "condiție de trig: 1:2 … 8:8 (măsura A din fiecare B), FILL, !FILL, PRE, !PRE, 1ST, !1ST. O crestătură în "
         "colțul celulei o arată")),
      (T("press [[SEL]]", "[[SEL]] drücken", "apasă [[SEL]]"),
       T("removes the step's shift and locks", "löscht Verschiebung und Locks des Steps",
         "șterge decalajul și lock-urile pasului")))

h("b", 3, T("a sound for one step", "ein klang für einen step", "un sunet pentru un singur pas"))
p(T("Press [[EDIT]]. Hold a white key and turn a knob. The value now belongs to that step only; the track keeps "
    "its own. This is a lock. Locked values show in orange.",
    "[[EDIT]] drücken. Weiße Taste halten und einen Knopf drehen. Der Wert gehört jetzt nur diesem Step; die Spur "
    "behält ihren eigenen. Das ist ein Lock. Gelockte Werte erscheinen orange.",
    "Apasă [[EDIT]]. Ține o clapă albă și rotește un buton. Valoarea aparține acum doar acelui pas; pista o "
    "păstrează pe a ei. Acesta este un lock. Valorile cu lock apar cu portocaliu."))
img("lock", T("Step 1 of the kick with its own TUNE.", "Step 1 der Kick mit eigenem TUNE.",
              "Pasul 1 al kick-ului cu propriul TUNE."))

h("b", 4, SAME("lfo"))
p(T("Every track has two LFOs: slow waves in time with the groove. [[LFO]] opens the first, [[LFO]] again the "
    "second. RATE is one cycle, from a sixteenth to sixteen bars. DEPTH moves the value either way, up to half its "
    "range; zero is off. TARGET is one of the track's sound parameters (SOUND or SOUND 2), or LEVEL, PAN, DELAY, REVERB. SHAPE: "
    "SINE, TRI, SAW, SQR, or RAND (a new value each cycle). Both LFOs may move the same value. The sound parameters "
    "take the LFO at each hit; level, pan and the sends follow it all the time. The LFOs start with the groove at "
    "PLAY and are kept with the pattern.",
    "Jede Spur hat zwei LFOs: langsame Wellen im Takt des Grooves. [[LFO]] öffnet den ersten, nochmal [[LFO]] den "
    "zweiten. RATE ist ein Durchlauf, von einer Sechzehntel bis sechzehn Takte. DEPTH bewegt den Wert in beide "
    "Richtungen, bis zur Hälfte seines Bereichs; null ist aus. TARGET ist ein Klangparameter der Spur (SOUND oder "
    "SOUND 2) oder LEVEL, PAN, DELAY, REVERB. SHAPE: SINE, TRI, SAW, SQR oder RAND (ein neuer Wert pro Durchlauf). Beide LFOs "
    "dürfen denselben Wert bewegen. Klangparameter übernehmen den LFO bei jedem Schlag; Pegel, Pan und Sends folgen "
    "ihm ständig. Die LFOs starten mit dem Groove bei PLAY und werden mit dem Pattern gespeichert.",
    "Fiecare pistă are două LFO-uri: unde lente în ritmul groove-ului. [[LFO]] îl deschide pe primul, încă o dată "
    "[[LFO]] pe al doilea. RATE este un ciclu, de la o șaisprezecime la șaisprezece măsuri. DEPTH mută valoarea în "
    "ambele direcții, până la jumătate din domeniu; zero înseamnă oprit. TARGET este un parametru de sunet al pistei "
    "(SOUND sau SOUND 2) sau LEVEL, PAN, DELAY, REVERB. SHAPE: SINE, TRI, SAW, SQR sau RAND (o valoare nouă la fiecare "
    "ciclu). Ambele LFO-uri pot mișca aceeași valoare. Parametrii de sunet preiau LFO-ul la fiecare lovitură; "
    "nivelul, pan-ul și send-urile îl urmează tot timpul. LFO-urile pornesc cu groove-ul la PLAY și se salvează cu "
    "pattern-ul."))

h("b", 5, T("pages", "seiten", "pagini"))
table(T(["button", "page", "KNOB1", "KNOB2", "KNOB3", "KNOB4"], ["taste", "seite", "KNOB1", "KNOB2", "KNOB3", "KNOB4"],
        ["buton", "pagină", "KNOB1", "KNOB2", "KNOB3", "KNOB4"]),
      ("[[HOME]]", "GROOVE", "TEMPO<br>90 – 160", "SWING<br>50 – 75 %", "DRIFT", "DUCK"),
      ("[[HOME]] ×2", "GROOVE 2", T("TRACK 5<br>STAB, CLICK, 8-BIT, NOISE", "TRACK 5 (Spur 5)<br>STAB, CLICK, 8-BIT, NOISE",
                                    "TRACK 5 (pista 5)<br>STAB, CLICK, 8-BIT, NOISE"),
       T("TRACK 6<br>STAB, CLICK, 8-BIT, NOISE", "TRACK 6 (Spur 6)<br>STAB, CLICK, 8-BIT, NOISE",
         "TRACK 6 (pista 6)<br>STAB, CLICK, 8-BIT, NOISE"), "FILTER<br>LP ← OFF → HP", "BASS"),
      ("[[EDIT]]", "SOUND", T("see “six tracks”", "siehe „sechs spuren“", "vezi „șase piste”"), "", "", ""),
      ("[[EDIT]] ×2", "SOUND 2", "PITCH", T("see above", "siehe oben", "vezi mai sus"), "DRIVE", "CRUSH"),
      ("[[ENV]]", "MIX", "LEVEL", "PAN", "DELAY", "REVERB"),
      ("[[FX]]", "FX", "D.TIME<br>1/16, 1/8, 3/16", "D.FDBK", "R.SIZE", "R.DAMP"),
      ("[[FX]] ×2", "SIDECHAIN", "SOURCE", "DEPTH", "RELEASE", "AMOUNT"),
      ("[[FX]] ×3", "SLICE", "MODE<br>OFF, GATE, STUTTER, GRAIN", "RATE", "RANDOM", "MIX"),
      ("[[FX]] ×4", "SLICE LFO", "RATE", "DEPTH", "TARGET<br>RATE, RANDOM, MIX", "SHAPE"),
      ("[[GLO]]", "GLOBAL", "ROOT<br>C1 – B2", "SCALE<br>MIN, DOR, PHR, PEN, PDOM, HMIN", "CLOCK", "CHAIN"),
      ("[[GLO]] ×2", "GLOBAL 2", "MODE<br>LAZY, HARD", "PLAY<br>LOOP, A-D, RANDOM", "AIR<br>0–100 %", "WORK<br>LIVE, PROD"),
      ("[[SEQ]]", "EUCLID", "HITS", "ROTATE", "CHANCE", "ACCENT"),
      ("[[SEQ]] ×2", "LINK", "SOURCE", "MODE", "FOLLOW", "ACCENT"),
      ("[[SEQ]] ×3", "TIMING", "STEP", "TRACK", T("GLIDE (SUB, STAB)", "GLIDE (SUB, STAB)", "GLIDE (SUB, STAB)"), ""),
      ("[[LFO]]", "LFO 1", "RATE", "DEPTH", "TARGET", "SHAPE"),
      ("[[LFO]] ×2", "LFO 2", "RATE", "DEPTH", "TARGET", "SHAPE"),
      ("[[LFO]] ×3", "MOD", "RESTART", "ENV SRC", "ENV DEPTH", "ENV TGT"))
p(T("Amounts read in per cent: levels, sends, drift, duck, depths (LFO and ENV from -100 to +100 %), drive, "
    "crush, resonance, mix, random and the like; times, pitches and counts keep their own units. The kick starts "
    "at 72 %.",
    "Mengen stehen in Prozent da: Pegel, Sends, Drift, Duck, Tiefen (LFO und ENV von -100 bis +100 %), Drive, "
    "Crush, Resonanz, Mix, Random und Ähnliches; Zeiten, Tonhöhen und Zählwerte behalten ihre Einheiten. Die Kick "
    "startet bei 72 %.",
    "Cantitățile se citesc în procente: niveluri, send-uri, drift, duck, adâncimi (LFO și ENV de la -100 la +100 %), "
    "drive, crush, rezonanță, mix, random și altele asemenea; timpii, înălțimile și numărătorile își păstrează "
    "unitățile. Kick-ul pornește la 72 %."))
p(T("NOISE hisses, rises and falls: white noise through a resonant filter whose cutoff "
    "SWEEPs up or down over the note's LENGTH, a sixteenth to eight bars; TONE where it starts, RESO how narrow; "
    "SWELL on SOUND 2 lets it fall from the start (left), swell to the end (right) or rise and fall. Its generator "
    "puts a riser on bar four of four (a trig condition), a downlifter on bar one, or hiss on the off-beats. "
    "TONE, SWEEP, RESO and SWELL are heard at once, while a sweep runs; LENGTH from the next note on. LENGTH all the "
    "way left is CLAP: three short bursts 9 ms apart and a tail, TONE its centre (about 1.3 kHz), RESO how narrow, "
    "SWEEP becomes TAIL (60 to 500 ms). Half the time the generator puts it on 2 and 4, now and then with a flam "
    "before the 4: the 1-3 kHz that lend a groove its presence. Chosen on GROOVE 2, NOISE comes as this clap on 2 "
    "and 4 (steps 5 and 13); turned to CLAP, LENGTH moves the steps there too. NEW keeps to the mode: a clap stays on 2 and 4 with a figure around it (a flam, a ghost, a fill in bar four), "
    "a sweep stays a riser, a downlifter or hiss. B and C vary each engine by its own rules: a clap gains or loses its "
    "ghost in B and a fill in C, stab chords change order, clicks turn, a melody stays.",
    "NOISE zischt, steigt und fällt: weißes Rauschen durch ein resonantes Filter, dessen "
    "Cutoff über die LENGTH der Note (eine Sechzehntel bis acht Takte) nach oben oder unten SWEEPt; TONE wo es "
    "beginnt, RESO wie eng; SWELL auf SOUND 2 lässt es ab dem Anfang fallen (links), bis zum Ende anschwellen "
    "(rechts) oder steigen und fallen. Sein Generator setzt einen Riser in Takt vier von vier (eine Trig-Bedingung), "
    "einen Downlifter in Takt eins oder Zischen auf die Offbeats. TONE, SWEEP, RESO und SWELL hört man sofort, "
    "während ein Sweep läuft; LENGTH ab der nächsten Note. LENGTH ganz links ist CLAP: drei kurze Rauschstöße "
    "im Abstand von 9 ms und eine Fahne, TONE ihre Mitte (um 1,3 kHz), RESO wie eng, SWEEP wird TAIL (60 bis 500 ms). "
    "Der Generator setzt ihn in der Hälfte der Fälle auf 2 und 4, manchmal mit einem Vorschlag vor der 4: die "
    "1–3 kHz, die einem Groove Präsenz geben. Auf GROOVE 2 gewählt, kommt NOISE als dieser Clap auf 2 und 4 (Steps 5 "
    "und 13); wird LENGTH auf CLAP gedreht, wandern die Steps ebenfalls dorthin. NEW bleibt im Modus: Ein Clap bleibt auf 2 und 4 mit einer Figur drumherum (Vorschlag, Geister-Clap, Fill "
    "in Takt vier), ein Sweep bleibt Riser, Downlifter oder Zischen. B und C variieren jede Engine nach ihren eigenen "
    "Regeln: der Clap bekommt in B einen Geister-Clap dazu oder verliert ihn, in C einen Fill; Stab-Akkorde wechseln die "
    "Reihenfolge, Clicks drehen sich, eine Melodie bleibt.",
    "NOISE șuieră, urcă și coboară: zgomot alb printr-un filtru rezonant al cărui cutoff "
    "face SWEEP în sus sau în jos pe LENGTH-ul notei, de la o șaisprezecime la opt măsuri; TONE de unde pornește, "
    "RESO cât de îngust; SWELL pe SOUND 2 îl face să scadă de la început (stânga), să crească până la sfârșit "
    "(dreapta) sau să urce și să coboare. Generatorul lui pune un riser în măsura patru din patru (o condiție de "
    "trig), un downlifter în măsura unu sau șuierat pe contratimpi. TONE, SWEEP, RESO și SWELL se aud imediat, "
    "cât timp merge un sweep; LENGTH de la nota următoare. LENGTH complet la stânga e CLAP: trei rafale scurte "
    "la 9 ms una de alta și o coadă, TONE centrul (cam 1,3 kHz), RESO cât de îngust, SWEEP devine TAIL (60–500 ms). "
    "Generatorul îl pune în jumătate din cazuri pe 2 și 4, uneori cu un flam înainte de 4: cei 1–3 kHz care dau "
    "prezență unui groove. Ales pe GROOVE 2, NOISE vine ca acest clap pe 2 și 4 (pașii 5 și 13); rotit pe CLAP, "
    "LENGTH mută și pașii acolo. NEW rămâne în mod: un clap rămâne pe 2 și 4 cu o figură în jur (flam, ghost, fill în măsura patru), un sweep "
    "rămâne riser, downlifter sau șuierat. B și C variază fiecare engine după regulile lui: clapul câștigă sau pierde "
    "ghost-ul în B și un fill în C, acordurile stab își schimbă ordinea, click-urile se rotesc, o melodie rămâne."))
p(T("The master, on GROOVE 2 ([[HOME]] twice): FILTER, one knob, low-pass to the left, high-pass to the right, off "
    "in the middle; BASS adds the lows below 100 Hz once more, up to about +9 dB; its partner for the top is AIR on [[GLO]] twice, knob 3: what lies over about 2.5 kHz once more, up to +6 dB (31 % at the start: presence and air). BEAT REPEAT: hold [[SEL]] and a "
    "white key 1 to 4, and the master repeats the beat, eighth, sixteenth or thirty-second from that moment until "
    "you let go.",
    "Die Summe, auf GROOVE 2 ([[HOME]] zweimal): FILTER, ein Regler, links Tiefpass, rechts Hochpass, in der Mitte "
    "aus; BASS legt die Tiefen unter 100 Hz noch einmal drauf, bis etwa +9 dB; das Gegenstück für oben ist AIR auf [[GLO]] zweimal, Regler 3: alles über etwa 2,5 kHz noch einmal, bis +6 dB (ab Werk 31 %: Präsenz und Luft). BEAT REPEAT: [[SEL]] halten und eine "
    "weiße Taste 1 bis 4, und die Summe wiederholt ab diesem Moment eine Viertel, Achtel, Sechzehntel oder "
    "Zweiunddreißigstel, bis du loslässt.",
    "Suma, pe GROOVE 2 ([[HOME]] de două ori): FILTER, un buton, low-pass la stânga, high-pass la dreapta, oprit la "
    "mijloc; BASS adaugă încă o dată joasele sub 100 Hz, până la circa +9 dB; perechea lui pentru sus e AIR pe [[GLO]] de două ori, butonul 3: tot ce e peste circa 2,5 kHz încă o dată, până la +6 dB (31 % la pornire: prezență și aer). BEAT REPEAT: ține [[SEL]] și o clapă "
    "albă 1–4, iar suma repetă din acel moment o pătrime, optime, șaisprezecime sau treizecidoime până dai drumul."))
p(T("Tracks 5 and 6 are free: [[HOME]] twice, GROOVE 2, knobs 1 and 2, and each plays STAB (FM chords), CLICK "
    "(noise grains), 8-BIT (a sound chip) or NOISE (hiss, risers, the clap), two of the same too. A new engine brings its sound and a pattern in its rules and comes in muted: [[SEL]] brings it in when the "
    "moment is right; undo brings the old one back. The track changes in all four patterns (in HARD the new track "
    "is copied into the other three), as long as [[GLO]] twice, knob 4 WORK, says LIVE. WORK PROD is for producing ahead: in HARD only the pattern edited changes, so a track can play another engine in each pattern. Live, that is a voice to swap without leaving the groove.",
    "Die Spuren 5 und 6 sind frei: [[HOME]] zweimal, GROOVE 2, Regler 1 und 2, und jede spielt STAB (FM-Akkorde), "
    "CLICK (Rauschkörner), 8-BIT (ein Soundchip) oder NOISE (Rauschen, Riser, der Clap), auch zweimal dasselbe. Eine neue Engine bringt ihren Klang und ein Pattern nach ihren Regeln mit und "
    "kommt stumm dazu: [[SEL]] holt sie rein, wenn der Moment passt; Undo holt das alte zurück. Die Spur wechselt in "
    "allen vier Patterns (bei HARD wird die neue Spur in die anderen drei übernommen), solange [[GLO]] zweimal, Regler 4 WORK, auf LIVE steht. WORK PROD ist zum Vorproduzieren: bei HARD wechselt nur das bearbeitete Pattern, so spielt eine Spur in jedem Pattern eine andere Engine. Live ist das eine "
    "Stimme zum Tauschen, ohne den Groove zu verlassen.",
    "Pistele 5 și 6 sunt libere: [[HOME]] de două ori, GROOVE 2, butoanele 1 și 2, și fiecare cântă STAB (acorduri FM), "
    "CLICK (boabe de zgomot), 8-BIT (un cip de sunet) sau NOISE (șuierat, risere, clapul), chiar de două ori același. Un engine nou își aduce sunetul și un pattern după regulile lui și "
    "vine pe mut: [[SEL]] îl aduce când e momentul; undo îl aduce înapoi pe cel vechi. Pista se schimbă în toate "
    "cele patru pattern-uri (în HARD pista nouă e copiată în celelalte trei), cât timp [[GLO]] de două ori, butonul 4 WORK, e pe LIVE. WORK PROD e pentru pre-producție: în HARD se schimbă doar pattern-ul editat, așa o pistă poate cânta alt engine în fiecare pattern. Live e o voce de schimbat "
    "fără să ieși din groove."))
p(T("SLICE ([[FX]] three times) cuts up the sound of hat, percussion, stab and click; never the kick and the sub. "
    "GATE opens and shuts it on a grid from the hit (1/32 to 1/128; RANDOM 0 alternates, more shuts slices at "
    "random). STUTTER records the hit's first slice (1/16 to 1/128) and plays it again and again, fainter each time; "
    "RANDOM turns some round, up an octave or silent. GRAIN, a granular light: the track's last 186 ms are always "
    "recorded, and two grains (9 to 90 ms) play pieces of it from elsewhere, RANDOM spreading where, an octave up or "
    "down, backwards. MIX goes from dry to all sliced. GRAIN on two tracks at most: it is the first to go should "
    "the FM-1 run short of time. SLICE has an LFO of its own ([[FX]] four times): RATE, DEPTH, TARGET (the slices' "
    "RATE, RANDOM or MIX), SHAPE; MOD's RESTART restarts it with the track's other two.",
    "SLICE ([[FX]] dreimal) zerschneidet den Klang von Hat, Percussion, Stab und Click; nie Kick und Sub. GATE "
    "öffnet und schließt ihn in einem Raster ab dem Schlag (1/32 bis 1/128; RANDOM 0 abwechselnd, mehr schließt "
    "Stücke zufällig). STUTTER nimmt das erste Stück des Schlags auf (1/16 bis 1/128) und spielt es immer wieder, "
    "jedes Mal leiser; RANDOM dreht manche um, eine Oktave höher oder stumm. GRAIN, Granular light: Die letzten "
    "186 ms der Spur werden immer aufgenommen, zwei Körner (9 bis 90 ms) spielen Stücke daraus von anderswo, RANDOM "
    "streut wo, eine Oktave hoch oder runter, rückwärts. MIX geht von trocken bis ganz zerschnitten. GRAIN auf "
    "höchstens zwei Spuren: Es fliegt als Erstes raus, wenn der FM-1 zu wenig Rechenzeit hat. SLICE hat einen eigenen "
    "LFO ([[FX]] viermal): RATE, DEPTH, TARGET (RATE, RANDOM oder MIX der Stücke), SHAPE; RESTART auf MOD startet "
    "ihn mit den beiden anderen der Spur neu.",
    "SLICE ([[FX]] de trei ori) taie sunetul hat-ului, al percuției, al stab-ului și al click-ului; niciodată kick-ul "
    "și sub-ul. GATE îl deschide și îl închide pe o grilă de la lovitură (1/32–1/128; RANDOM 0 alternează, mai mult "
    "închide bucăți la întâmplare). STUTTER înregistrează prima bucată a loviturii (1/16–1/128) și o cântă iar și "
    "iar, tot mai încet; RANDOM întoarce unele, o octavă mai sus sau mute. GRAIN, granular light: ultimele 186 ms "
    "ale pistei se înregistrează mereu, iar două boabe (9–90 ms) cântă bucăți din ele de altundeva, RANDOM "
    "împrăștie unde, o octavă sus sau jos, invers. MIX merge de la sec la complet tăiat. GRAIN pe cel mult două "
    "piste: pleacă primul dacă FM-1 nu mai are timp de calcul. SLICE are propriul LFO ([[FX]] de patru ori): RATE, "
    "DEPTH, TARGET (RATE, RANDOM sau MIX al bucăților), SHAPE; RESTART de pe MOD îl repornește odată cu celelalte "
    "două ale pistei."))
p(T("Chains between tracks. ACCENT (LINK, fourth knob): the source's accented hits accent this track's hits on "
    "the same step. RESTART (MOD, first knob): each hit of the chosen track starts this track's two LFOs again, "
    "so the movement sits in the groove. ENV (MOD, knobs two to four): how loud the source sounds right now moves "
    "a target of this track, like an LFO's: on level, pan and the sends smoothly all the time, on a sound "
    "parameter at each new hit. KICK on the hat's level with DEPTH below zero: the hat gives way to the kick. A "
    "muted source still works.",
    "Ketten zwischen Spuren. ACCENT (LINK, vierter Regler): Akzentuierte Schläge der Quelle akzentuieren die "
    "Schläge dieser Spur auf demselben Step. RESTART (MOD, erster Regler): Jeder Schlag der gewählten Spur startet "
    "die beiden LFOs dieser Spur neu, so sitzt die Bewegung im Groove. ENV (MOD, Regler zwei bis vier): Wie laut "
    "die Quelle gerade klingt, bewegt ein Ziel dieser Spur wie ein LFO: Pegel, Pan und Sends fließend, "
    "Klangparameter bei jedem neuen Schlag. KICK auf den Pegel der Hat mit DEPTH unter null: Die Hat weicht der "
    "Kick. Eine stumme Quelle wirkt weiter.",
    "Lanțuri între piste. ACCENT (LINK, al patrulea buton): loviturile accentuate ale sursei accentuează "
    "loviturile acestei piste pe același pas. RESTART (MOD, primul buton): fiecare lovitură a pistei alese "
    "repornește cele două LFO ale acestei piste, ca mișcarea să stea în groove. ENV (MOD, butoanele doi–patru): "
    "cât de tare sună sursa acum mișcă o țintă a acestei piste, ca un LFO: nivel, pan și send-uri continuu, "
    "parametri de sunet la fiecare lovitură nouă. KICK pe nivelul hat-ului cu DEPTH sub zero: hat-ul se dă la o "
    "parte din calea kick-ului. O sursă mută lucrează mai departe."))
p(T("Trig conditions (hold a step, turn [[ALGORITHM]]): 1:2 plays in the first of every two bars, 3:4 in the third "
    "of every four, up to 8:8. FILL plays only while [[ARP]] is held, !FILL only when it is not. PRE plays when "
    "the track's last condition came out true, !PRE when not. 1ST only in the first bar after PLAY. The generator "
    "gives some quiet hats a 1:2 or 3:4 now and then: the groove breathes over four bars.",
    "Trig-Bedingungen (Step halten, [[ALGORITHM]] drehen): 1:2 spielt im ersten von je zwei Takten, 3:4 im dritten "
    "von je vier, bis 8:8. FILL spielt nur, solange [[ARP]] gehalten wird, !FILL nur dann nicht. PRE spielt, wenn "
    "die letzte Bedingung der Spur zutraf, !PRE wenn nicht. 1ST nur im ersten Takt nach PLAY. Der Generator gibt "
    "manchen leisen Hats ab und zu ein 1:2 oder 3:4: Der Groove atmet über vier Takte.",
    "Condiții de trig (ține un pas, rotește [[ALGORITHM]]): 1:2 cântă în prima din fiecare două măsuri, 3:4 în a "
    "treia din fiecare patru, până la 8:8. FILL cântă doar cât e ținut [[ARP]], !FILL doar când nu. PRE cântă când "
    "ultima condiție a pistei a fost adevărată, !PRE când nu. 1ST doar în prima măsură după PLAY. Generatorul dă "
    "din când în când unor hat-uri încete un 1:2 sau 3:4: groove-ul respiră peste patru măsuri."))
p(T("Two minutes untouched and the screen dreams: only the name, grey. Every kick pumps it up like a ball from "
    "its middle; on every step the next letter glows orange, one at a time. Behind it, dimmed, the sixteen by six "
    "dots light with what plays. The name drifts and bounces. Any touch wakes it, and still does what it does.",
    "Zwei Minuten unberührt, und der Bildschirm träumt: nur der Name, grau. Jede Kick pumpt ihn kugelförmig aus "
    "seiner Mitte auf; bei jedem Step leuchtet der nächste Buchstabe orange, immer nur einer. Dahinter, gedimmt, "
    "leuchten die sechzehn mal sechs Punkte mit, was spielt. Der Name treibt und prallt ab. Jede Berührung weckt ihn und tut trotzdem, was sie tut.",
    "Două minute neatins și ecranul visează: doar numele, gri. Fiecare kick îl umflă ca pe o minge din "
    "mijloc; la fiecare pas următoarea literă se aprinde portocaliu, câte una. În spate, estompate, cele "
    "șaisprezece pe șase puncte se aprind cu ce cântă. Numele plutește și ricoșează. Orice atingere îl trezește și își face totuși treaba."))
p(T("DRIFT moves timbre, decay, level and timing slowly and at random. At zero the machine is exact. "
    "The kick's timing never drifts.",
    "DRIFT bewegt Klangfarbe, Ausklang, Lautstärke und Timing langsam und zufällig. Bei null ist die Maschine exakt. "
    "Das Timing der Kick driftet nie.",
    "DRIFT mișcă timbrul, decay-ul, nivelul și timingul încet și la întâmplare. La zero mașina este exactă. "
    "Timingul kick-ului nu se mișcă niciodată."))

# ------------------------------------------------------------------ side c ---
h("b", 6, T("factory values", "werkseinstellungen", "valori din fabrică"))
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_st = F["style"]["romi"]
SCALE_DE = {"minor": "Moll", "dorian": "Dorisch", "phrygian": "Phrygisch", "minor pentatonic": "Moll-Pentatonik",
            "phrygian dominant": "Phrygisch-dominant", "harmonic minor": "Harmonisch Moll"}
SCALE_RO = {"minor": "minor", "dorian": "doric", "phrygian": "frigic", "minor pentatonic": "pentatonic minor",
            "phrygian dominant": "frigic dominant", "harmonic minor": "minor armonic"}
p(T(f"Read from the firmware's code as this manual was built ({F['date']}, {F['commit']}). A new groove starts at "
    f"{_st['bpm']} BPM, swing {_st['swing']} %, drift {pct(_st['drift'])}, duck {pct(_st['duck'])}, in "
    f"{NOTE_NAMES[_st['root'] % 12]} {F['scales'][_st['scale']]}. The sounds below are where a track starts; NEW moves "
    "colour and decay within ranges around them. Levels and sends read in per cent, as on the screen.",
    f"Aus dem Code der Firmware gelesen, als dieses Handbuch gebaut wurde ({F['date']}, {F['commit']}). Ein neuer Groove "
    f"startet mit {_st['bpm']} BPM, Swing {_st['swing']} %, Drift {pct(_st['drift'])}, Duck {pct(_st['duck'])}, in "
    f"{NOTE_NAMES[_st['root'] % 12]} {SCALE_DE[F['scales'][_st['scale']]]}. Die Klänge unten sind der Startpunkt einer Spur; NEW "
    "bewegt Klangfarbe und Ausklang in Bereichen darum. Pegel und Sends in Prozent, wie auf dem Display.",
    f"Citite din codul firmware-ului la construirea acestui manual ({F['date']}, {F['commit']}). Un groove nou pornește "
    f"la {_st['bpm']} BPM, swing {_st['swing']} %, drift {pct(_st['drift'])}, duck {pct(_st['duck'])}, în "
    f"{NOTE_NAMES[_st['root'] % 12]} {SCALE_RO[F['scales'][_st['scale']]]}. Sunetele de mai jos sunt punctul de pornire al unei "
    "piste; NEW mișcă timbrul și decay-ul în jurul lor. Nivelurile și send-urile în procente, ca pe ecran."))


def _knobs(names, vals):
    """name and value as the screen shows them (PITCH in semitones from its middle), unbroken"""
    return "<br>".join(f"{n}\u00a0{(v - 24) if n == 'PITCH' else v}" for n, v in zip(names, vals))


table(T(["track", "SOUND", "SOUND 2", "level", "pan", "delay", "reverb"],
        ["spur", "SOUND", "SOUND 2", "pegel", "pan", "delay", "hall"],
        ["pistă", "SOUND", "SOUND 2", "nivel", "pan", "delay", "reverb"]),
      *[(f"[[{F['tracks']['romi'][t]}]]", _knobs(F["sound"]["romi"][t], F["romi_def"][t][:4]),
         _knobs(F["sound2"]["romi"][t], F["romi_q"][t]), pct(F["romi_def"][t][4]), pan(F["romi_def"][t][5]),
         pct(F["romi_def"][t][6]), pct(F["romi_def"][t][7])) for t in range(6)])
p(T("Tracks 5 and 6 take these when an engine is chosen on GROOVE 2 (NOISE comes as a clap: LENGTH far left).",
    "Die Spuren 5 und 6 übernehmen diese Werte, wenn auf GROOVE 2 eine Engine gewählt wird (NOISE kommt als Clap: "
    "LENGTH ganz links).",
    "Pistele 5 și 6 iau aceste valori când se alege un engine pe GROOVE 2 (NOISE vine ca un clap: LENGTH complet la "
    "stânga)."))
table(T(["engine", "SOUND", "SOUND 2", "level", "pan", "delay", "reverb"],
        ["engine", "SOUND", "SOUND 2", "pegel", "pan", "delay", "hall"],
        ["engine", "SOUND", "SOUND 2", "nivel", "pan", "delay", "reverb"]),
      *[(F["engines"]["romi"][e], _knobs(F["eng_sound"][e][0], F["eng_def"][e][:4]),
         _knobs(F["eng_sound"][e][1], F["eng_def"][e][8:12]), pct(F["eng_def"][e][4]), pan(F["eng_def"][e][5]),
         pct(F["eng_def"][e][6]), pct(F["eng_def"][e][7])) for e in range(len(F["eng_def"]))])

h("c", 1, T("loop length", "looplänge", "lungimea buclei"))
p(T("[[ALGORITHM]] sets how many steps the selected track loops over. Unequal lengths run against each other.",
    "[[ALGORITHM]] setzt, über wie viele Steps die gewählte Spur läuft. Ungleiche Längen laufen gegeneinander.",
    "[[ALGORITHM]] stabilește peste câți pași rulează pista selectată. Lungimile inegale rulează una contra alteia."))
grid([("KICK", "X...X...X...X..."), ("PERC", "x..x.x.---------")],
     T("The kick loops over 16 steps, the percussion over 7. They meet again after 7 bars.",
       "Die Kick läuft über 16 Steps, die Percussion über 7. Nach 7 Takten treffen sie sich wieder.",
       "Kick-ul rulează peste 16 pași, percuția peste 7. Se reîntâlnesc după 7 măsuri."))

h("c", 2, SAME("euclid"))
p(T("Press [[SEQ]]. The page spreads hits as evenly as the loop allows. Notes stay. Afterwards every step can "
    "still be edited by hand. UNDO brings back what was there.",
    "[[SEQ]] drücken. Die Seite verteilt Schläge so gleichmäßig, wie der Loop es zulässt. Noten bleiben. Danach "
    "lässt sich jeder Step weiter von Hand bearbeiten. UNDO holt das Vorige zurück.",
    "Apasă [[SEQ]]. Pagina distribuie loviturile cât de uniform permite bucla. Notele rămân. După aceea fiecare "
    "pas poate fi editat în continuare de mână. UNDO aduce înapoi ce era înainte."))
table(T(["knob", "value"], ["knopf", "wert"], ["buton", "valoare"]),
      ("[[KNOB1]] HITS", T("number of hits in the loop", "Anzahl der Schläge im Loop", "numărul de lovituri din buclă")),
      ("[[KNOB2]] ROTATE", T("turns the pattern around the loop", "dreht das Muster im Loop", "rotește tiparul în buclă")),
      ("[[KNOB3]] CHANCE", T("chance for all hits, stepless: 1 to 100 %", "Chance für alle Schläge, stufenlos: 1 bis 100 %",
                             "șansa pentru toate loviturile, continuu: 1–100 %")),
      ("[[KNOB4]] ACCENT", T("accent on every hit, or every 2nd, 3rd, 4th; RANDOM: on about one hit in three, thrown anew with each turn",
                             "Akzent auf jedem Schlag oder jedem 2., 3., 4.; RANDOM: auf etwa jedem dritten Schlag, zufällig, bei jedem Drehen neu",
                             "accent pe fiecare lovitură sau la fiecare a 2-a, a 3-a, a 4-a; RANDOM: pe cam una din trei, aleator, din nou la fiecare rotire")))
grid([("PERC", "x...x..x..x..x..")], T("5 hits in 16 steps.", "5 Schläge in 16 Steps.", "5 lovituri în 16 pași."))

h("c", 3, SAME("link"))
p(T("Press [[SEQ]] twice. A track can depend on another track. The track keeps its own steps; the source decides "
    "which of them pass. What counts is whether the source really played, with its chance and its own loop length. "
    "A muted source still decides.",
    "[[SEQ]] zweimal drücken. Eine Spur kann von einer anderen abhängen. Die Spur behält ihre Steps; die Quelle "
    "entscheidet, welche davon durchkommen. Es zählt, ob die Quelle wirklich gespielt hat, mit ihrer Chance und "
    "ihrer eigenen Looplänge. Eine stumme Quelle entscheidet weiter.",
    "Apasă [[SEQ]] de două ori. O pistă poate depinde de altă pistă. Pista își păstrează pașii; sursa decide care "
    "dintre ei trec. Contează dacă sursa a cântat cu adevărat, cu șansa ei și cu lungimea ei de buclă. "
    "O sursă pe mut decide în continuare."))
table(T(["MODE", "the track's steps play"], ["MODE", "die steps der spur spielen"], ["MODE", "pașii pistei cântă"]),
      ("WITH", T("only where the source hits", "nur wo die Quelle schlägt", "doar unde lovește sursa")),
      ("GAPS", T("only where the source is silent", "nur wo die Quelle schweigt", "doar unde sursa tace")),
      ("AFTER", T("one step after a hit of the source", "einen Step nach einem Schlag der Quelle",
                  "la un pas după o lovitură a sursei")))
grid([("KICK", "X...X...X...X..."), ("SUB", ".xxx.xxx.xxx.xxx")],
     T("SUB with all 16 steps set, linked to KICK in mode GAPS: it rolls between the kicks.",
       "SUB mit allen 16 Steps, verknüpft mit KICK im Modus GAPS: Er rollt zwischen den Kicks.",
       "SUB cu toți cei 16 pași, legat de KICK în modul GAPS: se rostogolește între kick-uri."))

p(T("FOLLOW ([[KNOB3]]) links notes instead of steps: the track's notes move with the chords of another track. "
    "From the source's latest written step on, everything the track plays is transposed by that chord's root, "
    "whether the source sounded there or not. By default SUB follows STAB, so bass and chords change together. "
    "Set FOLLOW to OFF to keep the track on its own notes.",
    "FOLLOW ([[KNOB3]]) verknüpft Töne statt Steps: Die Töne der Spur wandern mit den Akkorden einer anderen Spur. "
    "Ab dem letzten geschriebenen Step der Quelle wird alles, was die Spur spielt, um den Grundton dieses Akkords "
    "verschoben, ob die Quelle dort erklungen ist oder nicht. Ab Werk folgt SUB dem STAB, Bass und Akkorde wechseln "
    "also gemeinsam. FOLLOW auf OFF lässt die Spur bei ihren eigenen Tönen.",
    "FOLLOW ([[KNOB3]]) leagă note, nu pași: notele pistei se mută odată cu acordurile altei piste. De la ultimul pas "
    "scris al sursei, tot ce cântă pista este transpus cu fundamentala acelui acord, fie că sursa a sunat acolo, fie "
    "că nu. Din fabrică SUB urmează STAB, deci basul și acordurile se schimbă împreună. FOLLOW pe OFF lasă pista pe "
    "notele ei."))
grid([("STAB", "..X...x....x...."), ("SUB", "xx.x.xx.x.xx.x.x")],
     T("With FOLLOW, the sub plays under each stab chord in that chord's key.",
       "Mit FOLLOW spielt der Sub unter jedem Stab-Akkord in dessen Tonart.",
       "Cu FOLLOW, sub-ul cântă sub fiecare acord stab în tonalitatea acelui acord."))

h("c", 4, SAME("timing"))
p(T("Press [[SEQ]] three times. [[SELECT]] steps from hit to hit. A white key picks a step directly and leaves "
    "it as it is. [[KNOB1]] moves the picked hit earlier (−) or later (+). [[KNOB2]] moves the whole track. "
    "Together they reach half a sixteenth in either direction.",
    "[[SEQ]] dreimal drücken. [[SELECT]] springt von Schlag zu Schlag. Eine weiße Taste wählt einen Step direkt "
    "und lässt ihn, wie er ist. [[KNOB1]] schiebt den gewählten Schlag früher (−) oder später (+). [[KNOB2]] "
    "schiebt die ganze Spur. Zusammen reichen sie eine halbe Sechzehntel in jede Richtung.",
    "Apasă [[SEQ]] de trei ori. [[SELECT]] sare de la o lovitură la alta. O clapă albă alege direct un pas și îl "
    "lasă cum este. [[KNOB1]] mută lovitura aleasă mai devreme (−) sau mai târziu (+). [[KNOB2]] mută toată "
    "pista. Împreună ajung la jumătate de șaisprezecime în fiecare direcție."))
img("timing", T("Step 6 of the percussion late, the whole track a little early.",
                "Step 6 der Percussion spät, die ganze Spur etwas früh.",
                "Pasul 6 al percuției târziu, toată pista puțin devreme."))
p(T("On this page the white keys do not switch steps. Change tracks with the black keys or [[OCT−]] [[OCT+]]. "
    "A linked track can only be moved later.",
    "Auf dieser Seite schalten die weißen Tasten keine Steps. Die Spur wechselst du mit den schwarzen Tasten oder "
    "[[OCT−]] [[OCT+]]. Eine verknüpfte Spur lässt sich nur später schieben.",
    "Pe această pagină clapele albe nu comută pași. Schimbi pista cu clapele negre sau cu [[OCT−]] [[OCT+]]. "
    "O pistă legată poate fi mutată doar mai târziu."))

h("c", 5, SAME("sidechain"))
p(T("Press [[FX]] twice. One track is the source, the kick by default. Each hit of the source pushes the other "
    "tracks down, and the delay and reverb with them. AMOUNT sets how much the selected track gives way. "
    "Mute the source and the pumping stays: a ghost kick.",
    "[[FX]] zweimal drücken. Eine Spur ist die Quelle, ab Werk die Kick. Jeder Schlag der Quelle drückt die "
    "anderen Spuren nach unten, Delay und Reverb mit. AMOUNT bestimmt, wie stark die gewählte Spur nachgibt. "
    "Schalte die Quelle stumm, und das Pumpen bleibt: eine Ghost-Kick.",
    "Apasă [[FX]] de două ori. O pistă este sursa, din fabrică kick-ul. Fiecare lovitură a sursei împinge "
    "celelalte piste în jos, împreună cu delay-ul și reverb-ul. AMOUNT stabilește cât cedează pista selectată. "
    "Pune sursa pe mut și pomparea rămâne: un ghost kick."))

# ------------------------------------------------------------------ side d ---
h("d", 1, T("patterns", "patterns", "pattern-uri"))
p(T("Pattern A is the groove. B, C and D are never other songs: they are ways of playing A, made from it and "
    "made again the moment A changes. B plays A varied: a few hats turned over, percussion and clicks turned on "
    "their loops, a sub hit moved, the same chords in another order, a ghost kick that comes or goes. C plays A "
    "leading into the next bar: the hats on the last sixteenths (a real roll one time in four, its ratchets at a chance), "
    "percussion and clicks, a kick and a sub pickup. D plays A in "
    "a related key: the subdominant, the dominant, the seventh or the third; the stab, the percussion and the sub "
    "move with it; the kick stays A's. The screen's bottom line says which one plays.",
    "Pattern A ist der Groove. B, C und D sind nie andere Songs: Sie sind Spielarten von A, aus A gemacht und neu "
    "gemacht, sobald A sich ändert. B spielt A variiert: ein paar Hats gedreht, Percussion und Clicks auf ihren "
    "Loops verschoben, ein Sub-Schlag versetzt, dieselben Akkorde in anderer Reihenfolge, eine Ghost-Kick, die kommt "
    "oder geht. C spielt A mit Anlauf in den nächsten Takt: Hats auf den letzten Sechzehnteln (ein echter Wirbel nur "
    "jedes vierte Mal, seine Ratchets mit Chance), Percussion und Clicks, ein Auftakt "
    "von Kick und Sub. D spielt A in einer verwandten Tonart: Subdominante, Dominante, Septime oder Terz; Stab, "
    "Percussion und Sub wandern mit, die Kick bleibt die von A. Die unterste Zeile im Display "
    "sagt, welche gerade läuft.",
    "Pattern-ul A este groove-ul. B, C și D nu sunt niciodată alte piese: sunt moduri de a cânta A, făcute din el "
    "și refăcute în clipa în care A se schimbă. B cântă A variat: câteva hat-uri întoarse, percuția și click-urile "
    "rotite pe buclele lor, o lovitură de sub mutată, aceleași acorduri în altă ordine, un ghost kick care apare "
    "sau dispare. C cântă A cu un avânt spre măsura următoare: hat-uri pe ultimele șaisprezecimi (un roll adevărat o dată "
    "din patru, ratchet-urile cu șansă), percuție și click-uri, un preambul de kick și sub. D cântă A într-o tonalitate înrudită: subdominanta, dominanta, "
    "septima sau terța; stab-ul, percuția și sub-ul se mută cu ea, iar kick-ul rămâne cel din A. "
    "Ultimul rând al ecranului spune care cântă."))
ul(T("[[PRESETS]] changes the pattern; while playing, at the next bar. Whatever you change, you change in A, even "
     "while B, C or D plays; they follow at once.",
     "[[PRESETS]] wechselt das Pattern; im Lauf zum nächsten Takt. Was du änderst, änderst du in A, auch während "
     "B, C oder D läuft; sie ziehen sofort nach.",
     "[[PRESETS]] schimbă pattern-ul; în timpul redării, la măsura următoare. Orice schimbi, schimbi în A, chiar "
     "când cântă B, C sau D; ele urmează imediat."),
   T("NEW on B, C or D throws that variation again; A stays.",
     "NEW auf B, C oder D würfelt diese Spielart neu; A bleibt.",
     "NEW pe B, C sau D aruncă din nou acea variantă; A rămâne."),
   T("CHAIN on the GLOBAL page plays A-B, A-C or A-D in turn, four bars each. EVOLVE plays A-D and then makes new "
     "B, C and D for the next round: a set that keeps moving.",
     "CHAIN auf der Seite GLOBAL spielt A-B, A-C oder A-D nacheinander, je vier Takte. EVOLVE spielt A-D und macht "
     "danach neue B, C und D für die nächste Runde: ein Set, das sich ständig weiterentwickelt.",
     "CHAIN de pe pagina GLOBAL cântă A-B, A-C sau A-D pe rând, câte patru măsuri. EVOLVE cântă A-D și apoi face "
     "B, C și D noi pentru runda următoare: un set care se tot mișcă."),
   T("The kick may rest: B now and then leaves out one beat, C often pauses for the last four steps before the bar. "
     "A and D keep it on every quarter.",
     "Die Kick darf ruhen: B lässt ab und zu einen Schlag weg, C pausiert oft in den letzten vier Steps vor dem Takt. "
     "A und D behalten sie auf jeder Viertel.",
     "Kick-ul se poate odihni: B lasă din când în când o lovitură afară, C face des pauză în ultimii patru pași "
     "dinaintea măsurii. A și D îl țin pe fiecare pătrime."),
   T("When C's kick pauses on 13 to 16, the dice decide, one time in three: the kick becomes another (the root or "
     "its fifth, decay, sweep, click and drive moved a little), from D on and in every pattern alike, A too. It "
     "stays so until you change it by hand or C's pause throws again. Once per visit of C; in LAZY and HARD.",
     "Wenn in C die Kick auf 13 bis 16 aussetzt, entscheidet der Würfel, eins zu drei: Die Kick wird eine andere "
     "(Grundton oder Quinte, Ausklang, Sweep, Click und Drive leicht verschoben), ab D und in allen Patterns gleich, "
     "auch in A. So bleibt sie, bis du sie von Hand änderst oder Cs Pause wieder würfelt. Einmal pro Durchgang von "
     "C; in LAZY und HARD.",
     "Când kick-ul din C face pauză pe 13–16, zarul hotărăște, o dată din trei: kick-ul devine altul (fundamentala "
     "sau cvinta, decay, sweep, click și drive mutate puțin), de la D încolo și la fel în toate pattern-urile, și "
     "în A. Rămâne așa până îl schimbi de mână sau până ce pauza din C aruncă iar zarul. O dată pe trecere prin C; "
     "în LAZY și HARD."),
   T("Sub and stab flow: GLIDE (TIMING page, third knob) lets a note that comes while the last one still sounds "
     "glide there; for the sub it is the same knob as on SOUND. SLIDE on a step (hold it, third knob) binds it to "
     "the note before: no new attack, the pitch glides over (with GLIDE at zero in 50 ms). The generator puts a "
     "slide in now and then.",
     "Sub und Stab fließen: GLIDE (Seite TIMING, dritter Regler) lässt einen Ton, der kommt, während der letzte noch "
     "klingt, dorthin gleiten; beim Sub ist es derselbe Wert wie auf SOUND. SLIDE auf einem Step (halten, dritter "
     "Regler) bindet ihn an den Ton davor: kein neuer Anschlag, die Tonhöhe gleitet hinüber (bei GLIDE null in "
     "50 ms). Der Generator setzt ab und zu einen Slide.",
     "Sub-ul și stab-ul curg: GLIDE (pagina TIMING, al treilea buton) face ca o notă care vine cât încă sună cea "
     "dinainte să alunece acolo; la sub e aceeași valoare ca pe SOUND. SLIDE pe un pas (ține-l, al treilea buton) "
     "îl leagă de nota dinainte: fără atac nou, înălțimea alunecă (cu GLIDE la zero, în 50 ms). Generatorul pune "
     "din când în când un slide."),
   T("Two modes, on GLOBAL 2 ([[GLO]] twice), MODE. LAZY is all of the above: the set grows by itself. HARD: "
     "B, C and D start as copies of A and then are yours; you edit the pattern that plays, NEW renews its track "
     "(hold: the whole pattern), all four are saved, EVOLVE stays still. Back in LAZY the HARD patterns wait aside "
     "and come back with HARD.",
     "Zwei Modi, auf GLOBAL 2 ([[GLO]] zweimal), MODE. LAZY ist alles oben: das Set wächst von selbst. HARD: "
     "B, C und D beginnen als Kopien von A und gehören dann dir; bearbeitet wird das Pattern, das läuft, NEW "
     "erneuert dort die Spur (halten: das ganze Pattern), alle vier werden gespeichert, EVOLVE ruht. Zurück in LAZY "
     "warten die HARD-Patterns beiseite und kommen mit HARD wieder.",
     "Două moduri, pe GLOBAL 2 ([[GLO]] de două ori), MODE. LAZY e tot ce e mai sus: setul crește singur. HARD: "
     "B, C și D încep ca și copii ale lui A și apoi sunt ale tale; editezi pattern-ul care cântă, NEW reînnoiește "
     "pista lui (ținut: tot pattern-ul), toate patru se salvează, EVOLVE stă. Înapoi în LAZY, pattern-urile HARD "
     "așteaptă deoparte și revin cu HARD."),
   T("PLAY, the second knob on GLOBAL 2, works in both modes. LOOP stays on the pattern (or follows CHAIN). "
     "A-D plays A, B, C and D, four bars each, and starts again at A. RANDOM jumps to another pattern every four "
     "bars. With CHAIN on EVOLVE, LAZY makes new B, C and D every sixteen bars.",
     "PLAY, der zweite Regler auf GLOBAL 2, wirkt in beiden Modi. LOOP bleibt beim Pattern (oder folgt CHAIN). "
     "A-D spielt A, B, C und D, je vier Takte, und beginnt wieder bei A. RANDOM springt alle vier Takte zu einem "
     "anderen Pattern. Steht CHAIN auf EVOLVE, macht LAZY alle sechzehn Takte neue B, C und D.",
     "PLAY, al doilea buton de pe GLOBAL 2, merge în ambele moduri. LOOP rămâne pe pattern (sau urmează CHAIN). "
     "A-D cântă A, B, C și D, câte patru măsuri, și o ia de la capăt cu A. RANDOM sare la alt pattern la fiecare "
     "patru măsuri. Cu CHAIN pe EVOLVE, LAZY face B, C și D noi la fiecare șaisprezece măsuri."),
   T("A tap on [[SAVE]] writes the changes to the device. The sound stops for a moment. Nothing is saved on its own. "
     "Held for 2 seconds, [[SAVE]] saves and says good night: the picture collapses like an old tube's, the music "
     "fades with it and ends in a smack, \u201cnoapte bun\u0103\u201d appears; then the screen, the sound and the lights "
     "stay off until you switch the FM-1 off, or a touch wakes it.",
     "Ein kurzer Druck auf [[SAVE]] schreibt das Projekt ins Gerät. Der Ton setzt kurz aus. Nichts wird von selbst gespeichert. "
     "2 Sekunden gehalten speichert [[SAVE]] und sagt gute Nacht: Das Bild zieht sich zusammen wie bei einer alten "
     "Röhre, die Musik blendet mit aus und endet in einem Schmatzer, \u201enoapte bun\u0103\u201c erscheint; danach bleiben "
     "Bildschirm, Ton und Lichter aus, bis du das FM-1 ausschaltest oder eine Berührung es weckt.",
     "O apăsare scurtă pe [[SAVE]] scrie proiectul în aparat. Sunetul se oprește o clipă. Nimic nu se salvează singur. "
     "Ținut 2 secunde, [[SAVE]] salvează și spune noapte bună: imaginea se strânge ca la un tub vechi, muzica se "
     "stinge odată cu ea și se termină cu un plescăit, apare \u201enoapte bun\u0103\u201d; apoi ecranul, sunetul și "
     "luminile rămân stinse până închizi FM-1 sau o atingere îl trezește."),
   T("UNDO, the last black key, takes back the last change to A. Pressed again, it brings the change back.",
     "UNDO, die letzte schwarze Taste, nimmt die letzte Änderung an A zurück. Nochmal gedrückt, holt es sie wieder.",
     "UNDO, ultima clapă neagră, anulează ultima schimbare a lui A. Apăsat din nou, o readuce."))

h("d", 2, T("keys and midi", "tasten und midi", "clape și midi"))
ul(T("[[REC]] turns the keys into a keyboard for the selected track. C4 is the track's base note. "
     "[[OCT−]] [[OCT+]] shift two octaves each way.",
     "[[REC]] macht die Tasten zum Keyboard für die gewählte Spur. C4 ist der Grundton der Spur. "
     "[[OCT−]] [[OCT+]] verschieben um bis zu zwei Oktaven.",
     "[[REC]] transformă clapele într-o claviatură pentru pista selectată. C4 este nota de bază a pistei. "
     "[[OCT−]] [[OCT+]] mută cu până la două octave."),
   T("While the groove runs, played notes are written into the step they fall on. [[SEQ]] leads back to the steps.",
     "Läuft der Groove, werden gespielte Noten in den Step geschrieben, auf den sie fallen. [[SEQ]] führt zurück zu den Steps.",
     "Cât timp rulează groove-ul, notele cântate sunt scrise în pasul pe care cad. [[SEQ]] duce înapoi la pași."),
   T("MIDI channels 1 to 6 play the six tracks; note 60 is the base note.",
     "Die MIDI-Kanäle 1 bis 6 spielen die sechs Spuren; Note 60 ist der Grundton.",
     "Canalele MIDI 1 până la 6 cântă cele șase piste; nota 60 este nota de bază."),
   T("Channel 10 is a drum map: 36 kick, 37 and 38 percussion, 39 click, 42 and 44 hat, 46 open hat.",
     "Kanal 10 ist eine Drum-Map: 36 Kick, 37 und 38 Percussion, 39 Click, 42 und 44 Hat, 46 offene Hat.",
     "Canalul 10 este o hartă de tobe: 36 kick, 37 și 38 percuție, 39 click, 42 și 44 hat, 46 hat deschis."),
   T("Start and stop are received. With CLOCK on, clock, start and stop are sent over USB.",
     "Start und Stopp werden empfangen. Mit CLOCK an werden Clock, Start und Stopp über USB gesendet.",
     "Start și stop sunt primite. Cu CLOCK pornit, clock, start și stop sunt trimise prin USB."))

h("d", 3, T("recipes", "rezepte", "rețete"))
table(T(["for", "do this"], ["für", "so geht es"], ["pentru", "fă așa"]),
      (T("a sub that rolls between the kicks", "einen Sub, der zwischen den Kicks rollt",
         "un sub care se rostogolește între kick-uri"),
       T("SUB: [[SEQ]], HITS up to 11. [[SEQ]] again, SOURCE KICK, MODE GAPS. [[EDIT]], GLIDE up.",
         "SUB: [[SEQ]], HITS auf 11. [[SEQ]] nochmal, SOURCE KICK, MODE GAPS. [[EDIT]], GLIDE hoch.",
         "SUB: [[SEQ]], HITS la 11. [[SEQ]] din nou, SOURCE KICK, MODE GAPS. [[EDIT]], GLIDE mai sus.")),
      (T("pumping without a kick", "Pumpen ohne Kick", "pompare fără kick"),
       T("KICK: [[SEL]]. The kick is silent and still ducks the rest. [[FX]] twice, DEPTH to taste.",
         "KICK: [[SEL]]. Die Kick schweigt und duckt weiter den Rest. [[FX]] zweimal, DEPTH nach Geschmack.",
         "KICK: [[SEL]]. Kick-ul tace și tot apasă restul. [[FX]] de două ori, DEPTH după gust.")),
      (T("a stab that breathes", "ein Stab, der atmet", "un stab care respiră"),
       T("STAB: [[LFO]], TARGET DECAY, RATE 4 BAR, DEPTH +30. [[LFO]] again: TARGET PAN, RATE 1 BAR, SHAPE RAND.",
         "STAB: [[LFO]], TARGET DECAY, RATE 4 BAR, DEPTH +30. Nochmal [[LFO]]: TARGET PAN, RATE 1 BAR, SHAPE RAND.",
         "STAB: [[LFO]], TARGET DECAY, RATE 4 BAR, DEPTH +30. Din nou [[LFO]]: TARGET PAN, RATE 1 BAR, SHAPE RAND.")),
      (T("seven against sixteen", "sieben gegen sechzehn", "șapte contra șaisprezece"),
       T("PERC: [[ALGORITHM]] to 7, [[SEQ]], HITS 3. CLICK: [[ALGORITHM]] to 11, CHANCE 50 %.",
         "PERC: [[ALGORITHM]] auf 7, [[SEQ]], HITS 3. CLICK: [[ALGORITHM]] auf 11, CHANCE 50 %.",
         "PERC: [[ALGORITHM]] la 7, [[SEQ]], HITS 3. CLICK: [[ALGORITHM]] la 11, CHANCE 50 %.")),
      (T("lazy hats", "träge Hats", "hat-uri leneșe"),
       T("HAT: [[SEQ]] three times, TRACK to +3. Then [[EDIT]], hold single steps and turn DECAY.",
         "HAT: [[SEQ]] dreimal, TRACK auf +3. Dann [[EDIT]], einzelne Steps halten und DECAY drehen.",
         "HAT: [[SEQ]] de trei ori, TRACK la +3. Apoi [[EDIT]], ține pași separați și rotește DECAY.")),
      (T("eight bars that keep moving", "acht Takte, die sich bewegen", "opt măsuri care se tot mișcă"),
       T("[[GLO]], CHAIN EVOLVE. DRIFT near 60. Let it run; touch A now and then.",
         "[[GLO]], CHAIN EVOLVE. DRIFT um 60. Laufen lassen; ab und zu an A drehen.",
         "[[GLO]], CHAIN EVOLVE. DRIFT în jur de 60. Lasă-l să meargă; atinge A din când în când.")))

h("d", 4, T("small print", "kleingedrucktes", "litere mici"))
ul(T("Up to 32 locks per pattern; one more and the screen says LOCKS FULL. A step moves at most 7/16 of a step, "
     "the whole track 8/16 more, together half a sixteenth. Notes reach 32 semitones down and 31 up.",
     "Bis zu 32 Locks pro Pattern; ein weiterer und das Display zeigt LOCKS FULL. Ein Step verschiebt sich höchstens um "
     "7/16 Step, die ganze Spur um weitere 8/16, zusammen eine halbe Sechzehntel. Noten reichen 32 Halbtöne nach unten "
     "und 31 nach oben.",
     "Până la 32 de lock-uri pe pattern; încă unul și ecranul arată LOCKS FULL. Un pas se mută cel mult 7/16 de pas, "
     "toată pista încă 8/16, împreună o jumătate de șaisprezecime. Notele ajung la 32 de semitonuri în jos și 31 în sus."),
   T("[[SAVE]] writes only what changed: the settings and each pattern are kept apart. USB carries MIDI only.",
     "[[SAVE]] schreibt nur, was sich geändert hat: Einstellungen und jedes Pattern liegen getrennt. Über USB läuft nur MIDI.",
     "[[SAVE]] scrie doar ce s-a schimbat: setările și fiecare pattern sunt păstrate separat. Prin USB trece doar MIDI."),
   T("One level of undo per change. A hold on [[SEL]] or NEW of about half a second is the second job: solo, the "
     "whole groove.",
     "Eine Undo-Stufe pro Änderung. [[SEL]] oder NEW etwa eine halbe Sekunde halten löst die zweite Aufgabe aus: "
     "Solo, ganzer Groove.",
     "Un singur nivel de undo pe schimbare. [[SEL]] sau NEW ținut cam o jumătate de secundă face a doua treabă: "
     "solo, tot groove-ul."),
   T("Muting several tracks at once: hold [[SEL]] and press their black keys, together or one after the other; "
     "each switches its own track off or on, and the selected track stays. Letting go of [[SEL]] then does "
     "nothing more. Mutes belong to A, so they hold in B, C and D too.",
     "Mehrere Spuren auf einmal stumm: [[SEL]] halten und ihre schwarzen Tasten drücken, zusammen oder "
     "nacheinander; jede schaltet ihre Spur aus oder an, die gewählte Spur bleibt. Das Loslassen von [[SEL]] tut "
     "dann nichts weiter. Mutes gehören zu A und gelten damit auch in B, C und D.",
     "Mai multe piste pe mut deodată: ține [[SEL]] și apasă clapele lor negre, împreună sau una după alta; fiecare "
     "își oprește sau pornește pista, iar pista selectată rămâne. Eliberarea lui [[SEL]] nu mai face nimic. "
     "Mute-urile aparțin lui A, deci se aplică și în B, C și D."),
   T("At slow tempos a long delay time does not fit; the delay then takes the next shorter value.",
     "Bei langsamen Tempi passt eine lange Delay-Zeit nicht; das Delay nimmt dann den nächstkürzeren Wert.",
     "La tempo lent, un timp lung de delay nu încape; delay-ul ia atunci valoarea mai scurtă următoare."),
   T("The very first step after start cannot play early.",
     "Der allererste Step nach dem Start kann nicht früher spielen.",
     "Primul pas de după pornire nu poate cânta mai devreme."),
   T("Sound, timing and processor load on the real device are not measured yet.",
     "Klang, Timing und Prozessorlast auf dem echten Gerät sind noch nicht gemessen.",
     "Sunetul, timingul și încărcarea procesorului pe aparatul real nu au fost încă măsurate."),
   T("Built on fm1-base and felucca-bsp. MIT licence. Not affiliated with M-VAVE.",
     "Gebaut auf fm1-base und felucca-bsp. MIT-Lizenz. Nicht mit M-VAVE verbunden.",
     "Construit pe fm1-base și felucca-bsp. Licență MIT. Fără legătură cu M-VAVE."))


# ---------------------------------------------------------------- render ---
def rich(s):
    """escape, then [[NAME]] -> <kbd>, and the few <br> written on purpose"""
    s = html.escape(s, quote=False).replace("&lt;br&gt;", "<br>")
    return re.sub(r"\[\[(.+?)\]\]", r"<kbd>\1</kbd>", s)


def tx(v, lang):
    return rich(v[lang] if isinstance(v, dict) else v)


def render(lang):
    out, side = [], None
    for b in B:
        k = b[0]
        if k == "h":
            if b[1] != side:
                if side:
                    out.append("</section>")
                side = b[1]
                out.append(f'<section class="side"><div class="sidehead"><span class="letter">{side}</span>'
                           f'<span>{tx(SIDES[side], lang)}</span></div>')
            out.append(f'<h2 id="{lang}-{b[1]}{b[2]}"><span class="no">{b[1]}{b[2]}</span>{tx(b[3], lang)}</h2>')
        elif k == "p":
            out.append(f"<p>{tx(b[1], lang)}</p>")
        elif k == "note":
            out.append(f'<p class="note">{tx(b[1], lang)}</p>')
        elif k == "pre":
            out.append(f'<pre class="panel">{html.escape(b[1][lang])}</pre>')
        elif k in ("ol", "ul"):
            out.append(f"<{k}>" + "".join(f"<li>{tx(i, lang)}</li>" for i in b[1]) + f"</{k}>")
        elif k == "table":
            head = b[1][lang]
            rows = "".join("<tr>" + "".join(f"<td>{tx(c, lang)}</td>" for c in r) + "</tr>" for r in b[2])
            out.append('<div class="scroll"><table><thead><tr>' + "".join(f"<th>{rich(c)}</th>" for c in head) +
                       f"</tr></thead><tbody>{rows}</tbody></table></div>")
        elif k == "grid":
            cls = {"X": "c acc", "x": "c on", ".": "c", "-": "c out"}
            lanes = "".join(f'<div class="lane"><span class="name">{n}</span>' +
                            "".join(f'<i class="{cls[ch]}"></i>' for ch in cells) + "</div>" for n, cells in b[1])
            out.append(f'<figure class="grid">{lanes}<figcaption>{tx(b[2], lang)}</figcaption></figure>')
        elif k == "img":
            data = base64.b64encode((ROOT / "manual" / f"screen-{b[1]}.png").read_bytes()).decode()
            out.append(f'<figure class="shot"><img src="data:image/png;base64,{data}" width="240" height="240" '
                       f'alt="{html.escape(b[2][lang])}"><figcaption>{tx(b[2], lang)}</figcaption></figure>')
    out.append("</section>")
    return "\n".join(out)


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ro:MINImal Manual</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* A white-label sleeve: paper, black type set small and lowercase, hairlines, much air; sections numbered like
   the sides of a double 12-inch (a1 .. d4). The only colour is the orange of the device's screen, kept for what
   the screen itself shows in orange. Layout: one narrow column, the side letter in a left margin from 760px. */
:root {
  color-scheme: light;
  --paper: #f4f4f1;
  --ink: #111110;
  --soft: #6b6b66;
  --hair: #cfcfc9;
  --cell: #dcdcd6;
  --signal: #e2551f;
  --sans: "Archivo", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --paper: #0e0e0d; --ink: #e9e8e2; --soft: #8f8e87; --hair: #2c2c29; --cell: #2a2a27; --signal: #ff6a33;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #0e0e0d; --ink: #e9e8e2; --soft: #8f8e87; --hair: #2c2c29; --cell: #2a2a27; --signal: #ff6a33;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 400 16px/1.55 var(--sans); }
.wrap { max-width: 760px; margin: 0 auto; padding: 28px 20px 96px; }

.top { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; flex-wrap: wrap;
  font: 400 12px/1.4 var(--mono); letter-spacing: .04em; text-transform: lowercase; color: var(--soft); }
.langs { display: flex; gap: 2px; }
.langs a { color: var(--soft); text-decoration: none; padding: 6px 10px; border: 1px solid transparent; border-radius: 999px; }
.langs a[aria-current="true"] { color: var(--ink); border-color: var(--ink); }
.langs a:hover { color: var(--ink); }
.top a.out { color: var(--ink); }
a:focus-visible { outline: 2px solid var(--signal); outline-offset: 2px; }

.cover { padding: 64px 0 56px; border-bottom: 1px solid var(--ink); }
.cover h1 { margin: 0; font: 500 clamp(40px, 11vw, 76px)/1 var(--sans); letter-spacing: -.03em; }
.cover h1 span { color: var(--soft); font-weight: 400; }
.cover .what { margin: 18px 0 0; font: 400 13px/1.5 var(--mono); letter-spacing: .04em; text-transform: lowercase; color: var(--soft); }
.cover .what b { color: var(--ink); font-weight: 500; }
.what.try { margin-top: 28px; }
.what.try a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--signal); padding-bottom: 2px; }
.disc { display: flex; gap: 6px; margin-top: 44px; }
.disc i { width: 13px; height: 13px; background: var(--cell); }
.disc i.k { background: var(--ink); }
.disc i.s { background: var(--signal); }

.side { padding-top: 56px; }
.sidehead { display: flex; align-items: baseline; gap: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--hair);
  font: 400 12px/1.4 var(--mono); letter-spacing: .08em; text-transform: lowercase; color: var(--soft); }
.sidehead .letter { font: 500 30px/1 var(--sans); letter-spacing: -.02em; color: var(--ink); }
h2 { margin: 44px 0 12px; font: 500 20px/1.25 var(--sans); letter-spacing: -.01em; text-transform: lowercase; text-wrap: balance; }
h2 .no { display: inline-block; min-width: 38px; font: 400 12px/1 var(--mono); letter-spacing: .06em; color: var(--soft); }
p, li { max-width: 62ch; }
p { margin: 0 0 14px; }
ol, ul { margin: 0 0 14px; padding-left: 20px; }
li { margin: 6px 0; }
ul { list-style: none; padding-left: 0; }
ul li { padding-left: 18px; position: relative; }
ul li::before { content: ""; position: absolute; left: 0; top: .62em; width: 6px; height: 6px; background: var(--ink); }
ol li::marker { font: 400 12px var(--mono); color: var(--soft); }
.note { border-left: 3px solid var(--signal); padding: 2px 0 2px 14px; }
pre.panel { font: 400 11.5px/1.45 var(--mono); color: var(--ink); background: transparent; border: 1px solid var(--hair);
  padding: 14px 16px; overflow-x: auto; margin: 6px 0 22px; }
.toc { margin: 40px 0 0; columns: 2 240px; column-gap: 32px; font: 400 13px/1.5 var(--mono); }
.toc .s { break-inside: avoid; margin: 0 0 14px; }
.toc b { display: block; font-weight: 500; color: var(--ink); text-transform: lowercase; letter-spacing: .04em; }
.toc a { display: block; color: var(--soft); text-decoration: none; text-transform: lowercase; }
.toc a:hover { color: var(--ink); }
.toc a span { display: inline-block; width: 2.4em; color: var(--ink); }

kbd { font: 500 11.5px/1 var(--mono); letter-spacing: .04em; padding: 3px 5px 2px; border: 1px solid var(--ink);
  border-radius: 3px; white-space: nowrap; background: transparent; color: var(--ink); }

.scroll { overflow-x: auto; margin: 6px 0 18px; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; line-height: 1.45; }
th { text-align: left; font: 400 11.5px/1.3 var(--mono); letter-spacing: .06em; text-transform: lowercase; color: var(--soft);
  padding: 8px 14px 8px 0; border-bottom: 1px solid var(--ink); white-space: nowrap; }
td { padding: 9px 14px 9px 0; border-bottom: 1px solid var(--hair); vertical-align: top; }
td:first-child { white-space: nowrap; }
td:nth-child(n+3), th:nth-child(n+3) { font-family: var(--mono); font-size: 12.5px; }

figure { margin: 22px 0 22px; }
figcaption { margin-top: 10px; font: 400 12px/1.5 var(--mono); color: var(--soft); max-width: 60ch; }
.shot img { display: block; width: 240px; height: 240px; max-width: 100%; image-rendering: pixelated; border: 6px solid #000; background: #000; }
.grid .lane { display: flex; align-items: flex-end; gap: 3px; margin-bottom: 5px; }
.grid .name { width: 46px; font: 400 11px/14px var(--mono); letter-spacing: .04em; color: var(--soft); }
.grid .c { flex: 0 1 18px; height: 14px; background: var(--cell); }
.grid .c:nth-child(4n+2) { margin-left: 3px; }
.grid .c.on { background: var(--ink); }
.grid .c.acc { background: var(--ink); height: 22px; }
.grid .c.out { background: transparent; box-shadow: inset 0 -2px 0 var(--hair); }

footer { margin-top: 72px; padding-top: 14px; border-top: 1px solid var(--ink);
  font: 400 12px/1.6 var(--mono); letter-spacing: .04em; text-transform: lowercase; color: var(--soft); }
footer a { color: var(--ink); }
article[hidden] { display: none; }

@media (min-width: 760px) {
  .wrap { padding: 40px 32px 120px; }
  .cover { padding: 110px 0 72px; }
  .shot img { width: 300px; height: 300px; }
}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <span>ro:MINImal · @@DATE@@ · build @@COMMIT@@ · <a class="out" href="https://g0rst.github.io/ro-MINImal/">emulator, test page, download</a></span>
    <nav class="langs" aria-label="language">
      <a href="#en" data-l="en">english</a><a href="#de" data-l="de">deutsch</a><a href="#ro" data-l="ro">română</a>
    </nav>
  </div>
@@ARTICLES@@
  <footer>ro:MINImal · <a href="https://github.com/g0rst/ro-MINImal">github.com/g0rst/ro-MINImal</a></footer>
</div>
<script>
(function () {
  var langs = ["en", "de", "ro"];
  function pick() {
    var h = location.hash.replace("#", "").split("-")[0];
    if (langs.indexOf(h) >= 0) return h;
    var n = (navigator.language || "en").slice(0, 2).toLowerCase();
    return langs.indexOf(n) >= 0 ? n : "en";
  }
  function show() {
    var l = pick();
    langs.forEach(function (k) { document.getElementById("m-" + k).hidden = k !== l; });
    document.documentElement.lang = l;
    Array.prototype.forEach.call(document.querySelectorAll(".langs a"), function (a) {
      a.setAttribute("aria-current", a.getAttribute("data-l") === l ? "true" : "false");
    });
  }
  window.addEventListener("hashchange", function () {
    var lang = location.hash.indexOf("-") < 0;
    show();
    if (lang) window.scrollTo(0, 0);
  });
  show();
})();
</script>
</body>
</html>
"""

COVER = """<article id="m-{lang}" lang="{lang}"{hidden}>
  <header class="cover">
    <h1><span>ro:</span>MINI<span>mal</span></h1>
    <p class="what"><b>{title}</b> · {sub}</p>
    <div class="disc" aria-hidden="true">{disc}</div>
    <p class="what try"><a href="https://joakimeriksson.github.io/fm1-emu/?package=https%3A%2F%2Fg0rst.github.io%2Fro-MINImal%2Frominimal.fwsc&amp;name=ro%3AMINImal">▶ {emu}</a></p>
    <nav class="toc" aria-label="contents">{toc}</nav>
  </header>
{body}
</article>"""


def toc(lang):
    out, side = [], None
    for b in B:
        if b[0] != "h":
            continue
        if b[1] != side:
            if side:
                out.append("</div>")
            side = b[1]
            out.append(f'<div class="s"><b>{side} · {tx(SIDES[side], lang)}</b>')
        out.append(f'<a href="#{lang}-{b[1]}{b[2]}"><span>{b[1]}{b[2]}</span>{tx(b[3], lang)}</a>')
    return "".join(out) + "</div>"


def main():
    disc = "".join(f'<i class="{c}"></i>' for c in ["k", "", "", "", "k", "", "", "s", "k", "", "", "", "k", "", "", ""])
    arts = "\n".join(COVER.format(lang=l, hidden="" if l == "en" else " hidden", title=TITLE[l], sub=SUB[l], disc=disc,
                                  emu=EMU[l], toc=toc(l), body=render(l)) for l in LANGS)
    page = PAGE.replace("@@ARTICLES@@", arts).replace("@@DATE@@", F["date"]).replace("@@COMMIT@@", F["commit"])
    dest = ROOT / "docs" / "manual.html"
    dest.write_text(page, encoding="utf-8")
    words = {l: len(re.sub(r"<[^>]+>", " ", render(l)).split()) for l in LANGS}
    print(f"{dest}: {len(page)} bytes; words {words}")


if __name__ == "__main__":
    main()
