#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""suom1saundi's own manual, apart from ro:MINImal's: Finnish and Klingon, in suom1saundi's trashy dress (as in
github.com/g0rst/suom1saundi: comic type, a checkerboard, a ticker, stickers) with UFOs, 8-bit pixels and nonsense.

    python3 manual/suomi.py        ->  docs/suomi.html

suom1saundi is an experiment inside ro:MINImal, not a product: the manual says so. Its tables (tracks, knobs, factory
values, engines, start settings) come from the firmware's code (manual/codefacts.py). The way between the two
styles is not told here: a riddle only."""
import html
import pathlib
import re

from codefacts import facts, pct, pan

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = facts()
LANGS = ("fi", "tlh")
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ST = F["style"]["suomi"]
KEY = f"{NOTE_NAMES[ST['root'] % 12]}"


def L(fi, tlh):
    return {"fi": fi, "tlh": tlh}


# ------------------------------------------------------------------------------------------- the words ---
UI = {
    "title": L("suom1saundi – käyttöohje", "suom1saundi – lo'meH paq"),
    "ticker": L("★ SUOM1SAUNDI ★ UFO LASKEUTUI METSÄÄN ★ PSY-POTKU ★ HAPPO SIHISEE ★ 8-BITTIÄ ★ TÄMÄ ON KOKEILU, EI TUOTE ★ "
                "JOS FM-1 HIKOILEE, TÄMÄ LÄHTEE ENSIMMÄISENÄ ★ HYVÄÄ YÖTÄ ★ ÄLÄ SYÖ NAPPEJA ★",
                "★ SUOM1SAUNDI ★ DujDaq leng UFO, Sor Daq Saq ★ POTKU ★ HAPPO chuS ★ 8-BIT ★ ghot neH, Dochmey ngevlu'be' ★ "
                "FM-1 tlhuH ngaQDI', wa'DIch mej ★ maj ram ★ leQmey yISopQo' ★"),
    "tag": L("Kokeilu ro:MINImalin sisällä · ei tuote · build", "ro:MINImal qoD ghot · Doch ngevlu'be' · build"),
    "new": L("UUSI!", "chu'!"),
    "emu": L("▶ PELAA EMULAATTORISSA", "▶ emulator yIQujmoH"),
    "toc": L("SISÄLTÖ", "DotlhmeyDaj"),
    "home": L("projektisivu", "ghItlh tetlh"),
    "build": L("rakennettu koodista", "ngoqvo' chenmoHlu'"),
    "counter": L("kävijöitä", "Such ghotpu'"),
    "construct": L("TYÖMAA · TÄMÄ OHJE KIRJOITTAA ITSENSÄ UUDELLEEN JOKA KERTA · TYÖMAA",
                   "Qu' 'oH · ghItlh'vam rap ghItlh'qa' · Qu' 'oH"),
    "th_track": L(["kosketin", "raita", "suomeksi", "tehtävä"], ["leQ", "He", "Suomi Hol", "Qu'"]),
    "th_knob": L(["nuppi", "nimi", "tehdas", "mitä se tekee"], ["SeH", "pong", "ngo'", "nuq ta'"]),
    "th_mix": L(["raita", "taso", "pan", "delay", "kaiku", "glide"], ["He", "HoS", "pan", "delay", "reverb", "glide"]),
    "th_eng": L(["moottori", "SOUND", "SOUND 2", "taso"], ["QuQ", "SOUND", "SOUND 2", "HoS"]),
    "th_page": L(["painike", "sivu", "mitä siellä on"], ["leQ", "Hotlh", "nuq tu'lu'"]),
}

ROLE = {   # track: (Finnish meaning, role fi, role tlh)
    0: ("potku", "psy-kick, neljä lattiaan, viritettynä sävellajiin", "psy kick, loS rav Daq, key rur"),
    1: ("basso", "pumppaava suodinbasso kickin takana: rulla tai laukka", "bass pum, kick 'emDaq: roll pagh gallop"),
    2: ("hattu", "hatit ja shakerit offbeatilla, FM-metallia ja 8-bittistä kohinaa", "hat, offbeat Daq: baS FM, 8-bit chuS"),
    3: ("happo", "acid-linja 303:n tapaan: aksentti ja slide omalla loopillaan", "acid tlhegh, 303 rur: accent, slide"),
    4: ("piip", "äänipiirin melodia: kysymys ja vastaus", "wab chip bom: ghel, jang"),
    5: ("klikki", "ro:MINImalin klikit parittomilla loopeilla", "ro:MINImal click, loop chImmey"),
}

# what each knob does, by track and name: (fi, tlh)
DESC = {
    "POTKU": {
        "TUNE": ("perussävel", "QoQ botlh"), "DECAY": ("kuinka kauan se soi", "wab tIq"),
        "SWEEP": ("kuinka korkealta sävel putoaa: psy-”tok”", "wab pum: psy 'tok'"),
        "DRIVE": ("kylläisyys, lämpimästä rikkinäiseen", "HoS, jach"), "PITCH": ("koko raita ±24 puolisävelaskelta", "He Hoch vIH, ±24"),
        "CLICK": ("klikki alussa", "wab tagh 'och"), "SNAP": ("kuinka nopeasti sweep putoaa", "pum nom"),
        "CRUSH": ("bittisyvyys ja näytetaajuus alas: 8-bittiä", "bit mI' nup: 8-bit"),
    },
    "BASSO": {
        "CUTOFF": ("alipäästön rajataajuus (18 dB)", "tlhegh Hab: Dung bIng"), "RESO": ("resonanssi", "jach"),
        "ENVMOD": ("kuinka paljon verhokäyrä avaa suodinta", "tlhegh poSmoH"), "DECAY": ("tason ja suotimen häive", "wab tIq"),
        "PITCH": ("koko raita ±24 puolisävelaskelta", "He Hoch vIH, ±24"), "WAVE": ("saha (0) … kantti (127)", "saw 0 .. square 127"),
        "DRIVE": ("särö ennen suodinta", "HoS jach"), "CRUSH": ("bittisyvyys alas", "bit mI' nup"),
    },
    "HATTU": {
        "DECAY": ("kuinka kauan se soi", "wab tIq"), "TONE": ("metallin sävelkorkeus", "baS wab Dung bIng"),
        "METAL": ("kohina (0) … FM-metalli (127)", "chuS 0 .. baS 127"), "OPEN": ("aksentti avaa: suljettu … auki", "accent poSmoH"),
        "PITCH": ("koko raita ±24", "He Hoch vIH"), "CHIP": ("äänipiirin 8-bittinen kohina mukaan", "wab chip chuS"),
        "DRIVE": ("särö", "HoS"), "CRUSH": ("bittisyvyys alas", "bit mI' nup"),
    },
    "HAPPO": {
        "CUTOFF": ("rajataajuus: acid-linjan sydän", "tlhegh Hab: acid tIq"), "RESO": ("resonanssi, vihellyksen rajalle", "jach, wej SuS"),
        "ENVMOD": ("kuinka paljon verhokäyrä avaa", "tlhegh poSmoH"), "DECAY": ("häive; aksentti pidentää", "wab tIq"),
        "PITCH": ("koko raita ±24", "He Hoch vIH"), "WAVE": ("saha … kantti", "saw .. square"),
        "DRIVE": ("särö: 303 huutaa", "HoS: 303 jach"), "CRUSH": ("bittisyvyys alas", "bit mI' nup"),
    },
    "PIIP": {
        "WAVE": ("pulssi 12/25/50 %, 4-bittinen kolmio, saha, kohina", "pulse, triangle, saw, chuS"),
        "DECAY": ("kuinka kauan se soi", "wab tIq"), "ARP": ("arpeggio: oktaavit, soinnut", "arpeggio"),
        "VIBRATO": ("vibrato", "vibrato"), "PITCH": ("koko raita ±24", "He Hoch vIH"),
        "SPEED": ("arpeggion nopeus", "arpeggio Do"), "DRIVE": ("särö", "HoS"), "CRUSH": ("bittisyvyys alas", "bit mI' nup"),
    },
    "KLIKKI": {
        "DECAY": ("kuinka kauan se soi", "wab tIq"), "FREQ": ("kaistanpäästön taajuus", "Hab Dung bIng"),
        "RESO": ("kuinka kapea", "tlhop"), "SCATTER": ("kuinka laajalle stereoon", "stereo Daq ghomHa'"),
        "PITCH": ("koko raita ±24", "He Hoch vIH"), "ATTACK": ("isku: napsusta paisuntaan", "mup: nom .. QIt"),
        "DRIVE": ("särö", "HoS"), "CRUSH": ("bittisyvyys alas", "bit mI' nup"),
    },
}

# the prose: (heading, [blocks]); a block is ("p", text), ("ul", [texts]), ("sticker", text), ("gen", name)
S = []


def sec(fi, tlh, *blocks):
    S.append((L(fi, tlh), blocks))


sec("Mikä tämä on?", "nuq 'oH?",
    ("p", L("<b>suom1saundi</b> on <b>kokeilu</b>, ei tuote. Se asuu ro:MINImal-firmwaren sisällä M-VAVE FM-1:ssä: sama kone, "
            "sama paneeli, mutta äänet ja säännöt tulevat suomisaundista, suomalaisesta freestyle-psytrancesta. Se on "
            "hyppivää, leikkisää ja hölmöä: pumppaava basso, sihisevä acid, äänipiirin piipitys ja ääniä, joita kukaan ei "
            "odota.",
            "<b>suom1saundi</b> <b>ghot</b> 'oH, Doch ngevlu'bogh ghobe'. ro:MINImal firmware qoD, M-VAVE FM-1 Daq yIn: "
            "jan rap, SeHlaw rap, 'ach wabmey ra'mey je Suomi psytrance vo' ghoS. Sup, Quch, QIp: bass pum, acid chuS, "
            "wab chip, wab pIHbe'lu'bogh.")),
    ("p", L(f"Paketti <b>suom1saundi.fwsc</b> käynnistyy suom1saundina: {ST['bpm']} BPM, suora, {KEY} frygia-dominantti, "
            "ja UFO laskeutuu metsään. Kaikki ro:MINImalin taidot pysyvät: sivut, LFO:t, euclid, linkit, SLICE, beat repeat, "
            "LAZY ja HARD. Väri on happovihreä.",
            f"<b>suom1saundi.fwsc</b> suom1saundi bI'reS: {ST['bpm']} BPM, {KEY} phrygian dominant, 'ej Sor Daq leng UFO. "
            "ro:MINImal laH Hoch ratlh: Hotlhmey, LFO, euclid, muv, SLICE, beat repeat, LAZY HARD je. nguv: SuD acid.")),
    ("sticker", L("Kokeilu tarkoittaa: jos FM-1 hikoilee, suom1saundi lähtee ensimmäisenä. Se maksaa noin 8 % enemmän "
                  "prosessoria. Ilman sitä ro:MINImal on täsmälleen ennallaan.",
                  "ghot 'oH: FM-1 tlhuH ngaQDI', suom1saundi wa'DIch mej. 8 % latlh 'ar. ghajbe'DI', ro:MINImal rap.")))

sec("Varoitus", "ghuHmoHghach",
    ("ul", [L("Tämä on toiminut vain simulaattorissa ja emulaattorissa. <b>Ei vielä testattu oikealla FM-1:llä.</b>",
              "simulator emulator je Daq neH Qap. <b>FM-1 teH Daq waHbe'lu'.</b>"),
            L("Oma firmware voi tehdä FM-1:stä tiiliskiven: piirillä on yksi firmware eikä palautusnappia.",
              "firmware chu' FM-1 Qaw'laH: wa' firmware neH, chu'qa'ghach leQ ghajbe'."),
            L("Tiedä tie takaisin M-VAVEn firmwareen ennen asennusta (FM-1 Firmware Hub tai M-VAVEn päivitysohjelma).",
              "Dalanpa', M-VAVE firmware Daq chegh mIw yISov (FM-1 Firmware Hub, M-VAVE updater ghap).")]))

sec("Kokeile ja asenna", "yIwaH, yIlan",
    ("p", L("<b>Ilman laitetta:</b> yllä oleva vaaleanpunainen nappi avaa suom1saundin FM-1-emulaattorissa selaimessa, "
            "samalla koodilla kuin laitteessa. Ensin ääni päälle, sitten PLAY.",
            "<b>jan ghajbe'DI':</b> leQ Doq emulator poSmoH, De'wI' Daq; jan ngoQ rap. wab yIchu', PLAY yIyuv.")),
    ("ul", [L("Lataa <b>suom1saundi.fwsc</b> projektisivulta (SHA256SUMS vieressä).", "<b>suom1saundi.fwsc</b> yIlI' ghItlh tetlh vo'."),
            L("Asenna työkalulla, joka asentaa FM-1-firmwarepaketteja, esim. FM-1 Firmware Hub (fm1.designburgapps.com).",
              "FM-1 firmware jan yIlo' (FM-1 Firmware Hub)."),
            L("Kytke päälle: UFO laskeutuu harmaaseen pikselimetsään, zoomaa, räjähtää nimeksi. Mikä tahansa kosketus ohittaa.",
              "yIchu': Sor qIjHom Daq leng UFO, Hop, jor, pong moj. leQ yIyuv: Sup.")]))

sec("Pikastartti", "nom bI'reS",
    ("ul", [L("Paina <b>PLAY</b>. Groove soi; firmware tekee uuden joka käynnistyksellä.", "<b>PLAY</b> yIyuv. groove Qap; bI'reS Hoch chu'."),
            L("Vasemman reunan kuusi mustaa kosketinta valitsevat raidan: POTKU, BASSO, HATTU, HAPPO ja raidat 5–6.",
              "poS leQmey qIj jav He wIv: POTKU, BASSO, HATTU, HAPPO, He 5 – 6."),
            L("16 valkoista kosketinta ovat raidan 16 askelta. Napauta: päälle tai pois.", "leQmey chIS 16: mIwmey 16. yIyuv: chu' pagh tam."),
            L("<b>NEW</b> (neljäs musta oikealta): raita uusiksi. Pidä puoli sekuntia: koko groove uusiksi.",
              "<b>NEW</b>: He chu'. bID lup yI'uch: groove Hoch chu'."),
            L("<b>ARP</b>: yksi pieni mutaatio. <b>UNDO</b> (viimeinen musta): peru.", "<b>ARP</b>: choH mach. <b>UNDO</b>: yIteq."),
            L("<b>SAVE</b>: tallenna. Pidä 2 sekuntia: tallenna ja <b>hyvää yötä</b>.", "<b>SAVE</b>: pol. cha' lup yI'uch: pol, <b>maj ram</b>.")]))

sec("Kuusi raitaa", "jav Hemey", ("gen", "tracks"))

sec("Äänet", "wabmey",
    ("p", L("<b>EDIT</b> avaa raidan SOUND-sivun, <b>EDIT</b> uudelleen SOUND 2:n. Nupit 1–4. Taulukot tulevat suoraan "
            "firmwaren koodista: tehdasarvot 0–127, PITCH puolisävelaskelina.",
            "<b>EDIT</b>: SOUND Hotlh; <b>EDIT</b> latlh: SOUND 2. SeH 1 – 4. ngoqvo' ghoS tetlhmey: ngo' mI' 0 – 127.")),
    ("p", L("EDIT² tarkoittaa: EDIT kahdesti. Jokaisen nupin voi lukita askelkohtaisesti (pidä askelta ja käännä) ja "
            "liikuttaa LFO:illa.", "EDIT²: EDIT cha'logh. SeH Hoch mIw Daq lock laH ('uch, DIngmoH), LFO vIHmoH laH.")),
    ("gen", "knobs"),
    ("gen", "mix"))

sec("Askeleet ja lukot", "mIwmey lock je",
    ("p", L("Napauta valkoista kosketinta: askel päälle tai pois. <b>Pidä</b> valkoista kosketinta ja käännä: nupit muokkaavat "
            "vain sitä askelta.", "leQ chIS yIyuv: mIw chu' pagh tam. leQ chIS <b>yI'uch</b>, yIDIngmoH: mIw'vam neH choH.")),
    ("ul", [L("<b>K1</b>: nuotti ±24 puolisävelaskelta", "<b>K1</b>: QoQ ±24"),
            L("<b>K2</b>: todennäköisyys, portaaton 1–100 %", "<b>K2</b>: Do', 1 – 100 %"),
            L("<b>K3</b>: aksentti; BASSO/HAPPO/PIIP: OFF, ACC, SLIDE, ACC+SLIDE", "<b>K3</b>: accent; BASSO HAPPO PIIP: SLIDE je"),
            L("<b>K4</b>: ratchet, 1–4 iskua askeleessa", "<b>K4</b>: ratchet, 1 – 4 mup"),
            L("<b>SELECT</b>: askel aikaisemmin tai myöhemmin", "<b>SELECT</b>: nom pagh tlhaw'"),
            L("<b>ALGORITHM</b>: trig-ehto 1:2 … 8:8, FILL, !FILL, PRE, !PRE, 1ST", "<b>ALGORITHM</b>: ra'ghom 1:2 … 8:8, FILL, PRE, 1ST"),
            L("<b>SEL</b>: poista askeleen siirto ja lukot", "<b>SEL</b>: vIH lock je teq")]),
    ("p", L("Askeleen oma ääni on <b>lukko</b>: pidä askelta EDIT-sivulla ja käännä. Lukitut arvot näkyvät vihreinä. "
            "32 lukkoa patternia kohden. ALGORITHM ilman pidettyä askelta: raidan loopin pituus 1–16 – HAPPO 14:ssä kickin "
            "16:ta vastaan kohtaa sen vasta seitsemän tahdin päästä.",
            "mIw wab: <b>lock</b>. EDIT Daq mIw yI'uch, yIDIngmoH; SuD lock mI'mey. 32 lock. ALGORITHM, mIw 'uchbe'lu'DI': loop "
            "'aD 1 – 16; HAPPO 14, kick 16: Soch bar veb ghom.")))

sec("LFO:t ja MOD", "LFO MOD je",
    ("p", L("Jokaisella raidalla on kaksi LFO:ta (<b>LFO</b>, uudelleen <b>LFO</b>) grooven tahdissa: RATE kuudestoistaosasta "
            "kuuteentoista tahtiin, DEPTH kumpaankin suuntaan, TARGET mikä tahansa ääninuppi tai LEVEL, PAN, DELAY, REVERB, "
            "SHAPE SINE, TRI, SAW, SQR, RAND. Kolmas painallus: <b>MOD</b>.",
            "He Hoch cha' LFO (<b>LFO</b>, <b>LFO</b> latlh): RATE, DEPTH, TARGET, SHAPE. wejDIch: <b>MOD</b>.")),
    ("ul", [L("<b>RESTART</b>: toisen raidan isku käynnistää LFO:t alusta – liike istuu grooveen.",
              "<b>RESTART</b>: He latlh mup LFO bI'reS."),
            L("<b>ENV</b>: kuinka kovaa lähde soi, liikuttaa tämän raidan kohdetta. POTKU HATTUn tasolle, DEPTH alle nollan: "
              "hatti väistää kickiä.", "<b>ENV</b>: Hal HoS He'vam TARGET vIHmoH. POTKU HATTU HoS, DEPTH pagh bIng: hat Haw'."),
            L("Pidä <b>LFO</b>: raidan ääni takaisin alkuun (undo palauttaa).", "<b>LFO</b> yI'uch: He wab bI'reS (undo cheghmoH).")]),
    ("sticker", L("Hullu happo: HAPPO, LFO 1 → TARGET CUTOFF, RATE 2 BAR, SHAPE TRI, DEPTH +40. Toinen LFO RESOon, RAND. "
                  "Naapurit soittavat poliisille.", "acid QIp: HAPPO, LFO 1 → CUTOFF, RATE 2 BAR, TRI, +40. LFO 2 → RESO, RAND. "
                  "jIlpu' bep.")))

sec("Euclid, linkit, ajoitus", "euclid, muv, poH",
    ("ul", [L("<b>SEQ</b>: EUCLID levittää iskut tasaisesti: HITS, ROTATE, CHANCE (portaaton), ACCENT (joka n:s tai RANDOM).",
              "<b>SEQ</b>: EUCLID: HITS, ROTATE, CHANCE, ACCENT (RANDOM je)."),
            L("<b>SEQ</b> kahdesti: LINK. Raita soi vain siellä missä lähde iskee (WITH), on hiljaa (GAPS) tai askeleen "
              "jälkeen (AFTER). FOLLOW: nuotit seuraavat toisen raidan sointuja.",
              "<b>SEQ</b> cha'logh: LINK. WITH, GAPS, AFTER. FOLLOW: chord tlha'."),
            L("<b>SEQ</b> kolmesti: TIMING. Yksittäinen isku tai koko raita aikaisemmin/myöhemmin, puoli kuudestoistaosaa.",
              "<b>SEQ</b> wejlogh: TIMING. mup pagh He Hoch: nom, tlhaw'.")]))

sec("Raidat 5 ja 6: neljä moottoria", "He 5 He 6 je: loS QuQ",
    ("p", L("<b>HOME</b> kahdesti: GROOVE 2. Nuppi 1 valitsee raidan 5 moottorin, nuppi 2 raidan 6. Uusi moottori tuo "
            "äänensä ja sääntöjensä mukaisen patternin ja tulee <b>mykistettynä</b>: SEL tuo sen mukaan, kun on aika.",
            "<b>HOME</b> cha'logh: GROOVE 2. SeH 1: He 5 QuQ; SeH 2: He 6. QuQ chu' wab pattern je qem, <b>tamlu'</b>: SEL QoQmoH.")),
    ("ul", [L("<b>PIIP</b>: äänipiiri, melodia kysymyksenä ja vastauksena soinnun sävelillä.", "<b>PIIP</b>: wab chip, bom: ghel, jang."),
            L("<b>KLIKKI</b>: ro:MINImalin klikit.", "<b>KLIKKI</b>: ro:MINImal click."),
            L("<b>STAB</b>: ro:MINImalin FM-soinnut, sävellajissa.", "<b>STAB</b>: ro:MINImal FM chord."),
            L("<b>SUHINA</b>: kohina, riserit ja laskut. LENGTH ääri-vasemmalla: <b>CLAP</b> iskuille 2 ja 4, ei koskaan "
              "ykköselle.", "<b>SUHINA</b>: chuS, riser, downlifter. LENGTH poS: <b>CLAP</b>, 2 4 je.")]),
    ("gen", "engines"))

sec("Pumppu ja säännöt", "pum ra'mey je",
    ("p", L("Pumppu on sydän. <b>BASSO</b> ei koskaan soi kickin päällä vaan sen takana: useimmiten <b>rulla</b> "
            "(potku, basso, basso, basso), muuten <b>laukka</b> (potku, tauko, basso, basso). Kickin jälkeinen kuudestoistaosa "
            "hiljaa, offbeat aksentilla, lyhyt häive, ja kick painaa sen kokonaan alas.",
            "pum tIq 'oH. <b>BASSO</b> kickDaq QoQbe', 'emDaq QoQ: <b>roll</b> (POTKU, BASSO, BASSO, BASSO) pagh "
            "<b>gallop</b> (POTKU, leS, BASSO, BASSO). offbeat accent, ruS nom, kick Hoch duck.")),
    ("ul", [L("<b>HAPPO</b> kävelee kahdeksan nuotin motiivia omalla loopillaan; slide ja aksentti 303:n tapaan.",
              "<b>HAPPO</b>: chorgh QoQ motif, loopDaj; slide accent je, 303 rur."),
            L("<b>PIIP</b> vastaa siellä, missä happo lepää: kysymys päättyy auki, vastaus tulee kotiin.",
              "<b>PIIP</b> jang acid leSDI': ghel poS, jang juHDaq chegh."),
            L("<b>HATTU</b> istuu offbeatilla, harvoin tuplana; vähän rullia.", "<b>HATTU</b> offbeat Daq; puS roll."),
            L("<b>B</b> muuntelee, <b>C</b> lisää fillin seuraavaan tahtiin, <b>D</b> siirtyy sukulaissävellajiin.",
              "<b>B</b> choH, <b>C</b> fill, <b>D</b> key retlh.")]))

sec("Sivut", "Hotlhmey", ("gen", "pages"),
    ("p", L("Pidetty <b>LFO</b>: raidan ääni alkuun. Pidetty <b>FX</b>: efektit alkuun. <b>SEL</b> + valkoinen 1–4: beat repeat.",
            "<b>LFO</b> yI'uch: He wab bI'reS. <b>FX</b> yI'uch: FX bI'reS. <b>SEL</b> + chIS 1 – 4: beat repeat.")))

sec("Patternit A–D, LAZY ja HARD", "pattern A – D, LAZY HARD je",
    ("p", L("<b>A</b> on groove. <b>B</b> soittaa A:n muunneltuna, <b>C</b> filleillä seuraavaan tahtiin, <b>D</b> "
            "sukulaissävellajissa. PRESETS vaihtaa; soitettaessa tahdin alussa. LAZY-tilassa B–D syntyvät A:sta itsestään, "
            "HARD-tilassa ne ovat sinun. GLOBAL 2: MODE, PLAY (LOOP, A-D, RANDOM), AIR (läsnäolo ja ilma), WORK (LIVE: moottori "
            "vaihtuu kaikissa patterneissa; PROD: vain muokattavassa).",
            "<b>A</b>: groove. <b>B</b>: choH, <b>C</b>: fill, <b>D</b>: key retlh. PRESETS: choH, bar veb. LAZY: B – D A vo' "
            "Dung; HARD: Dun. GLOBAL 2: MODE, PLAY, AIR, WORK (LIVE: pattern Hoch; PROD: wa'neH).")),
    ("p", L("Kun C:n kick pitää tauon tahdin lopussa, noppa heittää kerran kolmesta: kick muuttuu kaikissa patterneissa.",
            "C kick leSDI', wej wa' Do': kick choH pattern Hoch Daq.")))

sec("SLICE ja beat repeat", "SLICE beat repeat je",
    ("ul", [L("<b>FX</b> kolmesti: SLICE pilkkoo HATTUn, HAPPOn, PIIPin ja KLIKIn (ei koskaan POTKUa eikä BASSOa): GATE, "
              "STUTTER tai GRAIN (enintään kaksi raitaa). <b>FX</b> neljästi: SLICE-LFO.",
              "<b>FX</b> wejlogh: SLICE pe' (POTKU BASSO pe'be'): GATE, STUTTER, GRAIN. <b>FX</b> loSlogh: SLICE LFO."),
            L("<b>SEL</b> pohjassa + valkoinen 1–4: master toistaa iskua, kahdeksasosaa, kuudestoistaosaa tai 32-osaa, "
              "kunnes päästät irti.", "<b>SEL</b> yI'uch + chIS 1 – 4: master rap QoQmoH."),
            L("<b>FX</b> kahdesti: SIDECHAIN. Mykistä POTKU: pumppu jää – haamukick.", "<b>FX</b> cha'logh: SIDECHAIN. POTKU yItammoH: pum ratlh.")]))

sec("Koskettimet ja MIDI", "leQmey MIDI je",
    ("ul", [L("<b>REC</b>: koskettimet soittavat valittua raitaa, C4 perussävel, OCT−/OCT+ kaksi oktaavia.",
              "<b>REC</b>: leQmey He QoQmoH, C4 botlh."),
            L("MIDI-kanavat 1–6 soittavat kuutta raitaa; kanava 10 on rumpukartta (36 potku …).", "MIDI 1 – 6: jav He; MIDI 10: drum."),
            L("Start/stop vastaanotetaan; CLOCK päällä: kello USB:n yli.", "bI'reS mev je Hev; CLOCK: USB.")]))

sec("Reseptit", "ghojmeH ghItlh",
    ("ul", [L("<b>UFO laskeutuu:</b> raita 6 → SUHINA, NEW kunnes tulee riser, SWEEP oikealle, RESO ylös. Neljännen tahdin "
              "lopussa jokin laskeutuu.", "<b>UFO leng:</b> He 6 → SUHINA, NEW, SWEEP nIH, RESO Dung."),
            L("<b>Saunabasso:</b> BASSO CUTOFF alas, RESO 70, DRIVE ylös, AIR 0. Löylyä.", "<b>bIQ tuj bass:</b> BASSO CUTOFF bIng, RESO 70, DRIVE Dung."),
            L("<b>Poron piippaus:</b> PIIP, WAVE pulssi 12 %, ARP ylös, SPEED nopea, CRUSH vähän.", "<b>PIIP:</b> pulse 12 %, ARP Dung, SPEED nom."),
            L("<b>Klikkimetsä:</b> KLIKKI ALGORITHM 11, CHANCE 50 %, SCATTER täysille.", "<b>click Sor:</b> ALGORITHM 11, CHANCE 50 %, SCATTER Hoch."),
            L("<b>Taputa:</b> raita 5 → SUHINA (tulee clapina iskuille 2 ja 4). SEL tuo sen mukaan.", "<b>CLAP:</b> He 5 → SUHINA, 2 4 je. SEL.")]))

sec("UFO, uni ja hyvää yötä", "UFO, Qong, maj ram",
    ("ul", [L("<b>Käynnistys:</b> vihreä 8-bittinen UFO laskeutuu harmaaseen metsään, kamera zoomaa, UFO räjähtää ja "
              "pirstaleista nousee nimi, jinglen kera. Sitten kuva häivytetään sivuille.",
              "<b>bI'reS:</b> SuD 8-bit UFO Sor qIjHom Daq leng, Hop, jor; pong Hu', bom mach. HaSta Hotlh moj."),
            L("<b>Kaksi minuuttia koskematta:</b> nimi pumppaa kickin tahdissa, kirjain kerrallaan vihreänä.",
              "<b>cha' tup DachQo'DI':</b> pong pum kick rur, ngutlh wa' SuD."),
            L("<b>SAVE 2 s:</b> tallentaa, kuva kutistuu kuin vanhassa putkitelkkarissa, musiikki maiskahtaa pois ja "
              "<b>HYVÄÄ YÖTÄ</b> hehkuu. Sitten pimeää ja hiljaista, kunnes sammutat tai kosket.",
              "<b>SAVE cha' lup:</b> pol, HaSta luj, QoQ SoQ, <b>HYVÄÄ YÖTÄ</b> wov. Hurgh, tam, DachunDI' pagh DachDI'.")]))

sec("Usein kysyttyä", "ghel law'",
    ("ul", [L("<b>Voiko tällä soittaa humppaa?</b> Teknisesti kyllä. Moraalisesti emme vastaa.", "<b>humppa?</b> HIja'. 'ach jIjangbe'."),
            L("<b>Miksi UFO?</b> Koska psytrance. Seuraava kysymys.", "<b>qatlh UFO?</b> psytrance. ghel latlh."),
            L("<b>Missä on lehmä?</b> Sitä ei ole koskaan nähty uudestaan.", "<b>nuqDaq tangqa'?</b> not leghqa'lu'."),
            L("<b>Kuumeneeko FM-1?</b> Ei. Sinä kuumenet.", "<b>FM-1 tuj?</b> ghobe'. SoH tuj."),
            L("<b>Onko tämä valmis?</b> Ei. Se on kokeilu. Siksi se on hauska.", "<b>rIn'a'?</b> ghobe'. ghot 'oH. Quch.")]))

sec("Salaisuus", "pegh",
    ("sticker", L("Kaikkea ei kerrota. Sanotaan, että joka pitää tarpeeksi kauan kiinni maailmasta, näkee toisen. "
                  "Kaikki ei ole vihreää. 👽",
                  "Hoch jatlhbe'lu'. qo' Da'uchtaHvIS nI', qo' latlh Dalegh. SuD Hoch ghobe'. 👽")))

sec("Pientä präntättyä", "ghItlh mach",
    ("ul", [L("suom1saundi on kokeilu: jos FM-1:n aika loppuu, se lähtee ensimmäisenä (ROMI_SUOMI=0).",
              "suom1saundi ghot 'oH: poH HutlhDI', wa'DIch mej (ROMI_SUOMI=0)."),
            L("Ääntä, ajoitusta ja kuormaa oikealla laitteella ei ole vielä mitattu.", "jan teH wab, poH, 'ar je juvbe'lu'."),
            L("Alkuperä: github.com/g0rst/suom1saundi. Rakennettu fm1-basen ja felucca-bsp:n päälle. MIT-lisenssi. Ei M-VAVEn kanssa yhteydessä.",
              "ngoQ: github.com/g0rst/suom1saundi. fm1-base felucca-bsp je. MIT. M-VAVE muvbe'.")]))


# -------------------------------------------------------------------------------- generated from the code ---
def gen(name, lang):
    trk = F["tracks"]["suomi"]
    if name == "tracks":
        rows = [(f"{'musta' if lang == 'fi' else 'qIj'} {t + 1}", f"<b>{trk[t]}</b>", ROLE[t][0], ROLE[t][1 if lang == "fi" else 2])
                for t in range(6)]
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
                    d = DESC.get(nm, {}).get(n, ("", ""))
                    rows.append((f"EDIT{page}&nbsp;K{k + 1}", f"<b>{n}</b>", str(v - 24) if n == "PITCH" else str(v),
                                 html.escape(d[0 if lang == "fi" else 1])))
            out.append(f'<h3 id="{lang}-{nm.lower()}">{nm}</h3>' + table(UI["th_knob"][lang], rows))
        return "".join(out)
    if name == "mix":
        rows = [(f"<b>{trk[t]}</b>", pct(F["su_def"][t][4]), pan(F["su_def"][t][5]), pct(F["su_def"][t][6]),
                 pct(F["su_def"][t][7]), str(F["su_glide"][t])) for t in range(6)]
        return f'<h3>{"Miksaus tehtaalta" if lang == "fi" else "ngo DuD"}</h3>' + table(UI["th_mix"][lang], rows)
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
        fi = lang == "fi"
        rows = [("HOME", f"{pg[0]} · {pg[15]}", "TEMPO, SWING, DRIFT, DUCK · " + ("raitojen 5/6 moottori, FILTER, BASS" if fi else "He 5/6 QuQ, FILTER, BASS")),
                ("EDIT", f"{pg[1]} · {pg[11]}", "SOUND, SOUND 2"),
                ("ENV", pg[2], "LEVEL, PAN, DELAY, REVERB"),
                ("FX", f"{pg[3]} · {pg[6]} · {pg[14]} · {pg[16]}", "DELAY, REVERB · SIDECHAIN · SLICE · SLICE LFO"),
                ("GLO", f"{pg[4]} · {pg[12]}", ("pohjasävel, asteikko, MIDI-kello, CHAIN · MODE, PLAY, AIR, WORK" if fi
                                                else "QoQ botlh, scale, clock, CHAIN · MODE, PLAY, AIR, WORK")),
                ("SEQ", f"{pg[5]} · {pg[7]} · {pg[8]}", "EUCLID · LINK · TIMING"),
                ("LFO", f"{pg[9]} · {pg[10]} · {pg[13]}", "LFO 1 · LFO 2 · MOD")]
        return table(UI["th_page"][lang], [(f"<b>{a}</b>", b, c) for a, b, c in rows])
    raise KeyError(name)


def table(head, rows):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


# ------------------------------------------------------------------------------------------- pixel art ---
UFO = ["    .ooo.    ", "   .ooooo.   ", "  GGGGGGGGG  ", " GGGGGGGGGGGG", "GLGGLGGLGGLGG", "  ddddddddd  ", "   d     d   "]
COW = ["  wwwww ", " wkwwkww", "wwwwwwww", "wkkwwwkw", " w w w w"]
COL = {"o": "#b4ffc8", ".": "#5aaa78", "G": "#3cdc50", "L": "#fff078", "d": "#1e6e32", "w": "#ffffff", "k": "#111111"}


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


def render(lang):
    toc, body = [], []
    small = sprite(UFO, 3)
    for i, (head, blocks) in enumerate(S):
        hid = f"{lang}-{i + 1}"
        toc.append(f'<li><a href="#{hid}">{head[lang]}</a></li>')
        body.append(f'<h2 id="{hid}">{small}{head[lang]}</h2>')
        for b in blocks:
            if b[0] == "p":
                body.append(f"<p>{b[1][lang]}</p>")
            elif b[0] == "sticker":
                body.append(f'<aside class="sticker">{b[1][lang]}</aside>')
            elif b[0] == "ul":
                body.append("<ul>" + "".join(f"<li>{x[lang]}</li>" for x in b[1]) + "</ul>")
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
  <p class="pix">{"8-BIT · PSY · UFO" if l == "fi" else "8-BIT · psy · UFO"}</p>
  <div class="tag">{UI["tag"][l]} {F["commit"]} <span class="blink">{UI["new"][l]}</span></div>
  <nav class="langs" aria-label="kieli"><a href="#fi" data-l="fi">suomi</a><a href="#tlh" data-l="tlh">tlhIngan Hol</a><a href="index.html">⌂ {UI["home"][l]}</a></nav>
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
<title>suom1saundi – käyttöohje · lo'meH paq</title>
<!-- written by manual/suomi.py from the firmware's code: do not edit by hand -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&family=Press+Start+2P&display=swap">
<style>{CSS}</style>
</head>
<body>
{"".join(arts)}
<script>
(function () {{
  var langs = ["fi", "tlh"];
  function pick() {{
    var h = location.hash.replace("#", "").split("-")[0];
    if (langs.indexOf(h) >= 0) return h;
    return (navigator.language || "fi").slice(0, 3).toLowerCase() === "tlh" ? "tlh" : "fi";
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
