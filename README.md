# ro:MINImal

Firmware für den **M-VAVE FM-1**: ein Groove-Synthesizer für Rominimal und Microhouse.
Sechs feste Stimmen, ein polymetrischer Step-Sequencer mit Chance pro Step, Swing, Drift und ein
Groove-Generator. Dazu Tempo-Delay, Reverb und Kick-Ducking. Fünf Stile in einem Kern (ro:MINImal, suom1saundi, FRE3tek, schr4nz, p5ydub).

![Display](docs/screen.png)

**Ohne Gerät ausprobieren:** https://g0rst.github.io/ro-MINImal/ (dort im FM-1-Emulator testen: das echte
Firmware-Paket in fm1-emu)

**Handbuch:** https://g0rst.github.io/ro-MINImal/manual.html, in Englisch, Deutsch und Rumänisch (Quelle:
`manual/build.py`), mit Installation, Panel, Inhaltsverzeichnis und Werkseinstellungen direkt aus dem Code
(`manual/codefacts.py`). **suom1saundi** hat ein eigenes, absichtlich trashiges Handbuch auf Finnisch, Deutsch und Klingonisch
(UFOs, 8-Bit, Klamauk): https://g0rst.github.io/ro-MINImal/suomi.html (Quelle: `manual/suomi.py`); es nennt sich ehrlich
einen Versuch, kein Angebot, und verrät den Weg zwischen den Stilen nicht.

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

## Dritter Stil: FRE3tek (HOME 2 s halten)

**FRE3tek** ist Free Tekno: Acid, Mental, Tribe, 180 BPM, F phrygisch. **HOME 2 Sekunden halten** schaltet hinein
(Röhre zieht sich zusammen, eine Pixel-Boxenwand pumpt viermal im Takt, der Name knallt rein, die 3 in Dunkelrot, vier
Tekno-Kicks als Jingle); nochmal 2 s halten führt heim zu ro:MINImal. Ein kurzer Tipp auf HOME blättert
wie immer (jetzt beim Loslassen). Akzentfarbe Dunkelrot, Gute Nacht „DOBROU NOC“.

| Spur | Stimme | Regeln |
|---|---|---|
| KICK | TEK-KICK von memetek: Tonhöhe fällt exponentiell (×5 in 60 ms) auf die Tonart, hält ein Drittel der Fahne, tanh-Drive, hochpassgefilterter Klick | jede Viertel, gestimmt; manchmal ein Doppel vor dem Takt |
| ACID | 8-Bit-Bass von memetek: Rechteck, Puls, Säge, Dreieck oder Supersaw (SOUND 2 WAVE), TPT-Tiefpass mit schließender Hüllkurve, Dreieck eine Oktave tiefer, tanh | memeteks rollender Bass: Pause auf der Kick, Grundton auf den drei Sechzehnteln danach, Quinte und Oktave zum Taktende (beim Laden genau memeteks Muster, sonst eine von fünf Spielarten) |
| HAT | 808-Hats von memetek: sechs verstimmte Rechtecke und Rauschen, Bandpass 10 kHz, Hochpass 7,5 kHz; zwei Stimmen, eine geschlossene würgt die offene ab | offen auf jedem Offbeat, Ride mit 25/50 % |
| TRIBE | FM-Percussion von ro:MINImal als Toms, zwei Oktaven tiefer, wenig Bend | zwei Toms (Grundton tief, Quinte hoch), Euclid 5 oder 7 in 12/16 |
| SCREAM | Engine 8-BIT als Säge mit Vibrato | Melodie-Regeln der Engine |
| SIREN | Engine NOISE als Riser | Riser, Downlifter oder Zischen |

Klang: Kick, Bass und Hats sind von memetek portiert (`app/core/tek_voices.inc`, mit Erlaubnis des Autors), die Summe
läuft durch memeteks Master: tanh-Drive, Crusher (10 Bit, ein Drittel der Rate), Kompressor −10 dB 6:1 (3 ms Attack,
250 ms Release). Mischung wie bei memetek: der Bass trägt, die Hats stehen darüber. Alles liegt auf einem Akkord (die
SCREAM-Melodie bleibt auf den Tönen des Grundakkords), AIR fast aus, Duck 56 (der Bass rollt zwischen den Kicks). SIREN kommt stumm (SEL holt sie rein).
Ratchets auf den Hats: In C kommt ein echter Wirbel nur noch jedes vierte Mal (seine Ratchets mit 50 %), sonst nur ein
Doppel auf der letzten Sechzehntel mit 40 %; B verdoppelt nur noch manchmal einen Offbeat (mit 50 %); der Generator
setzt Doppelschläge auf Hats viel seltener. Gilt für alle Stile.
In allen drei Stilen steht der TUNE der Kick jetzt auf Halbtonschritten: eine Kick in der Tonart sitzt auf den Cent
genau (vorher bis zu einem Viertelton daneben, gemessen −18 Cent in FRE3tek).

Last im Simulator (schlimmster Fall): 2 057 Instruktionen pro Sample (ro:MINImal 1 914); mit GRAIN auf zwei
Spuren 2 598. Braucht den Teil von suom1saundi: ohne sie gebaut (ROMI_SUOMI=0) gibt es FRE3tek nicht. Eigenes
Handbuch im Flyer-Look, Deutsch und Englisch: https://g0rst.github.io/ro-MINImal/fre3tek.html (`manual/fre3tek.py`).

## Vierter Stil: schr4nz (in FRE3tek GLO 2 s halten)

**schr4nz** ist Schranz: harter deutscher Techno um 2000 (der Name stammt von Chris Liebing), 150 BPM, gerade, G-Moll,
fast keine Melodie, alles Percussion, komprimiert und verzerrt. Man kommt **nur aus FRE3tek** hin: dort **GLO 2 s
halten**. Show: Röhre zieht sich zusammen, gelb-schwarze Warnstreifen fahren ein, eine Gasmaske taucht aus dem Dunkel
auf und atmet im Takt (Gläser blitzen gelb, der Filter pufft), dann presst sich der Name herunter, die 4 in Gelb.
Jingle: Atemzug durch die Maske, vier verzerrte Kicks, ein gecrushter Schlag. In schr4nz: GLO 2 s zurück zu FRE3tek,
HOME 2 s heim zu ro:MINImal. Hintergrund Stahlgrau, Akzent Warngelb, Gute Nacht „GUTE NACHT“.

