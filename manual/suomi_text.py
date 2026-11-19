# SPDX-License-Identifier: MIT
"""The words of suom1saundi's manual (manual/suomi.py builds the page): Finnish, German, Klingon. Prose by hand; the
tables are made from the code. L(fi, de, tlh). Klingon is an approximation: technical words stay as printed."""


def L(fi, de, tlh):
    return {"fi": fi, "de": de, "tlh": tlh}


UI = {
    "ticker": L("★ SUOM1SAUNDI ★ UFO LASKEUTUI METSÄÄN ★ PSY-POTKU ★ HAPPO SIHISEE ★ 8-BITTIÄ ★ TÄMÄ ON KOKEILU, EI TUOTE ★ "
                "JOS FM-1 HIKOILEE, TÄMÄ LÄHTEE ENSIMMÄISENÄ ★ HYVÄÄ YÖTÄ ★ ÄLÄ SYÖ NAPPEJA ★ LEHMÄ ON YHÄ KADOKSISSA ★",
                "★ SUOM1SAUNDI ★ EIN UFO IST IM WALD GELANDET ★ PSY-KICK ★ DIE SÄURE ZISCHT ★ 8 BIT ★ DAS IST EIN VERSUCH, KEIN "
                "ANGEBOT ★ WENN DER FM-1 SCHWITZT, FLIEGT DAS ALS ERSTES RAUS ★ HYVÄÄ YÖTÄ ★ KNÖPFE NICHT ESSEN ★ DIE KUH IST "
                "IMMER NOCH WEG ★",
                "★ SUOM1SAUNDI ★ Sor Daq leng UFO ★ POTKU ★ HAPPO chuS ★ 8-BIT ★ ghot neH, Doch ngevlu'be' ★ FM-1 tlhuH ngaQDI', "
                "wa'DIch mej ★ maj ram ★ leQmey yISopQo' ★ tangqa' tu'be'lu' ★"),
    "tag": L("Kokeilu ro:MINImalin sisällä · ei tuote · build", "Ein Versuch in ro:MINImal · kein Angebot · Build",
             "ro:MINImal qoD ghot · Doch ngevlu'be' · build"),
    "pix": L("8-BIT · PSY · UFO", "8-BIT · PSY · UFO", "8-BIT · psy · UFO"),
    "new": L("UUSI!", "NEU!", "chu'!"),
    "emu": L("▶ PELAA EMULAATTORISSA", "▶ IM EMULATOR SPIELEN", "▶ emulator yIQujmoH"),
    "toc": L("SISÄLTÖ", "INHALT", "DotlhmeyDaj"),
    "home": L("projektisivu", "projektseite", "ghItlh tetlh"),
    "build": L("rakennettu koodista", "aus dem Code gebaut", "ngoqvo' chenmoHlu'"),
    "counter": L("kävijöitä", "Besucher", "Such ghotpu'"),
    "construct": L("TYÖMAA · TÄMÄ OHJE KIRJOITTAA ITSENSÄ UUDELLEEN JOKA KERTA · TYÖMAA",
                   "BAUSTELLE · DIESES HANDBUCH SCHREIBT SICH BEI JEDEM BUILD NEU · BAUSTELLE",
                   "Qu' 'oH · ghItlh'vam rap ghItlh'qa' · Qu' 'oH"),
    "th_track": L(["kosketin", "raita", "suomeksi", "tehtävä"], ["Taste", "Spur", "auf Finnisch", "Rolle"],
                  ["leQ", "He", "Suomi Hol", "Qu'"]),
    "black": L("musta", "schwarz", "qIj"),
    "th_knob": L(["nuppi", "nimi", "tehdas", "mitä se tekee"], ["Regler", "Name", "Werk", "was er tut"],
                 ["SeH", "pong", "ngo'", "nuq ta'"]),
    "mix_head": L("Miksaus tehtaalta", "Mix ab Werk", "ngo DuD"),
    "th_mix": L(["raita", "taso", "pan", "delay", "kaiku", "glide"], ["Spur", "Pegel", "Pan", "Delay", "Hall", "Glide"],
                ["He", "HoS", "pan", "delay", "reverb", "glide"]),
    "th_eng": L(["moottori", "SOUND", "SOUND 2", "taso"], ["Engine", "SOUND", "SOUND 2", "Pegel"], ["QuQ", "SOUND", "SOUND 2", "HoS"]),
    "th_page": L(["painike", "sivu", "mitä siellä on"], ["Taste", "Seite", "was dort liegt"], ["leQ", "Hotlh", "nuq tu'lu'"]),
    "th_ctl": L(["säädin", "mitä se tekee"], ["Element", "was es tut"], ["SeH", "nuq ta'"]),
    "pg_home": L("raitojen 5/6 moottori, FILTER, BASS", "Engine der Spuren 5/6, FILTER, BASS", "He 5/6 QuQ, FILTER, BASS"),
    "pg_glo": L("pohjasävel, asteikko, MIDI-kello, CHAIN · MODE, PLAY, AIR, WORK",
                "Grundton, Skala, MIDI-Clock, CHAIN · MODE, PLAY, AIR, WORK",
                "QoQ botlh, scale, clock, CHAIN · MODE, PLAY, AIR, WORK"),
}

ROLE = {   # track: (Finnish word, fi, de, tlh)
    0: ("potku", "psy-kick, neljä lattiaan, viritettynä sävellajiin", "Psy-Kick, vier auf den Boden, auf die Tonart gestimmt",
        "psy kick, loS rav Daq, key rur"),
    1: ("basso", "pumppaava suodinbasso kickin takana: rulla tai laukka", "pumpender Filterbass hinter der Kick: Roll oder Galopp",
        "bass pum, kick 'emDaq: roll pagh gallop"),
    2: ("hattu", "hatit ja shakerit offbeatilla, FM-metallia ja 8-bittistä kohinaa", "Hats und Shaker auf dem Offbeat, FM-Metall und 8-Bit-Rauschen",
        "hat, offbeat Daq: baS FM, 8-bit chuS"),
    3: ("happo", "acid-linja 303:n tapaan: aksentti ja slide omalla loopillaan", "Acid-Linie wie die 303: Akzent und Slide, eigene Looplänge",
        "acid tlhegh, 303 rur: accent, slide"),
    4: ("piip", "äänipiirin melodia: kysymys ja vastaus", "Soundchip-Melodie: Frage und Antwort", "wab chip bom: ghel, jang"),
    5: ("klikki", "pienet klikit parittomilla loopeilla", "kleine Klicks auf krummen Loops", "click mach, loop chImmey"),
}

