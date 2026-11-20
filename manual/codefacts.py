# SPDX-License-Identifier: MIT
"""What the manuals read from the firmware's code, so their tables cannot drift from it: the tracks' names, the knobs'
names, the factory values of both styles and of the engines of tracks 5 and 6, the pages, the scales, the start
settings. Standard library only; used by manual/build.py (ro:MINImal), manual/suomi.py (suom1saundi),
manual/fre3tek.py and manual/schr4nz.py."""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORE = ROOT / "app" / "core"


def _src(name):
    return (CORE / name).read_text(encoding="utf-8")


def _block(src, start):
    """the text of the initialiser that follows `start` (from its first { to the matching })"""
    i = src.index(start)
    i = src.index("{", i)
    depth, j = 0, i
    while True:
        c = src[j]
        depth += c == "{"
        depth -= c == "}"
        if depth == 0:
            return src[i:j + 1]
        j += 1


def _strings(block):
    return re.findall(r'"([^"]*)"', block)


def _rows(block):
    """the innermost {...} rows of numbers"""
    return [[int(v) for v in r.split(",") if v.strip()] for r in re.findall(r"\{\s*(-?\d+(?:\s*,\s*-?\d+)*)\s*,?\s*\}", block)]


def facts():
    romi, gen, tek, sch = _src("romi.c"), _src("suomi_gen.inc"), _src("tek_gen.inc"), _src("sch_gen.inc")
    tracks = _strings(_block(romi, "TRACK_NAMES[4][ROMI_TRACKS] ="))
    engines = _strings(_block(romi, "ENG_NAMES[4][ROMI_NENG] ="))
    sound = _strings(_block(romi, "SOUND_NAMES[4][ROMI_TRACKS][4] ="))
    sound2 = _strings(_block(romi, "SOUND2_NAMES[4][ROMI_TRACKS][4] ="))
    eng_sound = _strings(_block(romi, "ENG_SOUND[ROMI_NENG][2][4] ="))
    pages = _strings(_block(romi, "PAGE_NAME[ROMI_NPAGES] ="))
    romi_def = _rows(_block(romi, "static const uint8_t DEF[ROMI_TRACKS][8] ="))
    romi_q = _rows(_block(romi, "static const uint8_t Q[ROMI_TRACKS][4] ="))
    eng_def = _rows(_block(romi, "static const uint8_t D[ROMI_NENG][13] ="))
    su_def = _rows(_block(gen, "static const uint8_t DEF[ROMI_TRACKS][9] ="))
    su_glide = _rows(_block(gen, "static const uint8_t GLIDE[ROMI_TRACKS] ="))[0]
    tek_def = _rows(_block(tek, "static const uint8_t DEF[4][9] ="))
    tek_sc = _rows(_block(tek, "static const uint8_t SC[4] ="))[0]
    sch_def = _rows(_block(sch, "static const uint8_t DEF[4][9] ="))
    sch_sc = _rows(_block(sch, "static const uint8_t SC[4] ="))[0]
    scales = re.findall(r"/\*\s*([a-z ]+?)(?::[^*]*)?\s*\*/", _block(romi, "static const uint8_t SCALES[NSCALES][7] ="))
    style = {}
    m = re.search(r"if \(SCH\) \{\s*/\*.*?\*/(.*?)\} else if \(TEK\) \{\s*/\*[^*]*\*/(.*?)\} else if \(STYLE\) \{\s*/\*[^*]*\*/(.*?)\} else \{(.*?)\}",
                  _block(romi, "static void prj_style_defaults(void)"), re.S)
    for k, part in (("sch", m.group(1)), ("tek", m.group(2)), ("suomi", m.group(3)), ("romi", m.group(4))):
        style[k] = {a: int(b) for a, b in re.findall(r"p->(\w+)\s*=\s*(\d+);", part)}
    n = 6
    S = ("romi", "suomi", "tek", "sch")
    try:
        rev = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h %cs"], capture_output=True,
                             text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        rev = ["", ""]
    store = int(re.search(r"#define ROMI_VERSION (\d+)u", _src("romi.h")).group(1))
    return {
        "tracks": {k: tracks[j * n:(j + 1) * n] for j, k in enumerate(S)},
        "engines": {k: engines[j * 4:(j + 1) * 4] for j, k in enumerate(S)},
        "sound": {k: [sound[(j * n + i) * 4:(j * n + i) * 4 + 4] for i in range(n)] for j, k in enumerate(S)},
        "sound2": {k: [sound2[(j * n + i) * 4:(j * n + i) * 4 + 4] for i in range(n)] for j, k in enumerate(S)},
        "tek_def": tek_def, "tek_sc": tek_sc, "sch_def": sch_def, "sch_sc": sch_sc,
        "eng_sound": [[eng_sound[e * 8:e * 8 + 4], eng_sound[e * 8 + 4:e * 8 + 8]] for e in range(len(eng_sound) // 8)],
        "pages": pages,
        "romi_def": romi_def, "romi_q": romi_q, "eng_def": eng_def,
        "su_def": su_def, "su_glide": su_glide,
        "scales": scales, "style": style,
        "commit": rev[0] if rev else "", "date": rev[1] if len(rev) > 1 else "", "store": store,
    }


def pct(v):
    """a 0..127 amount as the screen shows it"""
    return f"{v * 100 // 127} %"


def pan(v):
    return "C" if 62 <= v <= 66 else (f"L{64 - v}" if v < 64 else f"R{v - 64}")


if __name__ == "__main__":
    import json
    print(json.dumps(facts(), indent=1))