Wege zwischen den Stilen: ro:MINImal ⇄ suom1saundi (GLO), ro:MINImal → FRE3tek (HOME), FRE3tek ⇄ schr4nz (GLO),
FRE3tek und schr4nz → ro:MINImal (HOME), suom1saundi ⇄ p5ydub (HOME), p5ydub → ro:MINImal (GLO). suom1saundi lädt nur aus
ro:MINImal und p5ydub, schr4nz nur aus FRE3tek, p5ydub nur aus suom1saundi.

| Spur | Stimme | Regeln |
|---|---|---|
| KICK | TEK-KICK von memetek, kurz (0,3 s) und hart verzerrt (DRIVE 112) | jede Viertel, gestimmt; jedes vierte Mal ein Doppel auf Step 16 |
| RUMBLE | neue Stimme (`tek_voices.inc`) nach der klassischen Technik: die Kick kopiert ohne Attack (Sinus auf dem Ton der Kick, etwas Bend, eingeblendet: ATTACK auf SOUND 2), in einen Hall 100 % nass (drei Kammfilter und ein Allpass bei einem Viertel der Rate; SMEAR seine Länge, 0,2 bis 2 s), auf jeder Sechzehntel neu angestoßen, Tiefpass 40–450 Hz (TONE), Hochpass 30 Hz, Sättigung; darüber eine zweite Schicht, Bandpass über TONE und hart verzerrt, für Druck in den Mitten (GRIT); Duck 100 % von der Kick | pro Viertel die drei Sechzehntel nach der Kick (sonst eine von vier Figuren), Offbeat betont |
| HAT | 808-Hats von memetek | geschlossen auf den Sechzehnteln neben der Kick, offen auf dem Offbeat |
| METAL | FM-Percussion von ro:MINImal, Verhältnis 4,07 (Blech) | einer von vier Schranz-Loops (3-3-3-3-2-2, dagegen, dicht, 3-3-2 vom Offbeat), Grundton/Grundton/Quinte |
| CLAP | Engine NOISE als Clap, DRIVE 40 | 2 und 4 |
| ALARM | Engine 8-BIT als Rechteck mit Sirenen-Vibrato, stumm | Melodie auf den Akkordtönen |

Klang: die Summe durch memeteks Master wie in FRE3tek, aber Drive ×5 statt ×3,65 und Crusher 12 Bit bei halber Rate
(mahlt statt zu zischen). Duck 90, Release kurz: das Rumpeln pumpt. Last im Simulator (schlimmster Fall) 2 137
Instruktionen pro Sample (mit dem Hall des Rumble 2 198), mit GRAIN auf zwei Spuren etwa 2 730. Eigenes Handbuch im Stil eines Sicherheitsdatenblatts
(Stahl, Warnstreifen, Gasmaske), Deutsch und Englisch: https://g0rst.github.io/ro-MINImal/schr4nz.html
(`manual/schr4nz.py`).

## Fünfter Stil: p5ydub (in suom1saundi HOME 2 s halten)

**p5ydub** ist Psytrance und Dub: 100 BPM (Psydub liegt bei 70 bis 110), D phrygisch, die Pentatonik für Bass und Melodie, kleine Moll-Akkorde, die das
Delay zum Klang macht. Man kommt **nur aus suom1saundi** hin: dort **HOME 2 s halten** (in ro:MINImal führt HOME weiter
zu FRE3tek). Show: Röhre zieht sich zusammen, ein **Om** wird Strich für Strich in Erdtönen auf beigem Grund gezeichnet
(Sonne dahinter, Ringe, die im Takt atmen), der Name **p5ydub** (die 5 in Terrakotta) kommt, sein letztes B hallt nach.
Jingle: eine Klangschale mit Dub-Echo (punktierte Achtel) über einem runden Bassschlag. In p5ydub: HOME 2 s zurück zu
suom1saundi, GLO 2 s heim zu ro:MINImal. Hintergrund Sand, Akzent Terrakotta, Gute Nacht „SHANTI“.

| Spur | Stimme | Regeln |
|---|---|---|
| KICK | POTKU von suom1saundi, rund | vier auf den Boden, vor dem Takt manchmal ein Geist |
| DUB | BASSO als Dub-Bass: Cutoff 36, Decay 74, von der Kick nur sanft geduckt (Duck 90) | lange Wurzeltöne auf den Offbeats, ab und zu Terz, Quarte, Quinte oder kleine Septime, gleitend; eine von fünf Linien |
| HAT | HATTU | offen auf dem Offbeat, wenige geschlossene dazwischen; fast alles ins Delay |
| BUBBLE | HAPPO | eine Pentatonik-Phrase (Random Walk) auf eigener Länge 12, 14, 15 oder 16, sparsam |
| CHORD | Engine STAB, dunkel, Send 110, Hall 84 | Moll-Dreiklänge auf dem Offbeat (Regeln der Engine) |
| PING | Engine PIIP als Sinus-Glocke durch das Echo | Regeln der Engine |