# what each knob does, by track and name: (fi, de, tlh)
_P = ("koko raita ±24 puolisävelaskelta", "die ganze Spur ±24 Halbtöne", "He Hoch vIH, ±24")
_C = ("bittisyvyys ja näytetaajuus alas: 8-bittiä", "Bittiefe und Samplerate runter: 8 Bit", "bit mI' nup: 8-bit")
_D = ("särö", "Verzerrung", "HoS")
_DEC = ("kuinka kauan se soi", "wie lange es klingt", "wab tIq")
DESC = {
    "POTKU": {"TUNE": ("perussävel", "Grundton", "QoQ botlh"), "DECAY": _DEC,
              "SWEEP": ("kuinka korkealta sävel putoaa: psy-”tok”", "wie tief die Tonhöhe fällt: das Psy-„Tock“", "wab pum: psy 'tok'"),
              "DRIVE": ("kylläisyys, lämpimästä rikkinäiseen", "Sättigung, von warm bis kaputt", "HoS, jach"), "PITCH": _P,
              "CLICK": ("klikki alussa", "der Klick am Anfang", "wab tagh 'och"),
              "SNAP": ("kuinka nopeasti sweep putoaa", "wie schnell der Sweep fällt", "pum nom"), "CRUSH": _C},
    "BASSO": {"CUTOFF": ("alipäästön rajataajuus (18 dB)", "Grenzfrequenz des Tiefpasses (18 dB)", "tlhegh Hab: Dung bIng"),
              "RESO": ("resonanssi", "Resonanz", "jach"),
              "ENVMOD": ("kuinka paljon verhokäyrä avaa suodinta", "wie weit die Hüllkurve das Filter öffnet", "tlhegh poSmoH"),
              "DECAY": ("tason ja suotimen häive", "Ausklang von Pegel und Filter", "wab tIq"), "PITCH": _P,
              "WAVE": ("saha (0) … kantti (127)", "Säge (0) bis Rechteck (127)", "saw 0 .. square 127"),
              "DRIVE": ("särö ennen suodinta", "Verzerrung vor dem Filter", "HoS jach"), "CRUSH": _C},
    "HATTU": {"DECAY": _DEC, "TONE": ("metallin sävelkorkeus", "Tonhöhe des Metalls", "baS wab Dung bIng"),
              "METAL": ("kohina (0) … FM-metalli (127)", "Rauschen (0) bis FM-Metall (127)", "chuS 0 .. baS 127"),
              "OPEN": ("aksentti avaa: suljettu … auki", "der Akzent öffnet: zu bis offen", "accent poSmoH"), "PITCH": _P,
              "CHIP": ("äänipiirin 8-bittinen kohina mukaan", "das 8-Bit-Rauschen eines Soundchips dazu", "wab chip chuS"),
              "DRIVE": _D, "CRUSH": _C},
    "HAPPO": {"CUTOFF": ("rajataajuus: acid-linjan sydän", "Grenzfrequenz: das Herz der Acid-Linie", "tlhegh Hab: acid tIq"),
              "RESO": ("resonanssi, vihellyksen rajalle", "Resonanz, bis kurz vorm Pfeifen", "jach, wej SuS"),
              "ENVMOD": ("kuinka paljon verhokäyrä avaa", "wie weit die Hüllkurve öffnet", "tlhegh poSmoH"),
              "DECAY": ("häive; aksentti pidentää", "Ausklang; ein Akzent verlängert", "wab tIq"), "PITCH": _P,
              "WAVE": ("saha … kantti", "Säge bis Rechteck", "saw .. square"),
              "DRIVE": ("särö: 303 huutaa", "Verzerrung: die 303 schreit", "HoS: 303 jach"), "CRUSH": _C},
    "PIIP": {"WAVE": ("pulssi 12/25/50 %, 4-bittinen kolmio, saha, kohina", "Puls 12/25/50 %, 4-Bit-Dreieck, Säge, Rauschen",
                      "pulse, triangle, saw, chuS"),
             "DECAY": _DEC, "ARP": ("arpeggio: oktaavit, soinnut", "Arpeggio: Oktaven, Akkorde", "arpeggio"),
             "VIBRATO": ("vibrato", "Vibrato", "vibrato"), "PITCH": _P,
             "SPEED": ("arpeggion nopeus", "Tempo des Arpeggios", "arpeggio Do"), "DRIVE": _D, "CRUSH": _C},
    "KLIKKI": {"DECAY": _DEC, "FREQ": ("kaistanpäästön taajuus", "Frequenz des Bandpasses", "Hab Dung bIng"),
               "RESO": ("kuinka kapea", "wie schmal", "tlhop"), "SCATTER": ("kuinka laajalle stereoon", "wie weit ins Stereo", "stereo Daq ghomHa'"),
               "PITCH": _P, "ATTACK": ("isku: napsusta paisuntaan", "Anschlag: vom Knacks bis zum Anschwellen", "mup: nom .. QIt"),
               "DRIVE": _D, "CRUSH": _C},
}

PANEL = """  MASTER   SELECT     ┌──────────┐    KNOB1   KNOB2   KNOB3   KNOB4
                      │  NÄYTTÖ  │
  PRESETS  ALGORITHM  │   (UFO)  │    [FX]  [SEL] [ENV] [LFO] [EDIT] [GLO]
                      └──────────┘    [HOME][SAVE][ARP] [SEQ] [PLAY] [REC]
  [OCT-] [OCT+]

  ■ POTKU BASSO HATTU HAPPO 5 6 │ CLEAR ◀ ▶ NEW UNDO
  □ 1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16"""

CONTROLS = [
    ("MASTER", L("äänenvoimakkuus", "Lautstärke", "wab HoS")),
    ("SELECT", L("valitsee raidan; TIMING-sivulla iskusta iskuun", "wählt die Spur; auf TIMING von Schlag zu Schlag", "He wIv; TIMING: mup")),
    ("PRESETS", L("pattern A tai sen muunnelmat B–D", "Pattern A oder seine Spielarten B bis D", "pattern A, B – D")),
    ("ALGORITHM", L("raidan loopin pituus 1–16; pidetyllä askeleella trig-ehto", "Looplänge 1–16; mit gehaltenem Step die Bedingung",
                    "loop 'aD; mIw 'uchlu'DI': ra'ghom")),
    ("KNOB1–4", L("näytön neljä arvoa", "die vier Werte auf dem Display", "HaSta mI' loS")),
    ("HOME", L("GROOVE; uudelleen GROOVE 2", "GROOVE; nochmal GROOVE 2", "GROOVE; latlh: GROOVE 2")),
    ("EDIT", L("SOUND; uudelleen SOUND 2", "SOUND; nochmal SOUND 2", "SOUND; latlh: SOUND 2")),
    ("ENV", L("MIX: taso, pan, delay, kaiku; pito 0,6 s: MIKSERI – mustat 1–6 raita sisään/ulos (pito: vain pidettäessä), valkoiset 1–6 ryhmä, SEL + nuppi: ryhmä, musta 7: ryhmä sisään/ulos",
              "MIX: Pegel, Pan, Delay, Hall; 0,6 s halten: MIXER – schwarz 1–6 Spur rein/raus (gehalten: nur solange), weiß 1–6 Gruppe, SEL + Regler: die Gruppe, schwarz 7: Gruppe rein/raus",
              "MIX; 'uch: MIXER – QIj 1 – 6 He 'el/mej, chIS 1 – 6 ghom, SEL + loS: ghom, QIj 7: ghom 'el/mej")),
    ("FX", L("FX · SIDECHAIN · SLICE · SLICE LFO; pito: efektit alkuun", "FX · SIDECHAIN · SLICE · SLICE LFO; halten: Effekte auf Start",
             "FX · SIDECHAIN · SLICE · SLICE LFO; 'uch: bI'reS")),
    ("GLO", L("GLOBAL; uudelleen GLOBAL 2", "GLOBAL; nochmal GLOBAL 2", "GLOBAL; latlh: GLOBAL 2")),
    ("SEQ", L("askeleet; EUCLID, LINK, TIMING", "Steps; EUCLID, LINK, TIMING", "mIwmey; EUCLID, LINK, TIMING")),
    ("SEL", L("napautus: mykistä; pito: soolo; pito + valkoinen 1–4: beat repeat", "tippen: stumm; halten: Solo; halten + weiß 1–4: Beat Repeat",
              "yuv: tam; 'uch: wa'neH; 'uch + chIS 1 – 4: beat repeat")),
    ("ARP", L("napautus: mutaatio; pito: FILL", "tippen: Mutation; halten: FILL", "yuv: choH; 'uch: FILL")),
    ("LFO", L("LFO 1 · LFO 2 · MOD; pito: raidan ääni alkuun", "LFO 1 · LFO 2 · MOD; halten: Klang der Spur auf Start",
              "LFO 1 · LFO 2 · MOD; 'uch: wab bI'reS")),
    ("REC", L("koskettimet soittavat raitaa", "die Tasten spielen die Spur", "leQmey He QoQmoH")),
    ("SAVE", L("tallenna; pito 2 s: hyvää yötä", "speichern; 2 s halten: gute Nacht", "pol; cha' lup 'uch: maj ram")),
    ("PLAY", L("käynnistys ja pysäytys", "Start und Stopp", "bI'reS mev je")),
]

