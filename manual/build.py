#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Builds the ro:MINImal manual: one self-contained page in English, German and Romanian.

    python3 manual/build.py        ->  docs/manual.html

The text lives here, once per language, block by block, so the three versions cannot drift apart in structure.
[[NAME]] marks a control as printed on the FM-1. The screens are the firmware's own (tests/run_tests.sh writes
them; manual/screen-*.png are copies).
"""
import base64
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("en", "de", "ro")


def T(en, de, ro):
    return {"en": en, "de": de, "ro": ro}


SAME = lambda s: {"en": s, "de": s, "ro": s}  # noqa: E731

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

h("a", 3, T("the first minute", "die erste minute", "primul minut"))
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

h("a", 4, T("the panel", "das panel", "panoul"))
table(T(["control", "what it does"], ["bedienelement", "funktion"], ["control", "ce face"]),
      ("[[MASTER]]", T("volume", "Lautstärke", "volum")),
      ("[[SELECT]]", T("selects the track; on the TIMING page it steps from hit to hit",
                       "wählt die Spur; auf der Seite TIMING springt es von Schlag zu Schlag",
                       "alege pista; pe pagina TIMING sare de la o lovitură la alta")),
      ("[[PRESETS]]", T("pattern A to D", "Pattern A bis D", "pattern-ul A până la D")),
      ("[[ALGORITHM]]", T("loop length of the track, 1 to 16 steps", "Looplänge der Spur, 1 bis 16 Steps",
                          "lungimea buclei pistei, 1 până la 16 pași")),
      ("[[KNOB1]] – [[KNOB4]]", T("the four values shown on the screen", "die vier Werte im Display",
                                  "cele patru valori de pe ecran")),
      ("[[OCT−]] [[OCT+]]", T("previous and next track; in keys mode the octave",
                              "vorige und nächste Spur; im Tastenmodus die Oktave",
                              "pista anterioară și următoare; în modul clape, octava")),
      ("[[HOME]]", T("page GROOVE", "Seite GROOVE", "pagina GROOVE")),
      ("[[EDIT]]", T("page SOUND of the track", "Seite SOUND der Spur", "pagina SOUND a pistei")),
      ("[[ENV]]", T("page MIX of the track", "Seite MIX der Spur", "pagina MIX a pistei")),
      ("[[FX]]", T("page FX; pressed again: SIDECHAIN", "Seite FX; nochmal gedrückt: SIDECHAIN",
                   "pagina FX; apăsat din nou: SIDECHAIN")),
      ("[[GLO]]", T("page GLOBAL", "Seite GLOBAL", "pagina GLOBAL")),
      ("[[SEQ]]", T("back to the steps; pages EUCLID, LINK, TIMING in turn",
                    "zurück zu den Steps; Seiten EUCLID, LINK, TIMING der Reihe nach",
                    "înapoi la pași; paginile EUCLID, LINK, TIMING pe rând")),
      ("[[SEL]]", T("tap: mute the track. Hold: solo", "kurz: Spur stumm. Halten: Solo",
                    "scurt: pista pe mut. Ținut: solo")),
      ("[[ARP]]", T("mutate: one small change", "Mutate: eine kleine Änderung", "mutate: o schimbare mică")),
      ("[[LFO]]", T("page LFO 1 of the track; pressed again: LFO 2", "Seite LFO 1 der Spur; nochmal: LFO 2",
                    "pagina LFO 1 a pistei; apăsat din nou: LFO 2")),
      ("[[REC]]", T("keys mode: the keys play the track", "Tastenmodus: die Tasten spielen die Spur",
                    "modul clape: clapele cântă pista")),
      ("[[SAVE]]", T("tap: save. Hold: copy", "kurz: speichern. Halten: kopieren", "scurt: salvează. Ținut: copiază")),
      ("[[PLAY STOP]]", T("start and stop", "Start und Stopp", "pornire și oprire")),
      (T("16 white keys", "16 weiße Tasten", "16 clape albe"),
       T("the steps of the selected track", "die Steps der gewählten Spur", "pașii pistei selectate")),
      (T("black keys 1 – 6", "schwarze Tasten 1 – 6", "clapele negre 1 – 6"),
       SAME("KICK, SUB, HAT, PERC, STAB, CLICK")),
      (T("black keys 7 – 11", "schwarze Tasten 7 – 11", "clapele negre 7 – 11"),
       T("clear the track, shift it left, shift it right, the track new (held: the whole groove), undo",
         "Spur leeren, nach links schieben, nach rechts schieben, Spur neu (gehalten: ganzer Groove), Undo",
         "golește pista, mut-o la stânga, mut-o la dreapta, pista nouă (ținut: tot groove-ul), undo")))

h("a", 5, T("the screen", "das display", "ecranul"))
img("groove", T("Six lanes, one per track. The selected track is marked white.",
                "Sechs Zeilen, eine pro Spur. Die gewählte Spur ist weiß markiert.",
                "Șase rânduri, câte unul pe pistă. Pista selectată este marcată cu alb."))
ul(T("A filled cell is a step that plays. A tall cell has an accent.",
     "Ein gefülltes Kästchen ist ein Step, der spielt. Ein hohes Kästchen hat einen Akzent.",
     "O celulă plină este un pas care cântă. O celulă înaltă are accent."),
   T("The darker the cell, the lower its chance: 100, 75, 50, 25 %.",
     "Je dunkler das Kästchen, desto geringer die Chance: 100, 75, 50, 25 %.",
     "Cu cât celula e mai închisă, cu atât șansa e mai mică: 100, 75, 50, 25 %."),
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
      ("SUB", T("sine with a short FM attack; notes glide", "Sinus mit kurzem FM-Anschlag; Noten gleiten",
                "sinus cu un atac FM scurt; notele alunecă"), "DECAY", "FM", "RATIO", "GLIDE"),
      ("HAT", T("metallic FM against noise; an accent opens it", "metallisches FM gegen Rauschen; ein Akzent öffnet",
                "FM metalic contra zgomot; accentul îl deschide"), "DECAY", "TONE", "METAL", "OPEN"),
      ("PERC", T("one FM pair with a pitch bend: rim, wood, tom, blip",
                 "ein FM-Paar mit Pitch-Bend: Rim, Holz, Tom, Blip",
                 "o pereche FM cu pitch bend: rim, lemn, tom, blip"), "DECAY", "FM", "RATIO", "BEND"),
      ("STAB", T("a three-note chord through a closing filter", "ein Dreiklang durch ein schließendes Filter",
                 "un acord de trei note printr-un filtru care se închide"), "DECAY", "BRIGHT", "CHORD", "DETUNE"),
      ("CLICK", T("a grain of noise through a resonant filter, somewhere in the stereo field",
                  "ein Rauschkorn durch ein Resonanzfilter, irgendwo im Stereofeld",
                  "un grăunte de zgomot printr-un filtru rezonant, undeva în câmpul stereo"),
       "DECAY", "FREQ", "RESO", "SCATTER"))

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
       T("chance: 100, 75, 50, 25 %", "Chance: 100, 75, 50, 25 %", "șansa: 100, 75, 50, 25 %")),
      (T("turn [[KNOB3]]", "[[KNOB3]] drehen", "rotește [[KNOB3]]"),
       T("accent on or off", "Akzent an oder aus", "accent pornit sau oprit")),
      (T("turn [[KNOB4]]", "[[KNOB4]] drehen", "rotește [[KNOB4]]"),
       T("ratchet: 1 to 4 hits in the step", "Ratchet: 1 bis 4 Schläge im Step", "ratchet: 1 până la 4 lovituri în pas")),
      (T("turn [[SELECT]]", "[[SELECT]] drehen", "rotește [[SELECT]]"),
       T("the step plays earlier or later", "der Step spielt früher oder später", "pasul cântă mai devreme sau mai târziu")),
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
    "range; zero is off. TARGET is one of the track's four sound parameters, or LEVEL, PAN, DELAY, REVERB. SHAPE: "
    "SINE, TRI, SAW, SQR, or RAND (a new value each cycle). Both LFOs may move the same value. The sound parameters "
    "take the LFO at each hit; level, pan and the sends follow it all the time. The LFOs start with the groove at "
    "PLAY and are kept with the pattern.",
    "Jede Spur hat zwei LFOs: langsame Wellen im Takt des Grooves. [[LFO]] öffnet den ersten, nochmal [[LFO]] den "
    "zweiten. RATE ist ein Durchlauf, von einer Sechzehntel bis sechzehn Takte. DEPTH bewegt den Wert in beide "
    "Richtungen, bis zur Hälfte seines Bereichs; null ist aus. TARGET ist einer der vier Klangparameter der Spur oder "
    "LEVEL, PAN, DELAY, REVERB. SHAPE: SINE, TRI, SAW, SQR oder RAND (ein neuer Wert pro Durchlauf). Beide LFOs "
    "dürfen denselben Wert bewegen. Klangparameter übernehmen den LFO bei jedem Schlag; Pegel, Pan und Sends folgen "
    "ihm ständig. Die LFOs starten mit dem Groove bei PLAY und werden mit dem Pattern gespeichert.",
    "Fiecare pistă are două LFO-uri: unde lente în ritmul groove-ului. [[LFO]] îl deschide pe primul, încă o dată "
    "[[LFO]] pe al doilea. RATE este un ciclu, de la o șaisprezecime la șaisprezece măsuri. DEPTH mută valoarea în "
    "ambele direcții, până la jumătate din domeniu; zero înseamnă oprit. TARGET este unul dintre cei patru parametri "
    "de sunet ai pistei sau LEVEL, PAN, DELAY, REVERB. SHAPE: SINE, TRI, SAW, SQR sau RAND (o valoare nouă la fiecare "
    "ciclu). Ambele LFO-uri pot mișca aceeași valoare. Parametrii de sunet preiau LFO-ul la fiecare lovitură; "
    "nivelul, pan-ul și send-urile îl urmează tot timpul. LFO-urile pornesc cu groove-ul la PLAY și se salvează cu "
    "pattern-ul."))

h("b", 5, T("pages", "seiten", "pagini"))
table(T(["button", "page", "KNOB1", "KNOB2", "KNOB3", "KNOB4"], ["taste", "seite", "KNOB1", "KNOB2", "KNOB3", "KNOB4"],
        ["buton", "pagină", "KNOB1", "KNOB2", "KNOB3", "KNOB4"]),
      ("[[HOME]]", "GROOVE", "TEMPO<br>90 – 150", "SWING<br>50 – 75 %", "DRIFT", "DUCK"),
      ("[[EDIT]]", "SOUND", T("see “six tracks”", "siehe „sechs spuren“", "vezi „șase piste”"), "", "", ""),
      ("[[ENV]]", "MIX", "LEVEL", "PAN", "DELAY", "REVERB"),
      ("[[FX]]", "FX", "D.TIME<br>1/16, 1/8, 3/16", "D.FDBK", "R.SIZE", "R.DAMP"),
      ("[[FX]] ×2", "SIDECHAIN", "SOURCE", "DEPTH", "RELEASE", "AMOUNT"),
      ("[[GLO]]", "GLOBAL", "ROOT<br>C1 – B2", "SCALE<br>MIN, DOR, PHR, PEN", "CLOCK", "CHAIN"),
      ("[[SEQ]]", "EUCLID", "HITS", "ROTATE", "CHANCE", "ACCENT"),
      ("[[SEQ]] ×2", "LINK", "SOURCE", "MODE", "FOLLOW", ""),
      ("[[SEQ]] ×3", "TIMING", "STEP", "TRACK", "", ""),
      ("[[LFO]]", "LFO 1", "RATE", "DEPTH", "TARGET", "SHAPE"),
      ("[[LFO]] ×2", "LFO 2", "RATE", "DEPTH", "TARGET", "SHAPE"))
p(T("DRIFT moves timbre, decay, level and timing slowly and at random. At zero the machine is exact. "
    "The kick's timing never drifts.",
    "DRIFT bewegt Klangfarbe, Ausklang, Lautstärke und Timing langsam und zufällig. Bei null ist die Maschine exakt. "
    "Das Timing der Kick driftet nie.",
    "DRIFT mișcă timbrul, decay-ul, nivelul și timingul încet și la întâmplare. La zero mașina este exactă. "
    "Timingul kick-ului nu se mișcă niciodată."))

# ------------------------------------------------------------------ side c ---
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
      ("[[KNOB3]] CHANCE", T("chance for all hits", "Chance für alle Schläge", "șansa pentru toate loviturile")),
      ("[[KNOB4]] ACCENT", T("accent on every hit, or every 2nd, 3rd, 4th",
                             "Akzent auf jedem Schlag oder jedem 2., 3., 4.",
                             "accent pe fiecare lovitură sau la fiecare a 2-a, a 3-a, a 4-a")))
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
ul(T("A project holds four patterns, A to D. [[PRESETS]] changes the pattern; while playing, at the next bar.",
     "Ein Projekt hält vier Patterns, A bis D. [[PRESETS]] wechselt das Pattern; im Lauf zum nächsten Takt.",
     "Un proiect ține patru pattern-uri, de la A la D. [[PRESETS]] schimbă pattern-ul; în timpul redării, la măsura următoare."),
   T("CHAIN on the GLOBAL page plays A-B, A-C or A-D in turn, four bars each.",
     "CHAIN auf der Seite GLOBAL spielt A-B, A-C oder A-D nacheinander, je vier Takte.",
     "CHAIN de pe pagina GLOBAL cântă A-B, A-C sau A-D pe rând, câte patru măsuri."),
   T("Copy a pattern: hold [[SAVE]], turn [[PRESETS]] to the target, let go.",
     "Pattern kopieren: [[SAVE]] halten, [[PRESETS]] zum Ziel drehen, loslassen.",
     "Copiază un pattern: ține [[SAVE]], rotește [[PRESETS]] până la țintă, eliberează."),
   T("Copy only the selected track: hold [[SAVE]], turn [[SELECT]] to the target pattern, let go.",
     "Nur die gewählte Spur kopieren: [[SAVE]] halten, [[SELECT]] zum Ziel-Pattern drehen, loslassen.",
     "Copiază doar pista selectată: ține [[SAVE]], rotește [[SELECT]] până la pattern-ul țintă, eliberează."),
   T("A tap on [[SAVE]] writes the changes to the device. The sound stops for a moment. Nothing is saved on its own.",
     "Ein kurzer Druck auf [[SAVE]] schreibt das Projekt ins Gerät. Der Ton setzt kurz aus. Nichts wird von selbst gespeichert.",
     "O apăsare scurtă pe [[SAVE]] scrie proiectul în aparat. Sunetul se oprește o clipă. Nimic nu se salvează singur."),
   T("UNDO, the last black key, takes back the last change to a pattern. Pressed again, it brings the change back. "
     "After a copy, press it in the target pattern.",
     "UNDO, die letzte schwarze Taste, nimmt die letzte Änderung an einem Pattern zurück. Nochmal gedrückt, holt "
     "es sie wieder. Nach einem Kopieren im Ziel-Pattern drücken.",
     "UNDO, ultima clapă neagră, anulează ultima schimbare a unui pattern. Apăsat din nou, o readuce. "
     "După o copiere, apasă-l în pattern-ul țintă."))

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
       T("Hold [[SAVE]], [[PRESETS]] to B, let go. In B press [[ARP]] on a few tracks. [[GLO]], CHAIN A-B. DRIFT near 60.",
         "[[SAVE]] halten, [[PRESETS]] auf B, loslassen. In B auf ein paar Spuren [[ARP]] drücken. [[GLO]], CHAIN A-B. DRIFT um 60.",
         "Ține [[SAVE]], [[PRESETS]] la B, eliberează. În B apasă [[ARP]] pe câteva piste. [[GLO]], CHAIN A-B. DRIFT în jur de 60.")))

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
            out.append(f'<h2><span class="no">{b[1]}{b[2]}</span>{tx(b[3], lang)}</h2>')
        elif k == "p":
            out.append(f"<p>{tx(b[1], lang)}</p>")
        elif k == "note":
            out.append(f'<p class="note">{tx(b[1], lang)}</p>')
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
    <span>ro:MINImal · @@DATE@@ · <a class="out" href="https://g0rst.github.io/ro-MINImal/">emulator, test page, download</a></span>
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
    var h = location.hash.replace("#", "");
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
  window.addEventListener("hashchange", function () { show(); window.scrollTo(0, 0); });
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
  </header>
{body}
</article>"""


def main():
    disc = "".join(f'<i class="{c}"></i>' for c in ["k", "", "", "", "k", "", "", "s", "k", "", "", "", "k", "", "", ""])
    arts = "\n".join(COVER.format(lang=l, hidden="" if l == "en" else " hidden", title=TITLE[l], sub=SUB[l], disc=disc, emu=EMU[l],
                                  body=render(l)) for l in LANGS)
    import datetime
    page = PAGE.replace("@@ARTICLES@@", arts).replace("@@DATE@@", datetime.date.today().strftime("%Y-%m"))
    dest = ROOT / "docs" / "manual.html"
    dest.write_text(page, encoding="utf-8")
    words = {l: len(re.sub(r"<[^>]+>", " ", render(l)).split()) for l in LANGS}
    print(f"{dest}: {len(page)} bytes; words {words}")


if __name__ == "__main__":
    main()