Start: Delay punktierte Achtel mit Feedback 78 %, Hall 92 (Dämpfung 48), Swing 52, Drift 55, Duck 62. Die Theorie dahinter
(Pentatonik, ♭II, Delay-Sends, Federhall) steht aus Foren und Guides zusammengetragen im Handbuch
(`manual/p5ydub.py`, https://g0rst.github.io/ro-MINImal/p5ydub.html). Last im Simulator: in `tests/run_tests.sh`
(Stil p5ydub) geprüft, Klang 5 s mit Peak und RMS.

**Bildschirmschoner in allen Stilen:** mit 30 % Chance pumpt statt des Namens das Maskottchen des Stils mit der Kick:
bei p5ydub das Om, bei schr4nz die Gasmaske (die Gläser blitzen gelb), bei FRE3tek ein Lautsprecher, bei suom1saundi das
UFO, bei ro:MINImal ein Lautsprecher-Konus.

## Zwei Stile, zwei Firmwares: ro:MINImal und suom1saundi

Derselbe Kern kann zwei Stile: **ro:MINImal** (Rominimal, Microhouse) und **suom1saundi** (Suomisaundi, finnischer
Freestyle-Psytrance, aus [suom1saundi](https://github.com/g0rst/suom1saundi) übernommen). Umgeschaltet wird mit
**GLO 2 s halten**: Das Bild zieht sich zusammen wie bei einem alten Röhrenbildschirm und piept kurz,
die Musik blendet mit aus und endet in einem Schmatzer; während der Show läuft nur ihr eigener Ton. Zu suom1saundi
landet ein grünes 8-Bit-UFO in einem Wald in Graustufen, der Bildschirm zoomt darauf, es explodiert in den Schriftzug
(mit Jingle, 4 s); zurück zu ro:MINImal fliegt der Name groß auf einen cleanen schwarzen Bildschirm herein (2 s). Am Ende
blendet das Bild in ein paar Frames in die Seiten über, und die Musik startet mit dem neuen Groove von vorn. Ein Druck überspringt. Das Projekt bekommt die Grundwerte des Stils (Tempo, Tonart, Skala, Klänge) und einen
neuen Groove in ihm. Gebaut werden zwei Pakete aus demselben Code, jedes mit dem anderen als Bonus:

| Paket | startet als | Bonus |
|---|---|---|
| `rominimal.fwsc` (`app/`) | ro:MINImal, 126 BPM, F Moll | suom1saundi |
| `suom1saundi.fwsc` (`app_suomi/`) | suom1saundi, 145 BPM, F# phrygisch-dominant | ro:MINImal |

**Wichtig: Der Stil suom1saundi fliegt als Erstes raus, wenn der FM-1 zu wenig Rechenzeit hat.** Mit
`ROMI_SUOMI=0` (in `o2_cflags` von `fm1.toml`) ist ro:MINImal wieder genau wie vorher; oder suom1saundi wird eine
eigene Firmware. Die Stimmen und der Generator von suom1saundi liegen deshalb abgetrennt in
`app/core/suomi_voices.inc` und `app/core/suomi_gen.inc`.

Von suom1saundi übernommen: die sechs Stimmen (**POTKU** Psy-Kick mit Hold und Body, **BASSO** Filterbass,
**HATTU** Hats mit 8-Bit-Rauschkanal, **HAPPO** Acid-Linie, **PIIP** Soundchip-Melodie mit Arpeggio; statt der
FM-Zaps OUTO spielt die sechste Spur **KLIKKI**, die Clicks von ro:MINImal), ihre Generator-Regeln, die Skala phrygisch-dominant (dazu harmonisch Moll, beide jetzt auch für
ro:MINImal), Grün als Farbe. Alles andere ist ro:MINImal: Sequencer, Seiten, LAZY/HARD, die Spielarten B bis D,
Trig-Bedingungen, Slide und Glide, LINK, MOD, Bildschirmschoner.

| Spur | SOUND (K1–K4) | SOUND 2 (K1–K4) |
|---|---|---|
| POTKU | TUNE, DECAY, SWEEP, DRIVE | PITCH, CLICK, SNAP, CRUSH |
| BASSO | CUTOFF, RESO, ENVMOD, DECAY | PITCH, WAVE, DRIVE, CRUSH |
| HATTU | DECAY, TONE, METAL, OPEN | PITCH, CHIP, DRIVE, CRUSH |
| HAPPO | CUTOFF, RESO, ENVMOD, DECAY | PITCH, WAVE, DRIVE, CRUSH |
| PIIP (Engine, Spur 5 ab Start) | WAVE, DECAY, ARP, VIBRATO | PITCH, SPEED, DRIVE, CRUSH |
| KLIKKI (Engine CLICK, Spur 6 ab Start) | DECAY, FREQ, RESO, SCATTER | PITCH, ATTACK, DRIVE, CRUSH |

Die Spuren 5 und 6 wählen ihre Engine in beiden Stilen frei (HOME zweimal, Seite GROOVE 2): STAB, CLICK oder PIIP.
Der Generator für PIIP/8-BIT schreibt Melodien nach Lehrbuch: ein Takt als Frage und Antwort auf demselben Rhythmus,
die Antwort wiederholt das Motiv; meist Sekundschritte, auf den Schwerpunkten ein Ton des Akkords, den der Stab dort
spielt (ohne Stab i – VI – VII – i); die Frage endet offen auf der Quinte (oder Sekunde), die Antwort zu Hause auf dem
Grundton (oder der Terz). In ro:MINImal heißt PIIP **8-BIT**, der Click bei suom1saundi KLIKKI. Vierte Engine: **NOISE** (bei suom1saundi
SUHINA): Rauschen durch ein resonantes Filter, dessen Cutoff über eine Sechzehntel bis acht Takte nach oben oder unten
läuft (Riser, Downlifter, Zischen); SOUND LENGTH, SWEEP, TONE, RESO, SOUND 2 PITCH, SWELL, DRIVE, CRUSH.
TONE, SWEEP, RESO und SWELL wirken sofort auf den laufenden Sweep, LENGTH ab der nächsten Note.
LENGTH ganz links ist **CLAP**: drei Rauschstöße im Abstand von 9 ms und eine Fahne durch den Bandpass (TONE um 1,3 kHz,
RESO, SWEEP wird TAIL 60–500 ms). Neu gewählt kommt NOISE immer als Clap auf 2 und 4 (Steps 5 und 13); LENGTH auf
CLAP gedreht setzt die Steps ebenfalls dorthin.

**Regeln je Stimme (Spur 5 und 6)** – der Generator und die Patterns B bis D halten sich an die Engine:

| Engine | NEW | B | C | D |
|---|---|---|---|---|
| STAB | Akkorde aus der Tonart auf Offbeat-Figuren, Progression oder Motiv | Akkorde in anderer Reihenfolge | wie A | in die Nachbartonart |
| CLICK | verstreute Klicks, manchmal Stotterer | auf eigener Schleife gedreht, andere Frequenz | Doppel- und Dreifachklick am Taktende | wie A |
| 8-BIT | Melodie als Frage und Antwort auf Akkordtönen | wie A | wie A | in die Nachbartonart |
| NOISE als CLAP | immer 2 und 4, nie auf der Eins; dazu eine Figur: Vorschlag vor der 4, Geister-Clap am Taktende, Fill in Takt 4, Shuffle-Ghost | Geister-Clap am Ende kommt oder geht | Fill aus zwei Claps in den nächsten Takt | wie A |
| NOISE als Sweep | Riser in Takt 4, Downlifter aus Takt 1 oder Zischen auf den Offbeats; bleibt ein Sweep | wie A | wie A | wie A |

Die übrigen Regler der zweiten Seite von suom1saundi bleiben auf dessen Werten (POTKU HOLD 20, BODY 10; BASSO SUB 40;
HATTU SPREAD 20, CUT 50; HAPPO ACCENT 90; PIIP PWM 30). GLIDE von BASSO, HAPPO und PIIP
sitzt auf TIMING (KNOB3), SLIDE pro Step auf KNOB3 beim gehaltenen Step.

**Die Pattern-Regeln von suom1saundi:**
- **Kick:** vier auf dem Boden, gestimmt; manchmal ein Ghost vor dem Takt oder ein Doppelschlag auf der letzten Viertel.
- **Der pumpende Bass:** nie auf der Kick, sondern dahinter: meist der **Roll** (Kick, Bass, Bass, Bass), sonst der
  **Gallop** (Kick, –, Bass, Bass) und Mischformen. Grundton, die Oktave am Ende des Takts (oft mit Slide), die
  Sechzehntel nach der Kick leise, der Offbeat akzentuiert, kurzer Ausklang, voll von der Kick geduckt (AMOUNT 127):
  so pumpt er.
- **Acid (HAPPO):** eine Rhythmuszelle aus acht Steps und ein Motiv aus acht Tönen über dem Akkord, auf eigener
  Looplänge; große Sprünge gleiten.
- **Melodie (PIIP):** Frage und Antwort über dem Akkord, sie lässt Platz, wo die Acid-Linie spielt.
- **Hats:** der Offbeat, meist offen, dazu leise Sechzehntel.
- **Clicks (KLIKKI):** wie bei ro:MINImal, auf ungeraden Längen und mit geringer Chance.
- **Spielarten:** wie bei ro:MINImal; in B bleibt der Bass-Puls stehen, stattdessen antwortet ein Ton der letzten
  Viertel eine Oktave höher mit Slide.

Last: Der Stil suom1saundi braucht etwa 8 % mehr Rechenzeit (typisch 1 519 statt 1 398, schlimmster Fall 1 777 statt
1 646 Instruktionen pro Sample, geschätzt 35 bis 65 % des FM-1). Er macht die Firmware etwa 17 KB größer.

**Anzeige:** Mengen (Pegel, Sends, Drift, Duck, Tiefen, Drive, Crush, Resonanz, Mix, Random …) stehen in Prozent,
LFO- und ENV-Tiefen von −100 bis +100 %. Zeiten, Tonhöhen und Zählwerte behalten ihre Einheiten. Die Kick startet
in beiden Stilen bei Pegel 92 von 127 (72 %).

## Konzept

Rominimal und Microhouse leben von wenigen Elementen, die sich kaum merklich bewegen. Daraus folgt der Aufbau:

- **Ein Groove, vier Spielarten.** Pattern A ist der Groove; B, C und D werden immer aus A gemacht und ziehen
  nach, sobald sich A ändert: B spielt ihn variiert (gleiche Harmonie, anderer Beat), C mit Drum-Rolls zum Takt,
  D in einer verwandten Tonart. B lässt dabei ab und zu einen Kick-Schlag weg, C pausiert die Kick oft in den
  letzten vier Steps vor dem Takt. Setzt sie in C auf 13 bis 16 aus, wird mit Chance eins zu drei die Kick eine
  andere (Grundton oder Quinte, Ausklang, Sweep, Click, Drive) – ab D in allen Patterns gleich, auch in A, bis du
  sie von Hand änderst oder Cs Pause wieder würfelt. D behält sonst die Kick von A. Mit CHAIN EVOLVE entstehen nach jeder Runde A–D neue B, C und D: ein Set,
  das sich ständig weiterentwickelt.
- **Zwei Modi (GLO zweimal: GLOBAL 2).** **LAZY** ist das oben: B bis D entstehen von selbst, gespeichert werden
  nur A und die Einstellungen. **HARD**: B bis D sind beim ersten Umschalten Kopien von A und danach eigenständig;
  bearbeitet wird das Pattern, das gerade läuft, NEW erneuert dort Spur oder (halten) Pattern, alle vier werden
  gespeichert. Zurück in LAZY bleiben die HARD-Patterns beiseite und sind beim nächsten Wechsel wieder da.
- **PLAY (GLOBAL 2, KNOB2), in beiden Modi:** LOOP spielt das Pattern weiter (oder die CHAIN von GLOBAL),
  A-D spielt A, B, C, D je vier Takte und beginnt wieder bei A, RANDOM springt alle vier Takte zu einem anderen
  Pattern. CHAIN EVOLVE erneuert in LAZY dabei alle sechzehn Takte B bis D.
- **Die Kick ist das Raster.** Vier auf dem Boden in A und D, nichts sonst ist sicher.
- **Jede Spur hat ihre eigene Looplänge** (1 bis 16 Steps). Percussion und Clicks laufen auf 7, 9, 11 oder 13
  Steps gegen die 16 der Kick. Der Takt wiederholt sich dadurch erst nach vielen Takten.
- **Jeder Step hat eine Chance** (stufenlos 1 bis 100 %), einen Akzent, eine Note und einen Ratchet (bis zu vier
  Schläge im Step). Sub und Stab haben dazu **SLIDE** pro Step (gleitet ohne neuen Anschlag vom Ton davor) und
  **GLIDE** pro Spur (Seite TIMING, KNOB3: überlappende Töne gleiten). Jeder Step kann eine **Trig-Bedingung**
  haben (Step halten + ALGORITHM): 1:2 … 8:8, FILL / !FILL (ARP gehalten), PRE / !PRE, 1ST / !1ST.
- **Swing** verschiebt jede zweite Sechzehntel (50 bis 75 %).
- **Drift** bewegt Klangfarbe, Ausklang, Lautstärke und Mikrotiming langsam und zufällig. Die Kick bleibt
  davon im Timing unberührt.
- **Der Generator macht einen Groove, nicht sechs Würfel.** NEW erneuert nur die gewählte Spur,
  passend zu den anderen. NEW gehalten macht einen ganz neuen Groove: zuerst eine Dichte (sparsam, mittel, dicht;
  schnelle Tempi eher sparsam), dann die Spuren in einer Reihenfolge, in der jede sich auf die vorigen stützt: Die Kick ist das Raster und wird auf den Grundton gestimmt, der Stab bildet die Harmonie, der Sub rollt
  zwischen den Kicks und beginnt auf dem Grundton, die Hats sitzen auf dem Offbeat, die Percussion läuft in eigener
  Länge und so gedreht, dass sie die Kick möglichst meidet, alle Töne bleiben in der Skala. Auch die Klangfarbe von
  Hat, Percussion, Stab und Click ändert sich in passenden Grenzen; Pegel, Mix und das Fundament aus Kick und Sub
  bleiben. `ARP` verändert eine Spur um einen Schritt. UNDO nimmt alles zurück.
- **Sidechain pro Spur.** Eine Quelle (ab Werk die Kick) duckt jede Spur um deren eigenen Anteil, dazu Delay
  und Reverb. Ist die Quelle stumm, duckt sie weiter (Ghost-Kick).
- **Verknüpfte Spuren (LINK).** Die Steps einer Spur können davon abhängen, ob eine andere Spur an dieser
  Stelle tatsächlich geschlagen hat, mit ihrer Chance und ihrer eigenen Looplänge. Eine stumme Quelle wirkt
  weiter: ein unhörbares Euklid-Muster als Tor für andere Spuren.
- **Zwei Klangseiten pro Spur.** SOUND hat die vier Grundparameter der Stimme, SOUND 2 formt sie: Tonhöhe der
  ganzen Spur, Einsatz (Attack) oder die bisher festen Zeiten (Click und Pitch-Abfall der Kick, FM-Anschlag des
  Sub, Bend der Percussion), Sättigung und Bit-/Samplerate-Reduktion. Ohne Filter, deshalb günstig. Ab Werk klingt
  alles wie ohne SOUND 2.
- **Zwei LFOs pro Spur**, im Takt des Grooves, auf Klangparameter, Pegel, Pan oder Sends. Ohne Filter, deshalb
  kaum Rechenzeit: Klangparameter werden pro Schlag moduliert, Pegel, Pan und Sends einmal pro Audioblock.
- **Parameter-Locks und Mikrotiming.** Jeder Step kann eigene Klangwerte haben (bis zu 32 Locks pro Pattern) und
  bis zu 7/16 Step früher oder später kommen; die ganze Spur dazu noch einmal bis zu 8/16.

### Stimmen

| Spur | Synthese | K1 bis K4 auf der Seite EDIT |
| --- | --- | --- |
| KICK | Sinus mit Pitch-Hüllkurve, Click, Soft-Clipper | TUNE, DECAY, PUNCH, DRIVE |
| SUB | Sinus mit kurzem FM-Anschlag, Legato-Glide; eine Oktave über dem Grundton (F2, gut hörbar auch auf kleinen Boxen), SOUND 2 PITCH -12 für den tiefen Sub; ohne eigenen Bass-Boost (kein Drive, duckt voll): das Fundament regelt GROOVE 2 K4 BASS. Ohne Knackser: Legato-Noten setzen bei der laufenden Lautstärke an, der FM-Anschlag wird weich eingeblendet, ein sanfter Tiefpass (1,2 kHz) nimmt die Kanten, und der Sidechain greift in 2 ms statt sprunghaft | DECAY, FM, RATIO, GLIDE |
| HAT | zwei unharmonische FM-Paare gegen Rauschen, Hochpass; Akzent öffnet | DECAY, TONE, METAL, OPEN |
| PERC | ein FM-Paar mit Pitch-Bend: Rim, Holz, Tom, Blip | DECAY, FM, RATIO, BEND |
| STAB | Dreiklang aus FM-Paaren, Tiefpass folgt der Hüllkurve bis dahin, wo BRIGHT ihn hält (0,4 bis 2,2 kHz), etwas FM bleibt stehen (Obertöne, Präsenz); unter 140 Hz gefiltert (Platz für Sub und Kick); CHORD (TRIAD, 7TH, 9TH, SUS, 5TH) wird in der Tonart aus Skalenstufen geschichtet: auf III, VI, VII Dur, auf II vermindert, wie die Skala es hat (nur Töne außerhalb der Skala bekommen feste Moll-Formen) | DECAY, BRIGHT, CHORD, DETUNE |
| CLICK | Rauschkorn durch resonanten Bandpass, zufällig im Stereofeld | DECAY, FREQ, RESO, SCATTER |

Effekte: Delay (1/16, 1/8, 3/16; links volle Zeit, rechts zwei Drittel), Reverb (vier Kämme, Allpässe),
Soft-Clipper in der Summe. 44,1 kHz, Blöcke zu 256 Frames.

## Bedienung

| Bedienelement | Funktion |
| --- | --- |
| PLAY | Start und Stopp |
| 16 weiße Tasten | die Steps der gewählten Spur; tippen schaltet um |
| weiße Taste halten + K1 / K2 / K3 / K4 | Note, Chance (stufenlos, 1 % pro Raste), Akzent (bei SUB/STAB: OFF, ACC, SLIDE, ACC+SLIDE), Ratchet (1 bis 4 Schläge) dieses Steps |
| weiße Taste halten + SELECT | Mikrotiming dieses Steps (bequemer auf der Seite TIMING) |
| weiße Taste halten + ALGORITHM | Trig-Bedingung: 1:2 … 8:8 (Takt A von je B), FILL, !FILL, PRE, !PRE, 1ST, !1ST; eine Kerbe im Kästchen zeigt sie |
| auf Seite EDIT: weiße Taste halten + K1 bis K4 | Parameter-Lock: der Klangwert gilt nur für diesen Step |
| weiße Taste halten + SEL | Locks und Verschiebung dieses Steps löschen |
| schwarze Tasten 1 bis 6 | Spur wählen: KICK, SUB, HAT, PERC, STAB, CLICK |
| schwarze Tasten 7 bis 11 | Spur leeren, nach links, nach rechts, Spur neu (gehalten: ganzer Groove neu), Undo |
| SELECT, OCT−, OCT+ | Spur wählen |
| ALGO | Looplänge der Spur |
| PRESET | Pattern A bis D (wechselt zum nächsten Takt) |
| HOME | Seite GROOVE: Tempo (70 bis 200), Swing, Drift, Duck |
| SEL halten + weiße Taste 1 bis 4 | BEAT REPEAT der Summe: Viertel, Achtel, Sechzehntel, Zweiunddreißigstel, ab dem Moment, bis zum Loslassen |
| HOME ein zweites Mal | Seite GROOVE 2: K1 Engine von Spur 5, K2 Engine von Spur 6 (beide Stile): STAB (FM-Akkorde), CLICK (Rauschkörner, bei suom1saundi KLIKKI), 8-BIT (bei suom1saundi PIIP, Soundchip) oder NOISE (bei suom1saundi SUHINA: Rauschen, Riser, Downlifter); K3 FILTER der Summe (links Tiefpass, rechts Hochpass, Mitte aus), K4 BASS (Tiefen unter 100 Hz, bis etwa +9 dB); auch zweimal dasselbe. Neue Engine: ihr Klang und ein Pattern nach ihren Regeln, sie kommt **stumm** dazu (SEL holt sie rein), UNDO holt das alte zurück. Die Spur wechselt in allen vier Patterns (LAZY: B bis D folgen A; HARD + WORK LIVE: die Spur wird in die anderen drei übernommen; HARD + WORK PROD: nur im bearbeiteten Pattern, jede Spur kann je Pattern eine andere Engine spielen) |
| EDIT | Seite SOUND: die vier Klangparameter der Spur |
| EDIT ein zweites Mal | Seite SOUND 2: PITCH (±24 Halbtöne), dann je Spur CLICK (Kick), FM.TIME (Sub), B.TIME (Perc) oder ATTACK (Hat, Stab, Click), DRIVE (Kick: P.TIME), CRUSH. Lockbar pro Step, Ziel für LFOs |
| ENV | Seite MIX: Pegel, Pan, Delay-Send, Reverb-Send |
| ENV gehalten (0,6 s) | **Mixer** (alle Stile): sechs Kanäle mit Fader, Meter und Regler (K1 bis K4 die Spuren 1 bis 4, ALGO Spur 5, SELECT Spur 6; PRESET wechselt weiter das Pattern). Schwarze Tasten 1 bis 6: Spur sofort raus oder rein (beim Drücken, Klang samt Ausklang in 5 ms weg); länger als 0,25 s gehalten nur solange gehalten (Kill, Punch-in). Weiße Tasten 1 bis 6: Spur an die Gruppe (G); SEL halten + beliebiger Regler: die ganze Gruppe gleichmäßig; schwarze Taste 7: Gruppe raus/rein (gehalten: nur solange). ENV tippen: zurück zur Seite MIX; jede andere Seite schließt ihn auch |
| FX | Delay-Zeit, Feedback, Reverb-Größe, Dämpfung. **FX gehalten** (0,6 s): die Effekte zurück auf den Start des Stils (Delay, Reverb, Sidechain-Quelle und Release; Sidechain-Anteil, SLICE und SLICE LFO der gewählten Spur), Tempo und Tonart bleiben |
| FX ein zweites Mal | Seite SIDECHAIN: Quelle (Spur), Tiefe, Release, Anteil der gewählten Spur. Eine stumme Quelle duckt weiter. |
| FX ein viertes Mal | Seite SLICE LFO: der eigene LFO des Slicers, K1 RATE, K2 DEPTH, K3 TARGET (RATE, RANDOM, MIX), K4 SHAPE |
| FX ein drittes Mal | Seite SLICE (Hat, Perc, Stab, Click; nicht Kick und Sub): K1 MODE OFF, GATE (Raster 1/32 bis 1/128, an und aus), STUTTER (das erste Stück des Schlags immer wieder), GRAIN (Granular light: zwei Körner aus den letzten 186 ms der Spur); K2 RATE (Rastergröße, Stück- oder Korngröße), K3 RANDOM (Zufall: welche Stücke, rückwärts, Oktave, wo), K4 MIX. GRAIN auf höchstens zwei Spuren |
| GLO | Grundton, Skala (Moll, Dorisch, Phrygisch, Pentatonik, Phrygisch-dominant, Harmonisch Moll), MIDI-Clock, CHAIN (A-B, A-C, A-D nacheinander, je vier Takte; EVOLVE: A-D und danach neue B, C, D) |
| GLO gehalten (2 s) | wechselt den Stil ROMI ↔ SUOM1 (neuer Groove im Stil), mit Show: Röhrenbild zieht sich zusammen (Piep); zu suom1saundi UFO-Landung im 8-Bit-Wald, Zoom, Explosion in den Schriftzug, Jingle; zu ro:MINImal fliegt der Name herein. Ein Druck überspringt. GLO tippen wirkt beim Loslassen, kürzer gehalten: nichts |
| GLO ein zweites Mal | Seite GLOBAL 2: MODE LAZY (B bis D entstehen aus A) oder HARD (vier eigene Patterns); PLAY LOOP, A-D oder RANDOM; AIR (Höhen-Shelf der Summe über etwa 2,5 kHz, bis +6 dB, ab Werk 31 %: Präsenz und Luft); WORK LIVE (Engine-Wechsel in allen Patterns, schnell live) oder PROD (in HARD nur im bearbeiteten Pattern, zum Vorproduzieren) |
| SEL | kurz: Spur stumm; halten: Solo (beim Loslassen) |
| 2 min nichts berührt | Bildschirmschoner: nur der Name, grau; er pumpt sich bei jeder Kick kugelförmig aus der Mitte auf, pro Step leuchtet der nächste Buchstabe orange (immer nur einer); dahinter, gedimmt, leuchten die 16 × 6 Step-Punkte mit, was spielt; der Name wandert. Jede Berührung weckt ihn und wirkt zugleich |
| SEL halten + schwarze Tasten 1 bis 6 | jede Spur direkt stumm oder an, auch mehrere zugleich; die gewählte Spur bleibt |
| ARP | kurz: Spur leicht verändern; halten: FILL (Steps mit FILL spielen, mit !FILL schweigen) |
| SEQ ein drittes Mal | Seite TIMING: SELECT springt von Schlag zu Schlag, eine weiße Taste wählt einen Step direkt (ohne ihn umzuschalten). K1 schiebt den gewählten Schlag, K2 die ganze Spur, zusammen bis zu eine halbe Sechzehntel früher oder später; K3 GLIDE (SUB, STAB) |
| LFO gehalten (0,6 s) | der Klang der gewählten Spur zurück auf den Start: SOUND, SOUND 2, Mix, Sidechain-Anteil, Glide, beide LFOs, MOD, SLICE und SLICE LFO; Steps, Länge, Engine und Verknüpfungen bleiben; UNDO holt ihn zurück |
| LFO | Seite LFO 1 der Spur; nochmal: LFO 2. Je RATE (1/16 bis 16 Takte), DEPTH (±), TARGET (Klangparameter beider SOUND-Seiten, Pegel, Pan, Delay, Reverb), SHAPE (Sinus, Dreieck, Säge, Rechteck, Zufall) |
| LFO ein drittes Mal | Seite MOD: K1 RESTART (FREE oder eine Spur, deren Schläge die LFOs der Spur neu starten), K2 ENV SRC (die Lautstärke einer Spur als Modulation), K3 ENV DEPTH (±), K4 ENV TGT (dieselben Ziele wie ein LFO; Pegel, Pan, Sends fließend) |
| REC | Tasten spielen die Spur chromatisch; bei laufendem Groove werden die Noten aufgenommen |
| SEQ | zurück zu den Steps und Seite EUCLID: Schläge, Rotation, Chance (stufenlos, 1 bis 100 %), Akzent auf jedem n-ten Schlag oder RANDOM (etwa jeder dritte, zufällig, mindestens einer) |
| SEQ ein zweites Mal | Seite LINK: die Steps der Spur hängen von einer anderen Spur ab. Quelle und Modus: WITH (nur mit ihren Schlägen), GAPS (nur in ihren Lücken), AFTER (einen Step danach). K3 FOLLOW: die Töne der Spur folgen den Akkorden einer anderen Spur (ab Werk: SUB folgt STAB; OFF schaltet es ab). K4 ACCENT: akzentuierte Schläge einer anderen Spur akzentuieren diese Spur auf demselben Step |
| SAVE | Projekt im Flash sichern (Einstellungen und Pattern A; B bis D entstehen daraus) |
| SAVE 2 s gehalten | speichern und gute Nacht: Bild zieht sich zusammen (Röhre), Musik blendet mit aus, Schmatzer, „noapte bună“ (bei suom1saundi „hyvää yötä“); dann Bildschirm, Ton und Lichter aus, bis zum Ausschalten. Eine Berührung weckt (und tut sonst nichts). Die Firmware kann das FM-1 nicht selbst ausschalten |
| Einschalten | die Start-Show des Stils: ro:MINImal fliegt herein (rominimal.fwsc), bei suom1saundi.fwsc landet das UFO; danach Überblendung. Eine Berührung beendet sie und wirkt sofort |
| PRESETS | Pattern A bis D, im Lauf zum nächsten Takt. Bearbeitet wird immer A, auch wenn B, C oder D läuft |
| NEW auf B, C oder D | diese Spielart neu würfeln; A bleibt |
| MASTER | Lautstärke |

LEDs: gesetzte Steps leuchten, die Looplänge glimmt, der Playhead invertiert seinen Step.
MIDI: Kanäle 1 bis 6 spielen die Spuren (Note 60 ist der Grundton), Kanal 10 eine Drum-Map.
Start und Stopp werden empfangen; Clock, Start und Stopp werden über USB gesendet. USB ist nur MIDI: Die Firmware
meldet sich nicht als Audio-Interface.

### Speicher und Last (berechnet, nicht am Gerät gemessen)

| | belegt | verfügbar | Anteil |
|---|---|---|---|
| Firmware-Image (Flash) | 165 100 B | 581 564 B (App-Slot) | 28 % |
| RAM .data + .bss | 42 348 B | 98 304 B | 43 % |
| RAM-Pool (Delay, Reverb, Beat Repeat, GRAIN, fm1-base) | 302 276 B | 344 064 B | 88 % |
| RAM-Code (.ram_text) | 5 100 B | 32 768 B | 16 % |
| Speicherfenster 0xB1000–0xBAFFF | höchstens 3 149 B (Einstellungen 37 B, A–D je bis 778 B) | 40 960 B | 8 % |

Last des Renderers: Instruktionen pro Sample mit callgrind gezählt (x86-64, -O2, wie der Core gebaut wird), auf
den AC79 (Kern r3, 360 MHz, Single-Precision-FPU) umgerechnet mit Faktor 1,6 bis 3,0 (mehr Instruktionen auf
einem RISC-Kern, Takte pro Instruktion, Cache-Misses beim Ausführen aus dem Flash). Budget: 8 163 Takte pro Sample.

| Fall | Instr./Sample | Last (1,6 / 2,2 / 3,0) |
|---|---|---|
| alle Spuren stumm (Delay, Reverb, Mix, Sequencer, LFOs) | 995 | 20 / 27 / 37 % |
| typischer Groove (Stand Nov. 2026: Stab mit stehender FM, AIR an) | 1 567 | 31 / 42 / 58 % |
| schlimmster Fall: jeder Step, Ratchet x4, Drive und Crush, LFOs, volle Sends, alle Verknüpfungen, FILTER, BASS, AIR (mit den geglätteten Mutes des Mixers) | 1 914 | 38 / 52 / 70 % |
| dazu alle Verknüpfungen (ACCENT, RESTART, ENV auf Pegel/Klang, Bedingungen) | 1 638 | 32 / 44 / 60 % |
| suom1saundi, schlimmster Fall | 1 750 | 34 / 47 / 64 % |
| suom1saundi, schlimmster Fall, dazu SLICE: GATE, STUTTER und GRAIN auf zwei Spuren | 2 230 (geschätzt heute ~2 420) | 44 / 60 / 82 % (heute ~47 / 65 / 89 %) |
| FRE3tek (memeteks Stimmen und Master), schlimmster Fall | 2 057 | 40 / 55 / 76 % |
| FRE3tek, schlimmster Fall, dazu GRAIN auf zwei Spuren | 2 598 | 51 / 70 / 95 % |
| schr4nz, schlimmster Fall | 2 198 | 43 / 59 / 81 % |
| schr4nz, schlimmster Fall, dazu GRAIN auf zwei Spuren | ~2 730 | 54 / 74 / 100 % |

SLICE: GATE kostet fast nichts, STUTTER wenig, GRAIN etwa 170 Instruktionen pro Sample und Spur. Deshalb höchstens
zwei Spuren mit GRAIN, und GRAIN ist nach suom1saundi das Erste, was rausfliegt, wenn es am Gerät eng wird.
Die Verknüpfungen kosten fast nichts: ACCENT und Bedingungen werden einmal pro Step entschieden, RESTART ist eine
Zahl pro Step, ENV liest die Hüllkurve, die die Stimme ohnehin hat; nur ein ENV auf Pegel, Pan oder Sends rampt
seine vier Mixwerte pro Sample (höchstens etwa 25 Instruktionen).
Anteile der Stimmen im schlimmsten Fall: Stab 207, Hat 173, Sub 93, Perc 87, Kick 58, Click 40 Instr./Sample. Die
Oberfläche (Zeichnen, Byte-Tausch der Streifen) kostet geschätzt 2 bis 4 %. Reserven, falls es eng wird: der zweite
Kern (fm1-base `cpu2`, z. B. Reverb oder die Hälfte der Stimmen), `cpu_clock = 396`, mehr Render-Code im RAM.
Der Bildschirmschoner (nach 2 min ohne Berührung) zeichnet 30 Bilder pro Sekunde: geschätzt 3 bis 5 % der CPU samt
Byte-Tausch, im Hauptprogramm, nicht im Audio-Pfad.
Der echte Wert kommt am Gerät aus `plat_cpu_pct`.

### Speicher

Gespeichert werden im LAZY-Modus zwei Objekte: die Einstellungen (32 Bytes, darin die Würfel für B bis D, MODE
und PLAY) und Pattern A (682 Bytes, mit 32 Locks 778 Bytes); im HARD-Modus dazu B, C und D. Ein Step belegt 4 Bytes
(Chance und Trig-Bedingung), Slide, Glide und die Verknüpfungen 8 Bytes pro Spur. Patterns der Versionen 13 und 14 werden weiter
geladen (ohne Slide, die Chance in vier Stufen übernommen). Locks stehen als Liste pro Pattern. Daraus folgen die Grenzen: höchstens
32 Locks pro Pattern (sonst „LOCKS FULL“), Verschiebung eines Steps ±7/16, Noten −32 bis +31 Halbtöne um den Grundton.
Ein beschädigtes Objekt lässt das andere unberührt.

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
    app/core/suomi_*.inc      der Stil suom1saundi (Stimmen, Generator): fällt mit ROMI_SUOMI=0 weg
    app/fm1.toml              Build-Einstellungen für fm1-base
    app_suomi/                dieselbe Firmware als suom1saundi (startet im Stil SUOMI): fm1.toml, app.h, Testskript
    app/tests/basic.txt       Testskript für den Host-Simulator von fm1-base
    base/                     fm1-base als Submodul (darin felucca-bsp): Plattform, Build, Installer
    sim/                      Browser-Testseite: wasm.c, page.html, build.sh  ->  docs/index.html
    tests/                    Host-Tests des Kerns
    manual/                   Handbücher: build.py -> docs/manual.html (en/de/ro), suomi.py -> docs/suomi.html (fi/de/tlh, Text: suomi_text.py), fre3tek.py -> docs/fre3tek.html, schr4nz.py -> docs/schr4nz.html (de/en), codefacts.py (Werte aus dem Code)

Der Kern zeichnet das Display selbst in Streifen von 240 x 48 Pixeln (eigene 5x7-Schrift). Deshalb zeigen
Gerät, Simulator und Browser dasselbe Bild.

## Bauen und testen

    git clone --recursive https://github.com/g0rst/ro-MINImal
    tests/run_tests.sh        # Kern-Tests (cc); schreibt build/tests/groove.wav und Bildschirmfotos
    sim/build.sh              # Browser-Testseite (clang mit wasm32-Target, wasm-ld, python3)
    ./build.sh --host         # Host-Simulator von fm1-base (python3, Pillow, cc)
    ./build.sh                # Firmware-Paket app/build/rominimal.fwsc (JieLi-Toolchain, AC79-SDK)
    python3 base/tools/build.py app_suomi          # dasselbe als app_suomi/build/suom1saundi.fwsc
    python3 base/tools/build.py app_suomi --host   # dessen Host-Simulator (tests/run_tests.sh führt ihn mit aus)

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