S = []


def sec(fi, de, tlh, *blocks):
    S.append((L(fi, de, tlh), blocks))


sec("Mikä tämä on?", "Was ist das?", "nuq 'oH?",
    ("p", L("<b>suom1saundi</b> on <b>kokeilu</b>, ei tuote. Se asuu ro:MINImal-firmwaren sisällä M-VAVE FM-1:ssä: sama kone, "
            "sama paneeli, mutta äänet ja säännöt tulevat suomisaundista, suomalaisesta freestyle-psytrancesta. Se on "
            "hyppivää, leikkisää ja hölmöä: pumppaava basso, sihisevä acid, äänipiirin piipitys ja ääniä, joita kukaan ei odota.",
            "<b>suom1saundi</b> ist ein <b>Versuch</b>, kein Angebot. Er wohnt in der Firmware ro:MINImal auf dem M-VAVE FM-1: "
            "dieselbe Maschine, dasselbe Panel, aber Klänge und Regeln kommen aus dem Suomisaundi, dem finnischen "
            "Freestyle-Psytrance. Das ist hüpfend, verspielt und albern: pumpender Bass, zischende Säure, Soundchip-Gepiepe "
            "und Geräusche, mit denen keiner rechnet.",
            "<b>suom1saundi</b> <b>ghot</b> 'oH, Doch ngevlu'bogh ghobe'. ro:MINImal firmware qoD, M-VAVE FM-1 Daq yIn: "
            "jan rap, SeHlaw rap, 'ach wabmey ra'mey je Suomi psytrance vo' ghoS. Sup, Quch, QIp: bass pum, acid chuS, "
            "wab chip, wab pIHbe'lu'bogh.")),
    ("p", L("Paketti <b>suom1saundi.fwsc</b> käynnistyy suom1saundina: {bpm} BPM, suora, {key} frygia-dominantti, ja UFO "
            "laskeutuu metsään. Kaikki emokoneen taidot pysyvät: sivut, LFO:t, euclid, linkit, SLICE, beat repeat, LAZY ja HARD. "
            "Väri on happovihreä.",
            "Das Paket <b>suom1saundi.fwsc</b> startet als suom1saundi: {bpm} BPM, gerade, {key} phrygisch-dominant, und ein "
            "UFO landet im Wald. Alles, was die Mutter-Firmware kann, bleibt: Seiten, LFOs, Euclid, Links, SLICE, Beat Repeat, "
            "LAZY und HARD. Die Farbe ist Säuregrün.",
            "<b>suom1saundi.fwsc</b> suom1saundi bI'reS: {bpm} BPM, {key} phrygian dominant, 'ej Sor Daq leng UFO. laH Hoch "
            "ratlh: Hotlhmey, LFO, euclid, muv, SLICE, beat repeat, LAZY HARD je. nguv: SuD acid.")),
    ("sticker", L("Kokeilu tarkoittaa: jos FM-1 hikoilee, suom1saundi lähtee ensimmäisenä. Se maksaa noin 8 % enemmän prosessoria.",
                  "Versuch heißt: Wenn der FM-1 ins Schwitzen kommt, fliegt suom1saundi als Erstes raus. Er kostet etwa 8 % mehr Rechenzeit.",
                  "ghot 'oH: FM-1 tlhuH ngaQDI', suom1saundi wa'DIch mej. 8 % latlh 'ar.")))

sec("Varoitus", "Warnung", "ghuHmoHghach",
    ("ul", [L("Tämä on toiminut vain simulaattorissa ja emulaattorissa. <b>Ei vielä testattu oikealla FM-1:llä.</b>",
              "Das lief bisher nur im Simulator und im Emulator. <b>Auf einem echten FM-1 noch nicht getestet.</b>",
              "simulator emulator je Daq neH Qap. <b>FM-1 teH Daq waHbe'lu'.</b>"),
            L("Oma firmware voi tehdä FM-1:stä tiiliskiven: piirillä on yksi firmware eikä palautusnappia.",
              "Custom-Firmware kann aus dem FM-1 einen Ziegelstein machen: Der Chip hält genau eine Firmware und hat keinen Recovery-Knopf.",
              "firmware chu' FM-1 Qaw'laH: wa' firmware neH, chu'qa'ghach leQ ghajbe'."),
            L("Tiedä tie takaisin M-VAVEn firmwareen ennen asennusta.", "Kenne den Weg zurück zur M-VAVE-Firmware, bevor du etwas installierst.",
              "Dalanpa', M-VAVE firmware Daq chegh mIw yISov.")]))

sec("Kokeile ja asenna", "Ausprobieren und installieren", "yIwaH, yIlan",
    ("p", L("<b>Ilman laitetta:</b> vaaleanpunainen nappi ylhäällä avaa suom1saundin FM-1-emulaattorissa selaimessa, samalla "
            "koodilla kuin laitteessa. Ensin ääni päälle, sitten PLAY. Puhelimella toimii hyvin.",
            "<b>Ohne Gerät:</b> Der pinke Knopf oben öffnet suom1saundi im FM-1-Emulator im Browser, mit demselben Code wie auf "
            "dem Gerät. Erst den Ton einschalten, dann PLAY. Auf dem Handy läuft das gut.",
            "<b>jan ghajbe'DI':</b> leQ Doq emulator poSmoH; jan ngoQ rap. wab yIchu', PLAY yIyuv.")),
    ("ol", [L("Lataa <b>suom1saundi.fwsc</b> projektisivulta; SHA256SUMS vieressä tarkistaa tiedoston.",
              "<b>suom1saundi.fwsc</b> von der Projektseite laden; SHA256SUMS daneben prüft die Datei.",
              "<b>suom1saundi.fwsc</b> yIlI' ghItlh tetlh vo'."),
            L("Asenna työkalulla, joka asentaa FM-1-firmwarepaketteja, esim. FM-1 Firmware Hub (fm1.designburgapps.com).",
              "Mit einem Werkzeug installieren, das FM-1-Firmware-Pakete installiert, etwa dem FM-1 Firmware Hub (fm1.designburgapps.com).",
              "FM-1 firmware jan yIlo' (FM-1 Firmware Hub)."),
            L("Kytke päälle: UFO laskeutuu harmaaseen pikselimetsään, kamera zoomaa, UFO räjähtää nimeksi. Kosketus ohittaa.",
              "Einschalten: Das UFO landet im grauen Pixelwald, die Kamera zoomt, es explodiert zum Namen. Ein Druck überspringt.",
              "yIchu': Sor qIjHom Daq leng UFO, Hop, jor, pong moj. leQ yIyuv: Sup.")]),
    ("note", L("Tie takaisin: M-VAVEn firmware FM-1 Firmware Hubin tai M-VAVEn päivitysohjelman kautta. Projektit asuvat omassa "
               "flash-osassaan.", "Der Weg zurück: die M-VAVE-Firmware über den FM-1 Firmware Hub oder M-VAVEs Updater. Projekte "
               "liegen in einem eigenen Teil des Flash.", "chegh: M-VAVE firmware, FM-1 Firmware Hub pagh M-VAVE updater.")))

