# ro:MINImal

Firmware für den **M-VAVE FM-1**: ein Groove-Synthesizer für Rominimal und Microhouse.
Sechs feste Stimmen, ein polymetrischer Step-Sequencer mit Chance pro Step, Swing, Drift und ein
Groove-Generator. Dazu Tempo-Delay, Reverb und Kick-Ducking.

![Display](docs/screen.png)

**Ohne Gerät ausprobieren:** https://g0rst.github.io/ro-MINImal/ (dort im FM-1-Emulator testen: das echte
Firmware-Paket in fm1-emu)

**Handbuch:** https://g0rst.github.io/ro-MINImal/manual.html, in Englisch, Deutsch und Rumänisch (Quelle:
`manual/build.py`).

**Im Browser testen:** `docs/index.html` öffnen. Die Seite enthält denselben C-Kern wie die Firmware
(als WebAssembly; online: https://g0rst.github.io/ro-MINImal/testseite.html) und bildet Display, Regler, Tasten und die 27 Keys des FM-1 in der Anordnung des Geräts nach.

K1 bis K4 heißen am Gerät KNOB1 bis KNOB4, ALGO und PRESET heißen ALGORITHM und PRESETS.

## Stand

| Teil | Zustand |
| --- | --- |
| Kern (`app/core/romi.c`): Klang, Sequencer, Generator, Display | läuft, Host-Tests grün (`tests/run_tests.sh`) |
| Browser-Testseite (`docs/index.html`) | läuft (WebAssembly aus demselben Kern) |
| FM-1-Anbindung (`app/app.c`) im Host-Simulator von fm1-base | läuft, Testskript `app/tests/basic.txt` grün (inkl. Speichern und Neustart) |
| Firmware-Paket `.fwsc` für das Gerät | wird bei jedem Push von GitHub Actions gebaut (Artefakt `firmware` im Lauf „build“, und auf der Projektseite); besteht die Prüfungen von fm1-base (Image 107 KB, RAM 42 von 96 KB) |
| Lauf auf einem echten FM-1 | **noch nicht getestet** |

Das Paket ist gebaut, aber nie auf einem Gerät gestartet. Offen bis zum ersten Lauf auf der Hardware: CPU-Last des Renderers, ob der Audio-Pfad aus dem RAM laufen
muss (`PLAT_RAM_CODE` in fm1-base), die Geschwindigkeit des Display-Neuzeichnens pro Step und der Klang über
Lautsprecher und Kopfhörer des Geräts.

**Vor dem Flashen lesen:** Custom-Firmware kann einen FM-1 unbrauchbar machen. Der Chip hat nur eine
Firmware-Bank und keinen Recovery-Taster; neuere Hardware-Revisionen (M-VAVE-Logo unter dem Display) vertragen
manche Custom-Firmwares nicht. Vorher auf die offizielle V15 gehen, Daten sichern und wissen, wie man
zurückkommt (Installer von fm1-base, `base/README.md`).

## Konzept

Rominimal und Microhouse leben von wenigen Elementen, die sich kaum merklich bewegen. Daraus folgt der Aufbau:

- **Die Kick ist das Raster.** Vier auf dem Boden, nichts sonst ist sicher.
- **Jede Spur hat ihre eigene Looplänge** (1 bis 16 Steps). Percussion und Clicks laufen auf 7, 9, 11 oder 13
  Steps gegen die 16 der Kick. Der Takt wiederholt sich dadurch erst nach vielen Takten.
- **Jeder Step hat eine Chance** (100, 75, 50, 25 %), einen Akzent, eine Note und einen Ratchet (bis zu vier
  Schläge im Step).
- **Swing** verschiebt jede zweite Sechzehntel (50 bis 75 %).
- **Drift** bewegt Klangfarbe, Ausklang, Lautstärke und Mikrotiming langsam und zufällig. Die Kick bleibt
  davon im Timing unberührt.
- **Der Generator** kennt die Rollen: Hats auf dem Offbeat, ein rollender Sub zwischen den Kicks, euklidische
  Percussion, seltene Akkord-Stabs, Clicks mit niedriger Chance. `SEL` würfelt eine Spur neu, `ARP` verändert
  sie um einen Schritt.
- **Sidechain pro Spur.** Eine Quelle (ab Werk die Kick) duckt jede Spur um deren eigenen Anteil, dazu Delay
  und Reverb. Ist die Quelle stumm, duckt sie weiter (Ghost-Kick).
- **Verknüpfte Spuren (LINK).** Die Steps einer Spur können davon abhängen, ob eine andere Spur an dieser
  Stelle tatsächlich geschlagen hat, mit ihrer Chance und ihrer eigenen Looplänge. Eine stumme Quelle wirkt
  weiter: ein unhörbares Euklid-Muster als Tor für andere Spuren.
- **Parameter-Locks und Mikrotiming.** Jeder Step kann eigene Klangwerte haben (bis zu 32 Locks pro Pattern) und
  bis zu 7/16 Step früher oder später kommen; die ganze Spur dazu noch einmal bis zu 8/16.

### Stimmen

| Spur | Synthese | K1 bis K4 auf der Seite EDIT |
| --- | --- | --- |
| KICK | Sinus mit Pitch-Hüllkurve, Click, Soft-Clipper | TUNE, DECAY, PUNCH, DRIVE |
| SUB | Sinus mit kurzem FM-Anschlag, Legato-Glide | DECAY, FM, RATIO, GLIDE |
| HAT | zwei unharmonische FM-Paare gegen Rauschen, Hochpass; Akzent öffnet | DECAY, TONE, METAL, OPEN |
| PERC | ein FM-Paar mit Pitch-Bend: Rim, Holz, Tom, Blip | DECAY, FM, RATIO, BEND |
| STAB | Dreiklang aus FM-Paaren, Tiefpass folgt der Hüllkurve | DECAY, BRIGHT, CHORD, DETUNE |
| CLICK | Rauschkorn durch resonanten Bandpass, zufällig im Stereofeld | DECAY, FREQ, RESO, SCATTER |

Effekte: Delay (1/16, 1/8, 3/16; links volle Zeit, rechts zwei Drittel), Reverb (vier Kämme, Allpässe),
Soft-Clipper in der Summe. 44,1 kHz, Blöcke zu 256 Frames.

## Bedienung

| Bedienelement | Funktion |
| --- | --- |
| PLAY | Start und Stopp |
| 16 weiße Tasten | die Steps der gewählten Spur; tippen schaltet um |
| weiße Taste halten + K1 / K2 / K3 / K4 | Note, Chance, Akzent, Ratchet (1 bis 4 Schläge) dieses Steps |
| weiße Taste halten + SELECT | Mikrotiming dieses Steps (bequemer auf der Seite TIMING) |
| auf Seite EDIT: weiße Taste halten + K1 bis K4 | Parameter-Lock: der Klangwert gilt nur für diesen Step |
| weiße Taste halten + SEL | Locks und Verschiebung dieses Steps löschen |
| schwarze Tasten 1 bis 6 | Spur wählen: KICK, SUB, HAT, PERC, STAB, CLICK |
| schwarze Tasten 7 bis 11 | Spur leeren, nach links, nach rechts, ganzer Groove neu, Undo |
| SELECT, OCT−, OCT+ | Spur wählen |
| ALGO | Looplänge der Spur |
| PRESET | Pattern A bis D (wechselt zum nächsten Takt) |
| HOME | Seite GROOVE: Tempo (90 bis 150), Swing, Drift, Duck |
| EDIT | Seite SOUND: die vier Klangparameter der Spur |
| ENV | Seite MIX: Pegel, Pan, Delay-Send, Reverb-Send |
| FX | Delay-Zeit, Feedback, Reverb-Größe, Dämpfung |
| FX ein zweites Mal | Seite SIDECHAIN: Quelle (Spur), Tiefe, Release, Anteil der gewählten Spur. Eine stumme Quelle duckt weiter. |
| GLO | Grundton, Skala (Moll, Dorisch, Phrygisch, Pentatonik), MIDI-Clock, Chain (Patterns A bis D nacheinander, je vier Takte) |
| SEL / ARP | Spur neu erzeugen / leicht verändern |
| SEQ ein drittes Mal | Seite TIMING: SELECT springt von Schlag zu Schlag, eine weiße Taste wählt einen Step direkt (ohne ihn umzuschalten). K1 schiebt den gewählten Schlag, K2 die ganze Spur, zusammen bis zu eine halbe Sechzehntel früher oder später |
| LFO | kurz: Spur stumm; halten: Solo |
| REC | Tasten spielen die Spur chromatisch; bei laufendem Groove werden die Noten aufgenommen |
| SEQ | zurück zu den Steps und Seite EUCLID: Schläge, Rotation, Chance, Akzent auf jedem n-ten Schlag |
| SEQ ein zweites Mal | Seite LINK: die Steps der Spur hängen von einer anderen Spur ab. Quelle und Modus: WITH (nur mit ihren Schlägen), GAPS (nur in ihren Lücken), AFTER (einen Step danach). K3 FOLLOW: die Töne der Spur folgen den Akkorden einer anderen Spur (ab Werk: SUB folgt STAB; OFF schaltet es ab) |
| SAVE | kurz: Projekt im Flash sichern. Geschrieben wird nur, was sich geändert hat: die Einstellungen und jedes Pattern liegen getrennt |
| SAVE halten + PRESETS | ganzes Pattern in ein anderes kopieren (A bis D); Loslassen kopiert |
| SAVE halten + SELECT | nur die gewählte Spur in ein anderes Pattern kopieren |
| MASTER | Lautstärke |

LEDs: gesetzte Steps leuchten, die Looplänge glimmt, der Playhead invertiert seinen Step.
MIDI: Kanäle 1 bis 6 spielen die Spuren (Note 60 ist der Grundton), Kanal 10 eine Drum-Map.
Start und Stopp werden empfangen; Clock, Start und Stopp werden über USB gesendet. USB ist nur MIDI: Die Firmware
meldet sich nicht als Audio-Interface.

### Speicher

Gespeichert wird in fünf Objekten: Einstellungen (24 Bytes) und jedes Pattern für sich (316 Bytes, mit 32 Locks
412 Bytes). Ein Step belegt dabei 2 Bytes, Locks stehen als Liste pro Pattern. Daraus folgen die Grenzen: höchstens
32 Locks pro Pattern (sonst „LOCKS FULL“), Verschiebung eines Steps ±7/16, Noten −32 bis +31 Halbtöne um den Grundton.
Ein beschädigtes Pattern lässt die anderen unberührt.

Die Objekte liegen im Flash bei `0xB1000–0xBAFFF`: auf dem FM-1 im Datenbereich von fm1-base, auf dem SMK-37 im
Fenster, das das Porting-Playbook für zusätzliche Objekte vorsieht. Keins berührt die Bereiche, die auf einem der
beiden Geräte geschützt sind (Bootloader, Bluetooth, Werkskalibrierung, Werksressourcen, Schlüssel). `app/app.c`
prüft das beim Übersetzen; ein Objekt außerhalb des erlaubten Fensters bricht den Build ab.

### SMK-37

Noch nicht unterstützt. `smk37-port.yaml` hält fest, was die Regeln des Porting-Playbooks
([genkigenki/fm1-to-smk37](https://github.com/genkigenki/fm1-to-smk37)) schon entscheiden, und listet die offenen
Bedienfragen. Ein Build für das SMK-37 bricht ab, solange es keine Board-Schicht gibt. Vor jeder Installation auf
einem SMK-37: vollständige Flash-Sicherung, wie im Playbook beschrieben.

## Aufbau

    app/core/romi.h, romi.c   der ganze Synthesizer: portables C99 ohne libc und ohne Plattform-Aufrufe
    app/app.c, app.h          Anbindung an fm1-base (Audio, MIDI, Panel, Display, Speicher)
    app/fm1.toml              Build-Einstellungen für fm1-base
    app/tests/basic.txt       Testskript für den Host-Simulator von fm1-base
    base/                     fm1-base als Submodul (darin felucca-bsp): Plattform, Build, Installer
    sim/                      Browser-Testseite: wasm.c, page.html, build.sh  ->  docs/index.html
    tests/                    Host-Tests des Kerns
    manual/                   Handbuch in drei Sprachen: build.py  ->  docs/manual.html

Der Kern zeichnet das Display selbst in Streifen von 240 x 48 Pixeln (eigene 5x7-Schrift). Deshalb zeigen
Gerät, Simulator und Browser dasselbe Bild.

## Bauen und testen

    git clone --recursive https://github.com/g0rst/ro-MINImal
    tests/run_tests.sh        # Kern-Tests (cc); schreibt build/tests/groove.wav und Bildschirmfotos
    sim/build.sh              # Browser-Testseite (clang mit wasm32-Target, wasm-ld, python3)
    ./build.sh --host         # Host-Simulator von fm1-base (python3, Pillow, cc)
    ./build.sh                # Firmware-Paket app/build/rominimal.fwsc (JieLi-Toolchain, AC79-SDK)

Ohne eigene Toolchain: Das Paket liegt auf der Projektseite (https://g0rst.github.io/ro-MINImal/rominimal.fwsc)
und als Artefakt `firmware` an jedem Lauf des Workflows `build` unter Actions
(`.github/workflows/build.yml`). JieLis SDK kommt dort von Gitee, das GitHub-Repository des SDK gibt es nicht
mehr (`SDK_URL=https://gitee.com/Jieli-Tech/fw-AC79_AIoT_SDK.git` für `get_sdk.sh`).

Toolchain und SDK für das Firmware-Paket beschreibt `base/README.md` (`base/tools/get_toolchain.sh`,
`base/bsp/tools/get_sdk.sh`). Installiert wird mit `base/tools/fm1_install.py`.

## Lizenz

MIT für die Dateien dieses Repositorys (`LICENSE`). `base/` (fm1-base, felucca-bsp) steht unter MPL-2.0;
ein Firmware-Paket enthält außerdem drei Dateien aus JieLis AC79-SDK (Apache-2.0).
Nicht mit M-VAVE oder JieLi verbunden.