sec("Ensimmäinen minuutti", "Die erste Minute", "wa'DIch tup",
    ("ol", [L("Paina <b>PLAY</b>. Groove soi; firmware tekee uuden joka käynnistyksellä.", "<b>PLAY</b> drücken. Ein Groove läuft; bei jedem Start ein neuer.",
              "<b>PLAY</b> yIyuv. groove Qap."),
            L("Vasemman reunan mustat koskettimet valitsevat raidan: POTKU, BASSO, HATTU, HAPPO, raidat 5 ja 6.",
              "Die schwarzen Tasten links wählen die Spur: POTKU, BASSO, HATTU, HAPPO, Spur 5 und 6.", "poS leQmey qIj He wIv."),
            L("16 valkoista kosketinta ovat raidan 16 askelta. Napauta: päälle tai pois.", "Die 16 weißen Tasten sind die 16 Steps. Tippen: an oder aus.",
              "leQmey chIS 16: mIwmey 16."),
            L("<b>NEW</b> (neljäs musta oikealta): raita uusiksi. Pidä puoli sekuntia: koko groove uusiksi.",
              "<b>NEW</b> (vierte schwarze von rechts): Spur neu. Eine halbe Sekunde halten: der ganze Groove neu.", "<b>NEW</b>: He chu'. 'uch: groove Hoch chu'."),
            L("<b>ARP</b>: yksi pieni mutaatio. <b>UNDO</b> (viimeinen musta): peru.", "<b>ARP</b>: eine kleine Mutation. <b>UNDO</b> (letzte schwarze): zurück.",
              "<b>ARP</b>: choH mach. <b>UNDO</b>: yIteq."),
            L("<b>HOME</b> ja nupit: TEMPO, SWING, DRIFT, DUCK.", "<b>HOME</b> und die Regler: TEMPO, SWING, DRIFT, DUCK.", "<b>HOME</b>: TEMPO, SWING, DRIFT, DUCK."),
            L("<b>SAVE</b>: tallenna. Pidä 2 sekuntia: tallenna ja <b>hyvää yötä</b>.", "<b>SAVE</b>: speichern. 2 Sekunden halten: speichern und <b>hyvää yötä</b>.",
              "<b>SAVE</b>: pol. cha' lup: <b>maj ram</b>.")]))

sec("Paneeli", "Das Panel", "SeHlaw", ("pre", PANEL), ("gen", "controls"))

sec("Näyttö", "Das Display", "HaSta",
    ("ul", [L("Kuusi kaistaa, yksi raitaa kohden; valittu raita on valkoinen.", "Sechs Bahnen, eine pro Spur; die gewählte ist weiß.", "jav tlhegh; wIvlu'bogh chIS."),
            L("Täysi ruutu soi, korkea ruutu on aksentti, tummempi ruutu harvemmin.", "Volles Kästchen spielt, hohes hat Akzent, dunkleres spielt seltener.",
              "'ay' teblu'bogh QoQ; woch: accent; Hurgh: Do' mach."),
            L("Viivoilla jaettu ruutu on ratchet; vihreä merkki on lukko; sivuun siirtynyt ruutu soi etu- tai jälkikäteen.",
              "Geteiltes Kästchen ist ein Ratchet; grüne Marke ein Lock; verschobenes spielt früher oder später.",
              "'ay' wavlu'bogh: ratchet; SuD ghItlh: lock; vIHlu'bogh: nom pagh tlhaw'."),
            L("Yliviivattu nimi on mykistetty; vihreä neliö nimen vieressä: raita on linkitetty.", "Durchgestrichener Name ist stumm; grünes Quadrat: verknüpft.",
              "pong wa'lu'pu'bogh: tam; SuD loS: muvlu'."),
            L("Vihreä ruudukossa on toistokohta; alarivi näyttää, mitä nupit kääntävät.", "Grün im Raster ist der Abspielpunkt; unten steht, was die Regler drehen.",
              "SuD: Qapbogh mIw; bIng: SeHmey.")]))

sec("Kuusi raitaa", "Sechs Spuren", "jav Hemey", ("gen", "tracks"))

sec("Äänet", "Klänge", "wabmey",
    ("p", L("<b>EDIT</b> avaa raidan SOUND-sivun, <b>EDIT</b> uudelleen SOUND 2:n (taulukoissa EDIT²). Taulukot tulevat suoraan "
            "firmwaren koodista: tehdasarvot 0–127, PITCH puolisävelaskelina. Jokaisen nupin voi lukita askelkohtaisesti ja "
            "liikuttaa LFO:illa.",
            "<b>EDIT</b> öffnet die Seite SOUND der Spur, nochmal <b>EDIT</b> SOUND 2 (in den Tabellen EDIT²). Die Tabellen kommen "
            "direkt aus dem Code der Firmware: Werkswerte 0–127, PITCH in Halbtönen. Jeder Regler lässt sich pro Step locken und "
            "von den LFOs bewegen.",
            "<b>EDIT</b>: SOUND; <b>EDIT</b> latlh: SOUND 2 (EDIT²). ngoqvo' ghoS tetlhmey: ngo' mI' 0 – 127. lock laH, LFO vIHmoH laH.")),
    ("gen", "knobs"), ("gen", "mix"))

sec("Askeleet ja lukot", "Steps und Locks", "mIwmey lock je",
    ("p", L("Napauta valkoista kosketinta: askel päälle tai pois. <b>Pidä</b> valkoista kosketinta ja käännä: nupit muokkaavat "
            "vain sitä askelta.", "Weiße Taste tippen: Step an oder aus. Weiße Taste <b>halten</b> und drehen: Die Regler ändern "
            "nur diesen Step.", "leQ chIS yIyuv: mIw chu' pagh tam. <b>yI'uch</b>, yIDIngmoH: mIw'vam neH.")),
    ("ul", [L("<b>K1</b>: nuotti ±24 puolisävelaskelta", "<b>K1</b>: Note ±24 Halbtöne", "<b>K1</b>: QoQ ±24"),
            L("<b>K2</b>: todennäköisyys, portaaton 1–100 %", "<b>K2</b>: Chance, stufenlos 1–100 %", "<b>K2</b>: Do', 1 – 100 %"),
            L("<b>K3</b>: aksentti; BASSO, HAPPO ja PIIP: OFF, ACC, SLIDE, ACC+SLIDE", "<b>K3</b>: Akzent; BASSO, HAPPO, PIIP: OFF, ACC, SLIDE, ACC+SLIDE",
              "<b>K3</b>: accent; SLIDE je"),
            L("<b>K4</b>: ratchet, 1–4 iskua askeleessa", "<b>K4</b>: Ratchet, 1–4 Schläge im Step", "<b>K4</b>: ratchet, 1 – 4"),
            L("<b>SELECT</b>: askel aikaisemmin tai myöhemmin", "<b>SELECT</b>: Step früher oder später", "<b>SELECT</b>: nom pagh tlhaw'"),
            L("<b>ALGORITHM</b>: trig-ehto 1:2 … 8:8, FILL, !FILL, PRE, !PRE, 1ST, !1ST", "<b>ALGORITHM</b>: Bedingung 1:2 … 8:8, FILL, !FILL, PRE, !PRE, 1ST, !1ST",
              "<b>ALGORITHM</b>: ra'ghom"),
            L("<b>SEL</b>: poista askeleen siirto ja lukot", "<b>SEL</b>: Verschiebung und Locks des Steps weg", "<b>SEL</b>: vIH lock je teq")]),
    ("p", L("Askeleen oma ääni on <b>lukko</b>: pidä askelta EDIT-sivulla ja käännä. Lukitut arvot näkyvät vihreinä; 32 lukkoa "
            "patternia kohden. Trig-ehto 1:2 soi joka toisen tahdin ensimmäisessä, FILL vain kun ARP on pohjassa, 1ST vain "
            "ensimmäisessä tahdissa PLAYn jälkeen.",
            "Ein eigener Klang für einen Step ist ein <b>Lock</b>: Step auf der EDIT-Seite halten und drehen. Gelockte Werte sind "
            "grün; 32 Locks pro Pattern. Bedingung 1:2 spielt im ersten von je zwei Takten, FILL nur bei gehaltenem ARP, 1ST "
            "nur im ersten Takt nach PLAY.",
            "mIw wab: <b>lock</b>. EDIT Daq mIw yI'uch, yIDIngmoH; SuD; 32 lock. 1:2: cha' bar wa'DIch; FILL: ARP 'uchlu'DI'; 1ST: wa'DIch bar.")))

sec("Looppien pituus", "Looplängen", "loop 'aD",
    ("p", L("<b>ALGORITHM</b> ilman pidettyä askelta asettaa raidan loopin pituuden 1–16. Erimittaiset loopit kulkevat toisiaan "
            "vastaan: HAPPO 14:ssä kickin 16:ta vastaan kohtaa sen vasta seitsemän tahdin päästä. Siksi suomisaundi ei koskaan "
            "toistu samana.",
            "<b>ALGORITHM</b> ohne gehaltenen Step stellt die Looplänge der Spur ein, 1–16. Ungleiche Längen laufen "
            "gegeneinander: HAPPO auf 14 gegen die 16 der Kick trifft sie erst nach sieben Takten wieder. Darum wiederholt sich "
            "Suomisaundi nie genau.",
            "<b>ALGORITHM</b>: loop 'aD 1 – 16. HAPPO 14, kick 16: Soch bar veb ghom. not rap.")))

sec("LFO:t ja MOD", "LFOs und MOD", "LFO MOD je",
    ("p", L("Jokaisella raidalla on kaksi LFO:ta (<b>LFO</b>, uudelleen <b>LFO</b>) grooven tahdissa: RATE kuudestoistaosasta "
            "kuuteentoista tahtiin, DEPTH kumpaankin suuntaan, TARGET mikä tahansa ääninuppi tai LEVEL, PAN, DELAY, REVERB, "
            "SHAPE SINE, TRI, SAW, SQR, RAND. Kolmas painallus: <b>MOD</b>.",
            "Jede Spur hat zwei LFOs (<b>LFO</b>, nochmal <b>LFO</b>) im Takt des Grooves: RATE von einer Sechzehntel bis 16 "
            "Takte, DEPTH in beide Richtungen, TARGET jeder Klangregler oder LEVEL, PAN, DELAY, REVERB, SHAPE SINE, TRI, SAW, "
            "SQR, RAND. Dritter Druck: <b>MOD</b>.",
            "He Hoch cha' LFO: RATE, DEPTH, TARGET, SHAPE. wejDIch: <b>MOD</b>.")),
    ("ul", [L("<b>RESTART</b>: toisen raidan isku käynnistää LFO:t alusta – liike istuu grooveen.",
              "<b>RESTART</b>: Jeder Schlag einer anderen Spur startet die LFOs neu – die Bewegung sitzt im Groove.",
              "<b>RESTART</b>: He latlh mup LFO bI'reS."),
            L("<b>ENV</b>: kuinka kovaa lähde soi, liikuttaa tämän raidan kohdetta. POTKU HATTUn tasolle, DEPTH alle nollan: hatti väistää kickiä.",
              "<b>ENV</b>: Wie laut die Quelle gerade klingt, bewegt ein Ziel dieser Spur. POTKU auf den Pegel von HATTU, DEPTH unter null: die Hat weicht der Kick.",
              "<b>ENV</b>: Hal HoS TARGET vIHmoH."),
            L("Pidä <b>LFO</b>: raidan ääni takaisin alkuun (undo palauttaa).", "<b>LFO</b> halten: Klang der Spur auf Start (Undo holt ihn zurück).",
              "<b>LFO</b> yI'uch: wab bI'reS.")]),
    ("sticker", L("Hullu happo: HAPPO, LFO 1 → CUTOFF, RATE 2 BAR, TRI, DEPTH +40. LFO 2 → RESO, RAND. Naapurit soittavat poliisille.",
                  "Irre Säure: HAPPO, LFO 1 → CUTOFF, RATE 2 BAR, TRI, DEPTH +40. LFO 2 → RESO, RAND. Die Nachbarn rufen die Polizei.",
                  "acid QIp: HAPPO, LFO 1 → CUTOFF, 2 BAR, TRI, +40. LFO 2 → RESO, RAND. jIlpu' bep.")))

sec("Euclid, linkit, ajoitus", "Euclid, Links, Timing", "euclid, muv, poH",
    ("ul", [L("<b>SEQ</b>: EUCLID levittää iskut tasaisesti: HITS, ROTATE, CHANCE (portaaton), ACCENT (joka n:s tai RANDOM).",
              "<b>SEQ</b>: EUCLID verteilt die Schläge gleichmäßig: HITS, ROTATE, CHANCE (stufenlos), ACCENT (jeder n-te oder RANDOM).",
              "<b>SEQ</b>: EUCLID: HITS, ROTATE, CHANCE, ACCENT."),
            L("<b>SEQ</b> kahdesti: LINK. Raita soi vain missä lähde iskee (WITH), on hiljaa (GAPS) tai askeleen jälkeen (AFTER). "
              "FOLLOW: nuotit seuraavat toisen raidan sointuja; ACCENT: lähteen aksentit.",
              "<b>SEQ</b> zweimal: LINK. Die Spur spielt nur, wo die Quelle schlägt (WITH), schweigt (GAPS) oder einen Step danach "
              "(AFTER). FOLLOW: Noten folgen den Akkorden einer anderen Spur; ACCENT: deren Akzente.",
              "<b>SEQ</b> cha'logh: LINK. WITH, GAPS, AFTER. FOLLOW, ACCENT."),
            L("<b>SEQ</b> kolmesti: TIMING. Yksittäinen isku tai koko raita aikaisemmin tai myöhemmin, puoli kuudestoistaosaa.",
              "<b>SEQ</b> dreimal: TIMING. Ein Schlag oder die ganze Spur früher oder später, bis eine halbe Sechzehntel.",
              "<b>SEQ</b> wejlogh: TIMING.")]))

sec("Sidechain: pumppu", "Sidechain: die Pumpe", "SIDECHAIN: pum",
    ("p", L("<b>FX</b> kahdesti. Lähde on POTKU. Jokainen isku painaa muut raidat alas, delay ja kaiku mukana. AMOUNT raidalle: BASSO "
            "127 (koko pumppu), muut puolet. Mykistä POTKU: pumppu jää – haamukick.",
            "<b>FX</b> zweimal. Quelle ist POTKU. Jeder Schlag drückt die anderen Spuren runter, Delay und Hall mit. AMOUNT pro Spur: "
            "BASSO 127 (die volle Pumpe), die anderen halb. POTKU stumm schalten: die Pumpe bleibt – eine Geister-Kick.",
            "<b>FX</b> cha'logh. Hal: POTKU. mup Hoch latlh bIngDaq yuv. BASSO 127. POTKU yItammoH: pum ratlh.")))

sec("Raidat 5 ja 6: neljä moottoria", "Spur 5 und 6: vier Engines", "He 5 He 6 je: loS QuQ",
    ("p", L("<b>HOME</b> kahdesti: GROOVE 2. Nuppi 1 valitsee raidan 5 moottorin, nuppi 2 raidan 6. Uusi moottori tuo äänensä ja "
            "sääntöjensä mukaisen patternin ja tulee <b>mykistettynä</b>: SEL tuo sen mukaan, kun on aika. GLOBAL 2:n WORK: LIVE "
            "vaihtaa kaikissa patterneissa, PROD vain muokattavassa.",
            "<b>HOME</b> zweimal: GROOVE 2. Regler 1 wählt die Engine von Spur 5, Regler 2 die von Spur 6. Eine neue Engine bringt "
            "Klang und Pattern nach ihren Regeln mit und kommt <b>stumm</b>: SEL holt sie rein, wenn's passt. WORK auf GLOBAL 2: "
            "LIVE wechselt in allen Patterns, PROD nur im bearbeiteten.",
            "<b>HOME</b> cha'logh: GROOVE 2. SeH 1: He 5; SeH 2: He 6. QuQ chu' <b>tamlu'</b>: SEL. WORK: LIVE, PROD.")),
    ("ul", [L("<b>PIIP</b>: äänipiiri, melodia kysymyksenä ja vastauksena soinnun sävelillä.", "<b>PIIP</b>: Soundchip, Melodie als Frage und Antwort auf Akkordtönen.",
              "<b>PIIP</b>: wab chip, bom."),
            L("<b>KLIKKI</b>: pienet kohinajyvät.", "<b>KLIKKI</b>: kleine Rauschkörner.", "<b>KLIKKI</b>: chuS mach."),
            L("<b>STAB</b>: FM-soinnut, sävellajissa.", "<b>STAB</b>: FM-Akkorde in der Tonart.", "<b>STAB</b>: FM chord."),
            L("<b>SUHINA</b>: kohina, riserit ja laskut. LENGTH ääri-vasemmalla: <b>CLAP</b> iskuille 2 ja 4, ei koskaan ykköselle.",
              "<b>SUHINA</b>: Rauschen, Riser, Downlifter. LENGTH ganz links: <b>CLAP</b> auf 2 und 4, nie auf die Eins.",
              "<b>SUHINA</b>: chuS. LENGTH poS: <b>CLAP</b>, 2 4 je.")]),
    ("gen", "engines"))

sec("Pumppu ja säännöt", "Die Pumpe und die Regeln", "pum ra'mey je",
    ("p", L("Pumppu on sydän. <b>BASSO</b> ei koskaan soi kickin päällä vaan sen takana: useimmiten <b>rulla</b> (potku, basso, "
            "basso, basso), muuten <b>laukka</b> (potku, tauko, basso, basso). Pohjasävelellä, tahdin lopussa oktaavi, usein "
            "slidella; kickin jälkeinen kuudestoistaosa hiljaa, offbeat aksentilla, lyhyt häive.",
            "Die Pumpe ist das Herz. <b>BASSO</b> spielt nie auf der Kick, sondern dahinter: meist der <b>Roll</b> (Kick, Bass, Bass, "
            "Bass), sonst der <b>Galopp</b> (Kick, Pause, Bass, Bass). Auf dem Grundton, am Taktende die Oktave, oft mit Slide; die "
            "Sechzehntel nach der Kick leise, der Offbeat betont, kurzer Ausklang.",
            "pum tIq 'oH. <b>BASSO</b> kickDaq QoQbe', 'emDaq QoQ: <b>roll</b> pagh <b>gallop</b>. QoQ botlh, octave, slide.")),
    ("ul", [L("<b>HAPPO</b> kävelee kahdeksan nuotin motiivia omalla loopillaan; slide ja aksentti 303:n tapaan.",
              "<b>HAPPO</b> geht ein Motiv aus acht Noten auf eigener Loop; Slide und Akzent wie bei der 303.", "<b>HAPPO</b>: chorgh QoQ motif."),
            L("<b>PIIP</b> vastaa siellä, missä happo lepää: kysymys päättyy auki, vastaus tulee kotiin.",
              "<b>PIIP</b> antwortet, wo die Säure Pause macht: die Frage endet offen, die Antwort kommt heim.", "<b>PIIP</b> jang acid leSDI'."),
            L("<b>HATTU</b> istuu offbeatilla, harvoin tuplana; <b>KLIKKI</b> kulkee parittomilla loopeilla.",
              "<b>HATTU</b> sitzt auf dem Offbeat, selten doppelt; <b>KLIKKI</b> läuft auf krummen Loops.", "<b>HATTU</b> offbeat; <b>KLIKKI</b> loop chIm."),
            L("<b>POTKU</b>: neljä lattiaan, viritettynä; joskus haamu tai tupla viimeisellä neljäsosalla.",
              "<b>POTKU</b>: vier auf den Boden, gestimmt; manchmal ein Geist oder ein Doppelschlag auf der letzten Viertel.", "<b>POTKU</b>: loS rav Daq."),
            L("Vähän rullia: C:ssä hatit tuplaavat vain kahdella viimeisellä askeleella.", "Wenig Wirbel: In C doppeln die Hats nur auf den letzten zwei Steps.",
              "roll puS.")]))

sec("Patternit, LAZY ja HARD", "Patterns, LAZY und HARD", "pattern, LAZY HARD je",
    ("p", L("<b>A</b> on groove. <b>B</b> soittaa A:n muunneltuna, <b>C</b> filleillä seuraavaan tahtiin, <b>D</b> sukulaissävellajissa. "
            "PRESETS vaihtaa; soitettaessa tahdin alussa. Mitä muutat, muutat A:ssa; B–D seuraavat heti.",
            "<b>A</b> ist der Groove. <b>B</b> spielt A variiert, <b>C</b> mit Fills in den nächsten Takt, <b>D</b> in einer verwandten "
            "Tonart. PRESETS wechselt; beim Spielen zum nächsten Takt. Was du änderst, änderst du in A; B bis D folgen sofort.",
            "<b>A</b>: groove. <b>B</b>: choH, <b>C</b>: fill, <b>D</b>: key retlh. PRESETS: choH.")),
    ("ul", [L("<b>GLOBAL 2</b> MODE: LAZY (B–D syntyvät itsestään) tai HARD (neljä omaa patternia).", "<b>GLOBAL 2</b> MODE: LAZY (B–D entstehen von selbst) oder HARD (vier eigene Patterns).",
              "<b>GLOBAL 2</b> MODE: LAZY pagh HARD."),
            L("PLAY: LOOP, A-D (neljä tahtia kukin) tai RANDOM.", "PLAY: LOOP, A-D (je vier Takte) oder RANDOM.", "PLAY: LOOP, A-D, RANDOM."),
            L("CHAIN (GLOBAL): A-B, A-C, A-D tai EVOLVE: setti joka liikkuu.", "CHAIN (GLOBAL): A-B, A-C, A-D oder EVOLVE: ein Set, das sich bewegt.", "CHAIN: EVOLVE."),
            L("Kun C:n kick pitää tauon, noppa heittää kerran kolmesta: kick muuttuu kaikissa patterneissa.",
              "Pausiert die Kick in C, würfelt es einmal in drei: die Kick ändert sich in allen Patterns.", "C kick leSDI', kick choH.")]))

sec("Sivut", "Seiten", "Hotlhmey", ("gen", "pages"),
    ("p", L("Pidetty <b>LFO</b>: raidan ääni alkuun. Pidetty <b>FX</b>: efektit alkuun.", "<b>LFO</b> halten: Klang der Spur auf Start. <b>FX</b> halten: Effekte auf Start.",
            "<b>LFO</b> yI'uch: wab bI'reS. <b>FX</b> yI'uch: FX bI'reS.")))

sec("SLICE ja beat repeat", "SLICE und Beat Repeat", "SLICE beat repeat je",
    ("ul", [L("<b>FX</b> kolmesti: SLICE pilkkoo HATTUn, HAPPOn ja raidat 5–6 (ei koskaan POTKUa eikä BASSOa): GATE, STUTTER tai "
              "GRAIN (enintään kaksi raitaa). <b>FX</b> neljästi: SLICE-LFO.",
              "<b>FX</b> dreimal: SLICE zerhackt HATTU, HAPPO und die Spuren 5–6 (nie POTKU und BASSO): GATE, STUTTER oder GRAIN "
              "(höchstens zwei Spuren). <b>FX</b> viermal: der SLICE-LFO.",
              "<b>FX</b> wejlogh: SLICE (POTKU BASSO pe'be'): GATE, STUTTER, GRAIN. <b>FX</b> loSlogh: SLICE LFO."),
            L("<b>SEL</b> pohjassa + valkoinen 1–4: master toistaa iskua, kahdeksasosaa, kuudestoistaosaa tai 32-osaa, kunnes päästät irti.",
              "<b>SEL</b> halten + weiße Taste 1–4: die Summe wiederholt Viertel, Achtel, Sechzehntel oder Zweiunddreißigstel, bis du loslässt.",
              "<b>SEL</b> 'uch + chIS 1 – 4: master rap QoQmoH.")]))

sec("Master: FILTER, BASS, AIR, DRIFT", "Die Summe: FILTER, BASS, AIR, DRIFT", "master: FILTER, BASS, AIR, DRIFT",
    ("ul", [L("<b>FILTER</b> (GROOVE 2): yksi nuppi, alipäästö vasemmalle, ylipäästö oikealle, keskellä pois.",
              "<b>FILTER</b> (GROOVE 2): ein Regler, links Tiefpass, rechts Hochpass, in der Mitte aus.", "<b>FILTER</b>: poS low-pass, nIH high-pass."),
            L("<b>BASS</b> (GROOVE 2): alle 100 Hz:n alue uudelleen, noin +9 dB.", "<b>BASS</b> (GROOVE 2): alles unter 100 Hz noch einmal, bis +9 dB.", "<b>BASS</b>: 100 Hz bIng latlh."),
            L("<b>AIR</b> (GLOBAL 2): yli 2,5 kHz:n alue uudelleen, +6 dB.", "<b>AIR</b> (GLOBAL 2): alles über 2,5 kHz noch einmal, bis +6 dB.", "<b>AIR</b>: 2,5 kHz Dung latlh."),
            L("<b>DRIFT</b> (HOME): sointiväri, häive, taso ja ajoitus liikkuvat hitaasti ja satunnaisesti. Kick ei koskaan heittele.",
              "<b>DRIFT</b> (HOME): Klangfarbe, Ausklang, Pegel und Timing wandern langsam und zufällig. Die Kick nie.", "<b>DRIFT</b>: QIt vIH.")]))

sec("Koskettimet ja MIDI", "Tasten und MIDI", "leQmey MIDI je",
    ("ul", [L("<b>REC</b>: koskettimet soittavat valittua raitaa, C4 perussävel, OCT−/OCT+ kaksi oktaavia; soitettaessa nuotit kirjoittuvat askeliin.",
              "<b>REC</b>: die Tasten spielen die Spur, C4 ist der Grundton, OCT−/OCT+ zwei Oktaven; beim Spielen landen die Noten in den Steps.",
              "<b>REC</b>: leQmey He QoQmoH, C4 botlh."),
            L("MIDI-kanavat 1–6 soittavat kuutta raitaa; kanava 10 on rumpukartta (36 potku, 42 hattu …).",
              "MIDI-Kanäle 1–6 spielen die sechs Spuren; Kanal 10 ist eine Drum-Map (36 Kick, 42 Hat …).", "MIDI 1 – 6: jav He; MIDI 10: drum."),
            L("Start/stop vastaanotetaan; CLOCK päällä: kello USB:n yli.", "Start/Stopp kommen an; mit CLOCK geht die Clock über USB raus.", "bI'reS mev je; CLOCK: USB.")]))

sec("Reseptit", "Rezepte", "ghojmeH ghItlh",
    ("ul", [L("<b>UFO laskeutuu:</b> raita 6 → SUHINA, LENGTH 1 BAR, NEW kunnes tulee riser, SWEEP oikealle, RESO ylös.",
              "<b>Das UFO landet:</b> Spur 6 → SUHINA, LENGTH 1 BAR, NEW bis ein Riser kommt, SWEEP nach rechts, RESO hoch.",
              "<b>UFO leng:</b> He 6 → SUHINA, SWEEP nIH, RESO Dung."),
            L("<b>Saunabasso:</b> BASSO CUTOFF alas, RESO 70, DRIVE ylös, BASS 40 %, AIR 0. Löylyä.",
              "<b>Saunabass:</b> BASSO CUTOFF runter, RESO 70, DRIVE hoch, BASS 40 %, AIR 0. Aufguss.", "<b>bIQ tuj bass:</b> CUTOFF bIng, DRIVE Dung."),
            L("<b>Poron piippaus:</b> PIIP, WAVE pulssi 12 %, ARP ylös, SPEED nopea, CRUSH vähän.",
              "<b>Rentier-Gepiepse:</b> PIIP, WAVE Puls 12 %, ARP hoch, SPEED schnell, etwas CRUSH.", "<b>PIIP:</b> pulse 12 %, ARP Dung."),
            L("<b>Klikkimetsä:</b> KLIKKI ALGORITHM 11, CHANCE 50 %, SCATTER täysille.", "<b>Klickwald:</b> KLIKKI ALGORITHM 11, CHANCE 50 %, SCATTER voll.",
              "<b>click Sor:</b> ALGORITHM 11, CHANCE 50 %."),
            L("<b>Taputa:</b> raita 5 → SUHINA (tulee clapina iskuille 2 ja 4). SEL tuo sen mukaan.",
              "<b>Klatschen:</b> Spur 5 → SUHINA (kommt als Clap auf 2 und 4). SEL holt ihn rein.", "<b>CLAP:</b> He 5 → SUHINA, SEL."),
            L("<b>Hullu happo:</b> katso LFO-tarra. Naapurit tietävät.", "<b>Irre Säure:</b> siehe LFO-Sticker. Die Nachbarn wissen Bescheid.",
              "<b>acid QIp:</b> LFO yIlegh."),
            L("<b>Hiljainen tunti:</b> POTKU mykistetty, pumppu jää, HAPPO RESO 100, DRIFT 80. Odota.",
              "<b>Stille Stunde:</b> POTKU stumm, die Pumpe bleibt, HAPPO RESO 100, DRIFT 80. Warten.", "<b>tam rep:</b> POTKU tam, pum ratlh.")]))

sec("UFO, uni ja hyvää yötä", "UFO, Schlaf und gute Nacht", "UFO, Qong, maj ram",
    ("ul", [L("<b>Käynnistys:</b> vihreä 8-bittinen UFO laskeutuu harmaaseen metsään, kamera zoomaa, UFO räjähtää ja pirstaleista "
              "nousee nimi, jinglen kera. Sitten kuva häivytetään sivuille.",
              "<b>Einschalten:</b> Ein grünes 8-Bit-UFO landet im grauen Wald, die Kamera zoomt, es explodiert und aus den Splittern "
              "steigt der Name, mit Jingle. Dann blendet das Bild in die Seiten.",
              "<b>bI'reS:</b> SuD 8-bit UFO Sor Daq leng, Hop, jor; pong Hu', bom mach."),
            L("<b>Kaksi minuuttia koskematta:</b> nimi pumppaa kickin tahdissa, kirjain kerrallaan vihreänä.",
              "<b>Zwei Minuten nichts berührt:</b> Der Name pumpt im Takt der Kick, ein Buchstabe nach dem anderen grün.",
              "<b>cha' tup DachQo'DI':</b> pong pum kick rur."),
            L("<b>SAVE 2 s:</b> tallentaa, kuva kutistuu kuin vanhassa putkitelkkarissa, musiikki maiskahtaa pois ja <b>HYVÄÄ YÖTÄ</b> "
              "hehkuu. Sitten pimeää ja hiljaista, kunnes sammutat tai kosket.",
              "<b>SAVE 2 s:</b> speichert, das Bild schnurrt zusammen wie bei einer alten Röhre, die Musik schmatzt weg und "
              "<b>HYVÄÄ YÖTÄ</b> leuchtet. Dann dunkel und still, bis du ausschaltest oder etwas berührst.",
              "<b>SAVE cha' lup:</b> pol, HaSta luj, QoQ SoQ, <b>HYVÄÄ YÖTÄ</b> wov.")]))

sec("Usein kysyttyä", "Häufige Fragen", "ghel law'",
    ("ul", [L("<b>Voiko tällä soittaa humppaa?</b> Teknisesti kyllä. Moraalisesti emme vastaa.",
              "<b>Kann man damit Humppa spielen?</b> Technisch ja. Moralisch übernehmen wir keine Haftung.", "<b>humppa?</b> HIja'. 'ach jIjangbe'."),
            L("<b>Miksi UFO?</b> Koska psytrance. Seuraava kysymys.", "<b>Warum ein UFO?</b> Weil Psytrance. Nächste Frage.", "<b>qatlh UFO?</b> psytrance. ghel latlh."),
            L("<b>Missä on lehmä?</b> Sitä ei ole koskaan nähty uudestaan.", "<b>Wo ist die Kuh?</b> Sie wurde nie wieder gesehen.",
              "<b>nuqDaq tangqa'?</b> not leghqa'lu'."),
            L("<b>Kuumeneeko FM-1?</b> Ei. Sinä kuumenet.", "<b>Wird der FM-1 heiß?</b> Nein. Du wirst heiß.", "<b>FM-1 tuj?</b> ghobe'. SoH tuj."),
            L("<b>Miksi kaikki on vihreää?</b> Happo. Seuraava.", "<b>Warum ist alles grün?</b> Säure. Nächste.", "<b>qatlh SuD Hoch?</b> acid."),
            L("<b>Onko tämä valmis?</b> Ei. Se on kokeilu. Siksi se on hauska.", "<b>Ist das fertig?</b> Nein. Es ist ein Versuch. Darum macht es Spaß.",
              "<b>rIn'a'?</b> ghobe'. ghot 'oH. Quch.")]))

sec("Salaisuus", "Das Geheimnis", "pegh",
    ("sticker", L("Kaikkea ei kerrota. Sanotaan, että joka pitää tarpeeksi kauan kiinni maailmasta, näkee toisen. Kaikki ei ole vihreää. 👽",
                  "Nicht alles wird verraten. Man sagt, wer lange genug an der Welt festhält, sieht eine andere. Nicht alles ist grün. 👽",
                  "Hoch jatlhbe'lu'. qo' Da'uchtaHvIS nI', qo' latlh Dalegh. SuD Hoch ghobe'. 👽")))

sec("Pientä präntättyä", "Kleingedrucktes", "ghItlh mach",
    ("ul", [L("suom1saundi on kokeilu: jos FM-1:n aika loppuu, se lähtee ensimmäisenä (ROMI_SUOMI=0).",
              "suom1saundi ist ein Versuch: Wird die Zeit des FM-1 knapp, fliegt er als Erstes raus (ROMI_SUOMI=0).",
              "suom1saundi ghot 'oH: poH HutlhDI', wa'DIch mej."),
            L("Ääntä, ajoitusta ja kuormaa oikealla laitteella ei ole vielä mitattu.", "Klang, Timing und Last auf dem echten Gerät sind noch nicht gemessen.",
              "jan teH wab, poH, 'ar je juvbe'lu'."),
            L("Alkuperä: github.com/g0rst/suom1saundi. Rakennettu fm1-basen ja felucca-bsp:n päälle. MIT-lisenssi. Ei M-VAVEn kanssa yhteydessä.",
              "Herkunft: github.com/g0rst/suom1saundi. Gebaut auf fm1-base und felucca-bsp. MIT-Lizenz. Nicht mit M-VAVE verbunden.",
              "ngoQ: github.com/g0rst/suom1saundi. fm1-base felucca-bsp je. MIT. M-VAVE muvbe'.")]))
