/* SPDX-License-Identifier: MIT
 * ro:MINImal core: six fixed voices, a polymetric probability sequencer, a groove generator, drift, delay,
 * reverb, and the whole user interface drawn into 240 x 48 strips. See romi.h. */
#include "romi.h"

#if defined ROMI_FM1_POOL && !defined PLAT_HOST   /* the FM-1: big buffers go in fm1-base's .pool region */
#define POOL __attribute__((section(".pool")))
#else
#define POOL
#endif

#define INV_SR (1.0f / (float)ROMI_SR)
#define DLY_LEN 16384u                  /* mono delay line, int16: 0.37 s */

/* ------------------------------------------------------------------ math --- */
static float sintab[1025];

static void sin_init(void)
{
    int i;
    for (i = 0; i <= 256; i++) {        /* a quarter by Taylor series, the rest by symmetry */
        float x = (float)i * (6.2831853f / 1024.0f), x2 = x * x;
        float s = x * (1.0f - x2 / 6.0f * (1.0f - x2 / 20.0f * (1.0f - x2 / 42.0f * (1.0f - x2 / 72.0f))));
        sintab[i] = s;
        sintab[512 - i] = s;
        sintab[512 + i] = -s;
        sintab[1024 - i] = -s;
    }
}

static inline float fsin(float turns)   /* sine of a phase in turns, any value */
{
    float x;
    int i;
    turns -= (float)(int)turns;
    if (turns < 0.0f)
        turns += 1.0f;
    x = turns * 1024.0f;
    i = (int)x;
    return sintab[i] + (sintab[i + 1] - sintab[i]) * (x - (float)i);
}

static float fexp2(float x)
{
    union { uint32_t u; float f; } b;
    int i;
    float f;
    if (x < -60.0f)
        return 0.0f;
    if (x > 60.0f)
        x = 60.0f;
    i = (int)x;
    if ((float)i > x)
        i--;
    f = x - (float)i;
    b.u = (uint32_t)(i + 127) << 23;
    return b.f * (1.0f + f * (0.6931472f + f * (0.2402265f + f * (0.0555041f + f * (0.0096181f + f * 0.0013333f)))));
}

static float note_hz(float note) { return 440.0f * fexp2((note - 69.0f) * (1.0f / 12.0f)); }
/* the per-sample factor of a decay with time constant tau seconds */
static float decay_coef(float tau) { return fexp2(-1.442695f * INV_SR / tau); }
/* 0..127 on an exponential scale from lo to lo * 2^octaves */
static float pmap(float p, float lo, float octaves) { return lo * fexp2(p * (1.0f / 127.0f) * octaves); }
static inline float clip1(float x)      /* soft: linear near 0, 1 at 1.5 and beyond */
{
    if (x > 1.5f)
        return 1.0f;
    if (x < -1.5f)
        return -1.0f;
    return x - x * x * x * (4.0f / 27.0f);
}

static inline uint32_t xs32(uint32_t *s)
{
    uint32_t x = *s;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return *s = x;
}
static inline float frand(uint32_t *s) { return (float)(xs32(s) >> 8) * (1.0f / 16777216.0f); }   /* 0..1 */
static inline float brand(uint32_t *s) { return frand(s) * 2.0f - 1.0f; }                           /* -1..1 */

/* ----------------------------------------------------------------- state --- */
typedef struct { float gl, gr, sd, sr; } bus_t;
typedef struct { float att, attc, g, norm, held, levels; int32_t hold, cnt; } shape_t;   /* a track's SOUND 2 state */

static struct {
    romi_project_t prj;
    /* audio */
    uint32_t rng;                       /* audio context only */
    volatile uint8_t playing, want_play, want_stop;
    volatile uint8_t pending_pat;       /* 0xFF: none */
    float clk;                          /* samples to the next step */
    float cur_dur;                      /* the current step's length in samples */
    float songpos;                      /* steps since PLAY (with the fraction), for the LFOs: set each block */
    float mclk;                         /* samples to the next MIDI clock */
    uint32_t gstep;                     /* steps since start */
    volatile uint8_t pos[ROMI_TRACKS];  /* each track's step, for the screen */
    volatile uint32_t gstep_ui;
    float drift[ROMI_TRACKS][2];
    struct { int32_t delay, gap; int8_t note; uint8_t on, acc, rep, si; float vel; } pend[ROMI_TRACKS][2];
    uint8_t early[ROMI_TRACKS];         /* this step was already scheduled from the one before: it plays early */
    uint8_t hit[ROMI_TRACKS], hit_prev[ROMI_TRACKS], hit_early[ROMI_TRACKS];   /* did the track's step fire: now,
                                         * a step ago, and the early one's answer */
    volatile uint32_t hits[ROMI_TRACKS];
    volatile int8_t last_note[ROMI_TRACKS];
    volatile uint8_t tq[16][3];         /* triggers from the main loop: track, note + 64, velocity */
    volatile uint8_t tq_w, tq_r;
    volatile uint8_t rt[16];            /* MIDI real-time bytes out */
    volatile uint8_t rt_w, rt_r;
    volatile uint8_t flash[ROMI_TRACKS];   /* a trigger happened: the screen shows it */
    bus_t bus[ROMI_TRACKS];
    struct { float ph, amp, ac, penv, pc, f0, pd, drive, norm, vel, clickamt; int32_t click; } kick;
    struct { float ph, mph, f, ft, gc, amp, ac, ienv, ic, idx, ratio, att, vel; } sub;
    struct { float ph, mph, ph2, mph2, f, amp, ac, metal, lp, vel; } hat;
    struct { float ph, mph, f, benv, bc, bend, amp, ac, ienv, ic, idx, ratio, vel; } perc;
    struct { float ph[3], f[3], amp, ac, ienv, ic, idx, lp, vel; } stab;
    struct { float amp, ac, lp, bp, fc, q, pan, vel; } click;
    shape_t shape[ROMI_TRACKS];
    float duck_env;
    uint32_t dly_w;
    float dly_lp;
    uint32_t comb_i[4], ap_i[4];
    float comb_f[4];
    /* ui */
    uint32_t ui_rng;
    uint8_t track, page, keys_mode, unsaved, save_wanted;
    int8_t octave;
    volatile int8_t solo;               /* the one track heard, -1: all */
    uint32_t sel_t;                     /* SEL went down (0: not held) */
    uint8_t sel_used;                   /* track keys were pressed while SEL was held */
    uint32_t new_t;                     /* NEW went down (0: not held, or its hold already acted) */
    uint8_t cursor;                     /* the TIMING page: the step its first knob moves */
    uint32_t saved_sum[ROMI_NOBJ];      /* each object's sum as last loaded or saved (0: never) */
    volatile uint8_t evolve;            /* the chain came round in EVOLVE: new variations wanted */
    uint8_t base_changed;               /* A changed: B..D to be made again */
    romi_pattern_t aside[3];            /* HARD's B..D, kept while LAZY plays its own (and loaded there in LAZY) */
    uint8_t aside_ok;                   /* bit k: aside[k] holds a HARD pattern */
    uint8_t density;                    /* the generator's: 0 sparse, 1 medium, 2 busy (set by a whole NEW) */
    uint8_t eu_armed;                   /* the next turn on the EUCLID page keeps an undo first */
    uint32_t btn, keys, now;
    uint8_t step_edited;                /* a held step was edited: its release does not toggle it */
    uint32_t dirty;
    uint32_t seen_gstep;
    char msg[2][20];
    uint32_t msg_until;
    romi_pattern_t undo;
    uint8_t undo_pat, undo_ok;
} R;

static int16_t dly_buf[DLY_LEN] POOL;
static const uint16_t COMB_LEN[4] = {1116, 1277, 1422, 1557};
static const uint16_t AP_LEN[4] = {556, 441, 579, 464};   /* left: 0, 1; right: 2, 3 */
static int16_t comb_buf[4][1557] POOL;   /* the reverb's lines, 16 bit: 1.0 is 8192 (four times headroom) */
static int16_t ap_buf[4][579] POOL;
#define RV_IN (1.0f / 8192.0f)
static inline int16_t rv_out(float x)
{
    x *= 8192.0f;
    return (int16_t)(x > 32767.0f ? 32767 : x < -32768.0f ? -32768 : (int32_t)x);
}

static const uint8_t SCALES[4][7] = {
    {0, 2, 3, 5, 7, 8, 10},             /* minor */
    {0, 2, 3, 5, 7, 9, 10},             /* dorian */
    {0, 1, 3, 5, 7, 8, 10},             /* phrygian */
    {0, 3, 5, 7, 10, 12, 15},           /* minor pentatonic */
};
static const int8_t CHORDS[5][3] = {{0, 3, 7}, {0, 3, 10}, {3, 10, 14}, {0, 5, 10}, {0, 7, 12}};
static const float PERC_RATIO[8] = {1.0f, 1.41f, 1.73f, 2.0f, 2.76f, 3.5f, 4.07f, 5.33f};

#define PAT (&R.prj.pat[R.prj.cur_pat])   /* the pattern playing */
#define BASE (&R.prj.pat[0])                /* pattern A: in LAZY the one edited, B..D are made from it */
#define EDT (R.prj.mode ? PAT : BASE)       /* the pattern the panel edits: A (LAZY), the one playing (HARD) */

/* ---------------------------------------------------------------- voices --- */
/* a parameter with its drift: d in -1..1, scaled by the project's drift amount, up to +-24 of 127 */
static float drifted(int t, int which, uint8_t p)
{
    float v = (float)p + R.drift[t][which] * (float)R.prj.drift * (24.0f / 127.0f);
    return v < 0.0f ? 0.0f : v > 127.0f ? 127.0f : v;
}

/* ---- the LFOs: two a track, in time with the groove, cheap (evaluated once a block or once a hit) ----
 * Their phase comes from the song position in steps (R.songpos, set each block), so they line up with the bars
 * and start from zero at PLAY. Stopped, they rest at that position. */
static const uint16_t LFO_STEPS[9] = {1, 2, 4, 8, 16, 32, 64, 128, 256};

static float lfo_wave(const romi_lfo_t *l, int t, int k)
{
    float len = (float)LFO_STEPS[l->rate > 8 ? 8 : l->rate], c = R.songpos / len, ph;
    uint32_t cyc = (uint32_t)c, h;
    ph = c - (float)cyc;
    switch (l->shape) {
    case 1: return ph < 0.5f ? 4.0f * ph - 1.0f : 3.0f - 4.0f * ph;
    case 2: return 1.0f - 2.0f * ph;
    case 3: return ph < 0.5f ? 1.0f : -1.0f;
    case 4:                             /* random: a value a cycle, the same at the same place in the song */
        h = (cyc + 1u) * 2654435761u ^ (uint32_t)(t * 97 + k * 31 + 1) * 40503u;
        h ^= h >> 15;
        h *= 2246822519u;
        h ^= h >> 13;
        return (float)(h >> 8) * (2.0f / 16777216.0f) - 1.0f;
    default: return fsin(ph);
    }
}

/* the sum of the track's LFOs aimed at target, in 0..127 units */
static float lfo_offset(int t, int target)
{
    const romi_track_t *tr = &PAT->tr[t];
    float o = 0.0f;
    int k;
    for (k = 0; k < ROMI_LFOS; k++)
        if (tr->lfo[k].depth && tr->lfo[k].target == target)
            o += (float)tr->lfo[k].depth * lfo_wave(&tr->lfo[k], t, k);
    return o;
}

static float lim127(float v) { return v < 0.0f ? 0.0f : v > 127.0f ? 127.0f : v; }

static void bus_update(int t)
{
    const romi_track_t *tr = &PAT->tr[t];
    float lev = lim127((float)tr->level + lfo_offset(t, 4)) * (1.0f / 127.0f);
    float pan = lim127((float)tr->pan + lfo_offset(t, 5)) * (1.0f / 127.0f);
    float l = 2.0f * (1.0f - pan), r = 2.0f * pan;
    lev *= lev;
    R.bus[t].gl = lev * (l > 1.0f ? 1.0f : l);
    R.bus[t].gr = lev * (r > 1.0f ? 1.0f : r);
    R.bus[t].sd = lev * lim127((float)tr->dly + lfo_offset(t, 6)) * (1.0f / 127.0f);
    R.bus[t].sr = lev * lim127((float)tr->rev + lfo_offset(t, 7)) * (1.0f / 127.0f);
}

/* lock: the step's own values for the four sound parameters (0: the track's), or NULL */
static void trig(int t, int note, float vel, int acc, const uint8_t *lock)
{
    const romi_track_t *tr = &PAT->tr[t];
    uint8_t p[4], q[4];
    int li, pt;
    float root = (float)R.prj.root, x;
    int stab_quiet = R.stab.amp < 0.05f;
    for (li = 0; li < 4; li++) {          /* the step's lock or the track's value, then the LFOs on it */
        p[li] = lock && lock[li] ? (uint8_t)(lock[li] - 1u) : tr->p[li];
        p[li] = (uint8_t)lim127((float)p[li] + lfo_offset(t, li));
        q[li] = lock && lock[4 + li] ? (uint8_t)(lock[4 + li] - 1u) : tr->q[li];
        x = (float)q[li] + lfo_offset(t, 8 + li) * (li ? 1.0f : 48.0f / 127.0f);   /* (pitch: 48 steps, not 127) */
        q[li] = (uint8_t)(li ? lim127(x) : x < 0.0f ? 0.0f : x > 48.0f ? 48.0f : x);
    }
    pt = (int)q[0] - 24;                  /* SOUND 2 PITCH: the whole track, in semitones */
    if (t != ROMI_HAT)
        note += pt;
    /* SOUND 2: attack (hat, stab, click), drive (all but the kick: its own is on SOUND), crush (all) */
    {
        shape_t *sh = &R.shape[t];
        int has_att = t == ROMI_HAT || t == ROMI_STAB || t == ROMI_CLICK;
        float g = t == ROMI_KICK ? 1.0f : 1.0f + (float)q[2] * (6.0f / 127.0f);
        if (has_att && q[1]) {
            if (t != ROMI_STAB || stab_quiet)
                sh->att = 0.0f;
            sh->attc = 1.0f - decay_coef(0.0005f * fexp2((float)q[1] * (7.3f / 127.0f)));
        } else {
            sh->att = 1.0f;
            sh->attc = 1.0f;
        }
        sh->g = g;
        sh->norm = g > 1.001f ? 1.0f / clip1(g) : 1.0f;
        sh->hold = q[3] ? 1 + (int32_t)q[3] * 15 / 127 : 1;
        sh->levels = q[3] ? fexp2(12.0f - (float)q[3] * (10.0f / 127.0f)) : 0.0f;
    }
    bus_update(t);
    R.flash[t] = 1;
    R.last_note[t] = (int8_t)note;
    if (t == (int)R.prj.sc_src)
        R.duck_env = 1.0f;
    switch (t) {
    case ROMI_KICK: {
        float g = 1.0f + (float)p[3] * (5.0f / 127.0f);
        R.kick.f0 = pmap((float)p[0], 36.0f, 1.0f) * fexp2((float)note * (1.0f / 12.0f));
        R.kick.ac = decay_coef(pmap(drifted(t, 0, p[1]), 0.05f, 3.0f));
        R.kick.pd = drifted(t, 1, p[2]) * (7.0f / 127.0f);
        R.kick.pc = decay_coef(pmap((float)q[2], 0.006f, 3.0f));   /* SOUND 2: P.TIME */
        R.kick.clickamt = (float)q[1] * (0.6f / 127.0f);          /* SOUND 2: CLICK */
        R.kick.penv = 1.0f;
        R.kick.drive = g;
        R.kick.norm = 1.0f / clip1(g);
        R.kick.amp = 1.0f;
        R.kick.ph = 0.0f;
        R.kick.click = 90;
        R.kick.vel = vel;
        break;
    }
    case ROMI_SUB: {
        int legato = R.sub.amp > 0.05f;
        R.sub.ft = note_hz(root + (float)note);
        R.sub.gc = p[3] ? 1.0f - decay_coef(pmap((float)p[3], 0.002f, 6.0f)) : 1.0f;
        if (!legato) {
            R.sub.f = R.sub.ft;
            R.sub.ph = R.sub.mph = 0.0f;
            R.sub.att = 0.0f;
        }
        R.sub.ac = decay_coef(pmap(drifted(t, 0, p[0]), 0.04f, 4.0f));
        R.sub.idx = drifted(t, 1, p[1]) * (0.45f / 127.0f) * (acc ? 1.4f : 1.0f);
        R.sub.ic = decay_coef(pmap((float)q[1], 0.01f, 4.0f));   /* SOUND 2: FM.TIME */
        R.sub.ienv = 1.0f;
        R.sub.ratio = (float)(1 + p[2] * 3 / 128);
        R.sub.amp = 1.0f;
        R.sub.vel = vel;
        break;
    }
    case ROMI_HAT: {
        float open = acc ? 1.0f + (float)p[3] * (7.0f / 127.0f) : 1.0f;
        R.hat.f = pmap((float)p[1], 3000.0f, 1.6f) * fexp2((float)note * (1.0f / 24.0f) + (float)pt * (1.0f / 12.0f));
        R.hat.ac = decay_coef(pmap(drifted(t, 0, p[0]), 0.006f, 4.0f) * open);
        R.hat.metal = drifted(t, 1, p[2]) * (1.0f / 127.0f);
        R.hat.amp = 1.0f;
        R.hat.vel = vel;
        break;
    }
    case ROMI_PERC:
        R.perc.f = note_hz(root + 36.0f + (float)note);
        R.perc.ac = decay_coef(pmap(drifted(t, 0, p[0]), 0.012f, 4.5f));
        R.perc.idx = drifted(t, 1, p[1]) * (0.6f / 127.0f);
        R.perc.ic = decay_coef(0.03f);
        R.perc.ienv = 1.0f;
        R.perc.ratio = PERC_RATIO[p[2] >> 4];
        R.perc.bend = (float)p[3] * (2.0f / 127.0f);
        R.perc.bc = decay_coef(pmap((float)q[1], 0.003f, 4.0f));   /* SOUND 2: B.TIME */
        R.perc.benv = 1.0f;
        R.perc.amp = 1.0f;
        R.perc.ph = R.perc.mph = 0.0f;
        R.perc.vel = vel;
        break;
    case ROMI_STAB: {
        const int8_t *ch = CHORDS[p[2] * 5 / 128];
        float det = (float)p[3] * (0.008f / 127.0f);
        int i;
        for (i = 0; i < 3; i++)
            R.stab.f[i] = note_hz(root + 24.0f + (float)note + (float)ch[i]) * (1.0f + det * (float)(i - 1));
        R.stab.ac = decay_coef(pmap(drifted(t, 0, p[0]), 0.03f, 4.5f));
        R.stab.idx = drifted(t, 1, p[1]) * (0.5f / 127.0f);
        R.stab.ic = decay_coef(pmap((float)p[0], 0.02f, 4.0f));
        R.stab.ienv = 1.0f;
        R.stab.amp = 1.0f;
        R.stab.vel = vel;
        break;
    }
    default: {
        float sc = (float)p[3] * (1.0f / 127.0f);
        float f = pmap((float)p[1], 400.0f, 3.8f) * fexp2((float)note * (1.0f / 12.0f) + brand(&R.rng) * sc * 1.5f);
        float fc = 6.2831853f * f * INV_SR;
        R.click.fc = fc > 0.9f ? 0.9f : fc;
        R.click.q = 1.0f - (float)p[2] * (0.94f / 127.0f);
        R.click.ac = decay_coef(pmap(drifted(t, 0, p[0]), 0.0008f, 6.0f));
        R.click.pan = 0.5f + brand(&R.rng) * sc * 0.5f;
        R.click.amp = 1.0f;
        R.click.vel = vel;
        break;
    }
    }
}

void romi_panic(void)
{
    uint32_t i, k;
    R.kick.amp = R.sub.amp = R.hat.amp = R.perc.amp = R.stab.amp = R.click.amp = 0.0f;
    R.duck_env = 0.0f;
    for (i = 0; i < ROMI_TRACKS; i++)
        R.pend[i][0].on = R.pend[i][1].on = R.early[i] = 0;
    for (i = 0; i < DLY_LEN; i++)
        dly_buf[i] = 0;
    for (k = 0; k < 4; k++) {
        for (i = 0; i < COMB_LEN[k]; i++)
            comb_buf[k][i] = 0;
        for (i = 0; i < AP_LEN[k]; i++)
            ap_buf[k][i] = 0;
        R.comb_f[k] = 0.0f;
    }
    R.dly_lp = 0.0f;
}

/* ------------------------------------------------------------- sequencer --- */
static void rt_push(uint8_t b)
{
    uint8_t w = R.rt_w;
    if (!R.prj.clock_out || (uint8_t)((w + 1u) & 15u) == R.rt_r)
        return;
    R.rt[w] = b;
    R.rt_w = (uint8_t)((w + 1u) & 15u);
}

int romi_midi_rt_pop(void)
{
    uint8_t r = R.rt_r, b;
    if (r == R.rt_w)
        return -1;
    b = R.rt[r];
    R.rt_r = (uint8_t)((r + 1u) & 15u);
    return b;
}

static float step_samples(void) { return (float)ROMI_SR * 15.0f / (float)R.prj.bpm; }

/* a step's microtiming: its own shift and its track's, together at most half a sixteenth either way (an early
 * step is scheduled one step ahead, and at full swing the short sixteenth is only that long) */
static int eff_shift(const romi_track_t *tr, uint32_t pos)
{
    int v = tr->step[pos].shift + tr->tshift;
    return v < -8 ? -8 : v > 8 ? 8 : v;
}

/* FOLLOW: the transposition the source track's harmony gives at global step g. The harmony is the note of the
 * source's latest set step at or before g in its own loop (wrapping), whether it sounded or not (its chance, a
 * mute): so the harmony is the written one and stays put. Folded to a fifth either way of the base. */
static int harmony(int src, uint32_t g)
{
    const romi_track_t *st = &PAT->tr[src];
    uint32_t len = st->len ? st->len : 1u, pos = g % len, k;
    for (k = 0; k < len; k++) {
        const romi_step_t *sp = &st->step[(pos + len - k) % len];
        if (sp->flags & ROMI_ST_ON) {
            int n = ((sp->note % 12) + 12) % 12;
            return n > 6 ? n - 12 : n;
        }
    }
    return 0;
}

/* one step of a track, to play base samples from now (plus its own shift); dur: that step's length.
 * Returns 1 if the step fired: a muted track's counts too (the sidechain and the LINK page follow it unheard) */
static int schedule(int t, uint32_t pos, float base, float dur, uint32_t g)
{
    static const uint8_t PROB[4] = {100, 75, 50, 25};
    const romi_track_t *tr = &PAT->tr[t];
    romi_step_t st = tr->step[pos];
    float drift = (float)R.prj.drift * (1.0f / 127.0f), d;
    int k;
    if (!(st.flags & ROMI_ST_ON))
        return 0;
    if (xs32(&R.rng) % 100u >= PROB[ROMI_ST_PROB(st.flags)])
        return 0;
    if (tr->mute || (R.solo >= 0 && R.solo != t)) {
        if (t == (int)R.prj.sc_src)     /* the sidechain's source, muted: it still ducks (a ghost kick) */
            R.duck_env = 1.0f;
        return 1;
    }
    k = !R.pend[t][0].on ? 0 : !R.pend[t][1].on ? 1 : 0;
    R.pend[t][k].note = st.note;
    if (tr->follow && tr->follow - 1 != t) {
        int n = st.note + harmony(tr->follow - 1, g);
        R.pend[t][k].note = (int8_t)(n < -48 ? -48 : n > 48 ? 48 : n);
    }
    R.pend[t][k].si = (uint8_t)pos;
    R.pend[t][k].acc = (st.flags & ROMI_ST_ACC) != 0;
    R.pend[t][k].vel = (R.pend[t][k].acc ? 1.0f : 0.62f) * (1.0f + brand(&R.rng) * drift * 0.2f);
    d = base + (float)eff_shift(tr, pos) * step_samples() * (1.0f / 16.0f);
    if (t != ROMI_KICK)                 /* the kick is the grid; the rest may come up to 4 ms late with the drift */
        d += frand(&R.rng) * drift * 0.004f * (float)ROMI_SR;
    R.pend[t][k].delay = d > 0.0f ? (int32_t)d : 0;
    R.pend[t][k].rep = (uint8_t)(ROMI_ST_RATCH(st.flags) - 1u);   /* a ratchet: more hits, evenly within the step */
    R.pend[t][k].gap = (int32_t)(dur / (float)ROMI_ST_RATCH(st.flags));
    R.pend[t][k].on = 1;
    R.hits[t]++;
    return 1;
}

static void seq_step(void)
{
    float sw = (float)R.prj.swing * 0.01f, s = step_samples();
    float d_long = s * 2.0f * sw, d_short = s * 2.0f * (1.0f - sw);   /* swing: each pair of 16ths long, short */
    float dur = (R.gstep & 1u) ? d_short : d_long, next = (R.gstep & 1u) ? d_long : d_short;
    uint32_t done = 0;
    int t, pass;
    if (R.prj.chain && R.gstep && (R.gstep & 63u) == 0u && R.pending_pat == 0xFFu) {
        uint32_t np = R.prj.chain >= 3u ? 4u : R.prj.chain + 1u, next = (R.prj.cur_pat + 1u) % np;
        if (next == 0u && R.prj.chain == 4u && !R.prj.mode)
            R.evolve = 1;               /* (the main loop makes B..D anew, four bars before B plays) */
        R.prj.cur_pat = (uint8_t)next;
    }
    if (R.pending_pat != 0xFFu && (R.gstep & 15u) == 0u) {
        R.prj.cur_pat = R.pending_pat;
        R.pending_pat = 0xFFu;
    }
    for (t = 0; t < ROMI_TRACKS; t++) {
        int k;
        R.hit_prev[t] = R.hit[t];
        R.hit[t] = 0;
        R.pos[t] = (uint8_t)(R.gstep % (PAT->tr[t].len ? PAT->tr[t].len : 1u));
        for (k = 0; k < 2; k++) {       /* the drift: a slow random walk, pulled back to the middle */
            float d = R.drift[t][k] * 0.985f + brand(&R.rng) * 0.11f;
            R.drift[t][k] = d < -1.0f ? -1.0f : d > 1.0f ? 1.0f : d;
        }
    }
    /* the free tracks first, then those linked to a track already decided; a ring of links never fires */
    for (pass = 0; pass < ROMI_TRACKS; pass++)
        for (t = 0; t < ROMI_TRACKS; t++) {
            const romi_track_t *tr = &PAT->tr[t];
            uint32_t len = tr->len ? tr->len : 1u, pos = R.gstep % len, npos = (R.gstep + 1u) % len;
            int src = tr->dep_src && tr->dep_src - 1 != t ? tr->dep_src - 1 : -1, open = 1;
            if (done >> t & 1u)
                continue;
            if (src >= 0) {
                if (tr->dep_mode == 2)
                    open = R.hit_prev[src];
                else if (!(done >> src & 1u))
                    continue;           /* its source is not decided yet: a later pass */
                else
                    open = tr->dep_mode == 1 ? !R.hit[src] : R.hit[src];
            }
            done |= 1u << t;
            /* a step shifted early was scheduled a step ago; the very first step cannot be early, and neither can
             * a linked track's: its source is not known a step ahead */
            if (R.early[t]) {
                R.early[t] = 0;
                R.hit[t] = R.hit_early[t];
            } else if (eff_shift(tr, pos) >= 0 || R.gstep == 0u || src >= 0) {
                R.hit[t] = (uint8_t)(open && schedule(t, pos, 0.0f, dur, R.gstep));
            }
            if (src < 0 && eff_shift(tr, npos) < 0) {
                R.hit_early[t] = (uint8_t)schedule(t, npos, dur, next, R.gstep + 1u);
                R.early[t] = 1;
            }
        }
    R.clk += dur;
    R.cur_dur = dur;
    R.gstep++;
    R.gstep_ui = R.gstep;
}

static void transport(int start)
{
    if (start) {
        int t;
        for (t = 0; t < ROMI_TRACKS; t++) {
            R.early[t] = R.hit[t] = R.hit_prev[t] = 0;
            R.hits[t] = 0;
        }
        R.gstep = 0;
        R.clk = 0.0f;
        R.songpos = 0.0f;
        R.cur_dur = 0.0f;
        R.mclk = 0.0f;
        R.playing = 1;
        rt_push(0xFA);
    } else if (R.playing) {
        R.playing = 0;
        rt_push(0xFC);
    }
}

void romi_midi_transport(int start) { transport(start); }

void romi_midi_note(uint32_t channel, uint32_t note, uint32_t velocity)
{
    int t = -1, n = 0;
    if (channel < ROMI_TRACKS) {
        t = (int)channel;
        n = (int)note - 60;
    } else if (channel == 9u) {
        static const uint8_t MAP[12] = {ROMI_KICK, ROMI_PERC, ROMI_PERC, ROMI_CLICK, 255, 255,
                                        ROMI_HAT, 255, ROMI_HAT, 255, ROMI_HAT, 255};   /* 36 .. 47 */
        if (note >= 36u && note < 48u && MAP[note - 36u] != 255u)
            t = MAP[note - 36u];
        if (note == 46u)
            velocity = 127;             /* the open hat is the accent */
    }
    if (t >= 0)
        trig(t, n < -48 ? -48 : n > 48 ? 48 : n, (float)velocity * (1.0f / 127.0f), velocity > 100u, 0);
}

static void tq_push(int t, int note, int vel)   /* main loop */
{
    uint8_t w = R.tq_w;
    if ((uint8_t)((w + 1u) & 15u) == R.tq_r)
        return;
    R.tq[w][0] = (uint8_t)t;
    R.tq[w][1] = (uint8_t)(note + 64);
    R.tq[w][2] = (uint8_t)vel;
    R.tq_w = (uint8_t)((w + 1u) & 15u);
}

/* ---------------------------------------------------------------- render --- */
void romi_render(int32_t *lr, uint32_t n, uint32_t gain_q12)
{
    uint32_t i, k;
    float s16 = step_samples(), gain = (float)gain_q12 * (8388607.0f / 4096.0f);
    float duck_amt = (float)R.prj.duck * (0.9f / 127.0f), duck_c = decay_coef(pmap((float)R.prj.sc_rel, 0.03f, 3.7f));
    float sc[ROMI_TRACKS];
    float fb = (float)R.prj.dly_fb * (0.85f / 127.0f);
    float rfb = 0.70f + (float)R.prj.rev_size * (0.27f / 127.0f), damp = 0.05f + (float)R.prj.rev_damp * (0.7f / 127.0f);
    static const float DMUL[3] = {1.0f, 2.0f, 3.0f};
    uint32_t dl = (uint32_t)(s16 * DMUL[R.prj.dly_time > 2 ? 2 : R.prj.dly_time]), dr;
    while (dl > DLY_LEN - 8u)           /* a slow tempo: the next shorter note value that fits */
        dl = dl * 2u / 3u;
    if (dl < 16u)
        dl = 16u;
    dr = dl * 2u / 3u;

    if (R.want_play) {
        R.want_play = 0;
        transport(1);
    }
    if (R.want_stop) {
        R.want_stop = 0;
        transport(0);
    }
    while (R.tq_r != R.tq_w) {          /* keys played in the main loop */
        uint8_t r = R.tq_r;
        trig(R.tq[r][0], (int)R.tq[r][1] - 64, (float)R.tq[r][2] * (1.0f / 127.0f), R.tq[r][2] > 100u, 0);
        R.tq_r = (uint8_t)((r + 1u) & 15u);
    }
    if (R.playing && R.gstep && R.cur_dur > 0.0f) {
        float f = 1.0f - R.clk / R.cur_dur;
        R.songpos = (float)(R.gstep - 1u) + (f < 0.0f ? 0.0f : f > 1.0f ? 1.0f : f);
    } else if (R.playing) {
        R.songpos = 0.0f;
    }
    for (k = 0; k < ROMI_TRACKS; k++) {
        bus_update((int)k);
        sc[k] = k == R.prj.sc_src ? 0.0f : (float)PAT->tr[k].sc * (1.0f / 127.0f);
    }

    for (i = 0; i < n; i++) {
        float v[ROMI_TRACKS], l, r, sd, sr, duck, x, dly_l, dly_r, rv, rl, rr;
        if (R.playing) {
            if (R.clk <= 0.0f)
                seq_step();
            R.clk -= 1.0f;
            if (R.mclk <= 0.0f) {
                rt_push(0xF8);
                R.mclk += s16 * (1.0f / 6.0f);
            }
            R.mclk -= 1.0f;
        }
        for (k = 0; k < 2u * ROMI_TRACKS; k++) {
            uint32_t t = k >> 1, j = k & 1u;
            if (R.pend[t][j].on && --R.pend[t][j].delay < 0) {
                trig((int)t, R.pend[t][j].note, R.pend[t][j].vel, R.pend[t][j].acc,
                     PAT->tr[t].step[R.pend[t][j].si & 15u].lock);
                if (R.pend[t][j].rep) {
                    R.pend[t][j].rep--;
                    R.pend[t][j].delay = R.pend[t][j].gap;
                    R.pend[t][j].vel *= 0.82f;
                } else {
                    R.pend[t][j].on = 0;
                }
            }
        }

        /* kick: a sine falling in pitch, a click, a soft clipper */
        x = 0.0f;
        if (R.kick.amp > 1e-4f) {
            R.kick.ph += R.kick.f0 * (1.0f + R.kick.pd * R.kick.penv) * INV_SR;
            if (R.kick.ph >= 1.0f)
                R.kick.ph -= 1.0f;
            x = fsin(R.kick.ph);
            if (R.kick.click > 0) {
                x += brand(&R.rng) * R.kick.clickamt * (float)R.kick.click * (1.0f / 90.0f);
                R.kick.click--;
            }
            x = clip1(x * R.kick.amp * R.kick.drive) * R.kick.norm * R.kick.vel;
            R.kick.penv *= R.kick.pc;
            R.kick.amp *= R.kick.ac;
        }
        v[ROMI_KICK] = x;

        /* sub: a sine with a short burst of FM at its start, legato glide */
        x = 0.0f;
        if (R.sub.amp > 1e-4f) {
            R.sub.f += (R.sub.ft - R.sub.f) * R.sub.gc;
            R.sub.ph += R.sub.f * INV_SR;
            R.sub.mph += R.sub.f * R.sub.ratio * INV_SR;
            if (R.sub.ph >= 1.0f)
                R.sub.ph -= 1.0f;
            if (R.sub.mph >= 1.0f)
                R.sub.mph -= 1.0f;
            x = fsin(R.sub.ph + fsin(R.sub.mph) * R.sub.idx * R.sub.ienv) * R.sub.amp * R.sub.att * R.sub.vel;
            R.sub.att += (1.0f - R.sub.att) * 0.006f;
            R.sub.ienv *= R.sub.ic;
            R.sub.amp *= R.sub.ac;
        }
        v[ROMI_SUB] = x;

        /* hat: two inharmonic FM pairs against noise, high-passed */
        x = 0.0f;
        if (R.hat.amp > 1e-4f) {
            float f = R.hat.f * INV_SR, m;
            R.hat.ph += f;
            R.hat.mph += f * 1.4471f;
            R.hat.ph2 += f * 1.6170f;
            R.hat.mph2 += f * 2.3890f;
            if (R.hat.ph >= 1.0f) R.hat.ph -= 1.0f;
            if (R.hat.mph >= 1.0f) R.hat.mph -= 1.0f;
            if (R.hat.ph2 >= 1.0f) R.hat.ph2 -= 1.0f;
            if (R.hat.mph2 >= 1.0f) R.hat.mph2 -= 1.0f;
            m = (fsin(R.hat.ph + fsin(R.hat.mph) * 0.9f) + fsin(R.hat.ph2 + fsin(R.hat.mph2) * 0.7f)) * 0.5f;
            m = m * R.hat.metal + brand(&R.rng) * (1.0f - R.hat.metal);
            R.hat.lp += (m - R.hat.lp) * 0.45f;
            x = (m - R.hat.lp) * R.hat.amp * R.hat.vel;
            R.hat.amp *= R.hat.ac;
        }
        v[ROMI_HAT] = x;

        /* perc: one FM pair with a pitch bend: rims, woods, toms, blips */
        x = 0.0f;
        if (R.perc.amp > 1e-4f) {
            float f = R.perc.f * (1.0f + R.perc.bend * R.perc.benv) * INV_SR;
            R.perc.ph += f;
            R.perc.mph += f * R.perc.ratio;
            if (R.perc.ph >= 1.0f) R.perc.ph -= 1.0f;
            if (R.perc.mph >= 1.0f) R.perc.mph -= (float)(int)R.perc.mph;
            x = fsin(R.perc.ph + fsin(R.perc.mph) * R.perc.idx * R.perc.ienv) * R.perc.amp * R.perc.vel;
            R.perc.benv *= R.perc.bc;
            R.perc.ienv *= R.perc.ic;
            R.perc.amp *= R.perc.ac;
        }
        v[ROMI_PERC] = x;

        /* stab: a three-note chord of FM pairs through a low-pass that closes with the envelope */
        x = 0.0f;
        if (R.stab.amp > 1e-4f) {
            float ix = R.stab.idx * R.stab.ienv, c;
            for (k = 0; k < 3; k++) {
                R.stab.ph[k] += R.stab.f[k] * INV_SR;
                if (R.stab.ph[k] >= 1.0f) R.stab.ph[k] -= 1.0f;
                x += fsin(R.stab.ph[k] + fsin(R.stab.ph[k]) * ix);
            }
            c = 0.04f + 0.5f * R.stab.ienv;
            R.stab.lp += (x * (1.0f / 3.0f) - R.stab.lp) * c;
            x = R.stab.lp * R.stab.amp * R.stab.vel;
            R.stab.ienv *= R.stab.ic;
            R.stab.amp *= R.stab.ac;
        }
        v[ROMI_STAB] = x;

        /* click: a grain of noise through a resonant band-pass, somewhere in the stereo field */
        x = 0.0f;
        if (R.click.amp > 1e-4f) {
            float nz = brand(&R.rng) * R.click.amp, hp;
            R.click.lp += R.click.fc * R.click.bp;
            hp = nz - R.click.lp - R.click.q * R.click.bp;
            R.click.bp += R.click.fc * hp;
            x = R.click.bp * R.click.vel * (0.4f + 0.6f * R.click.q);
            R.click.amp *= R.click.ac;
        } else {
            R.click.lp = R.click.bp = 0.0f;
        }
        v[ROMI_CLICK] = x;

        /* SOUND 2 on each voice: attack, drive, crush (each skipped when off) */
        for (k = 0; k < ROMI_TRACKS; k++) {
            float y = v[k];
            if (R.shape[k].att < 1.0f) {
                y *= R.shape[k].att;
                R.shape[k].att += (1.0f - R.shape[k].att) * R.shape[k].attc;
                if (R.shape[k].att > 0.9999f)
                    R.shape[k].att = 1.0f;
            }
            if (R.shape[k].g > 1.001f)
                y = clip1(y * R.shape[k].g) * R.shape[k].norm;
            if (R.shape[k].levels > 0.0f) {
                if (--R.shape[k].cnt <= 0) {
                    R.shape[k].cnt = R.shape[k].hold;
                    R.shape[k].held = (float)(int32_t)(y * R.shape[k].levels) / R.shape[k].levels;
                }
                y = R.shape[k].held;
            }
            v[k] = y;
        }

        /* the mix: the sidechain's source ducks each track by that track's amount, and the effects */
        x = duck_amt * R.duck_env;
        duck = 1.0f - x;
        R.duck_env *= duck_c;
        l = r = sd = sr = 0.0f;
        for (k = 0; k < ROMI_TRACKS; k++) {
            float y = v[k] * (1.0f - x * sc[k]);
            if (k == ROMI_CLICK) {
                l += y * R.bus[k].gl * 2.0f * (1.0f - R.click.pan);
                r += y * R.bus[k].gr * 2.0f * R.click.pan;
            } else {
                l += y * R.bus[k].gl;
                r += y * R.bus[k].gr;
            }
            sd += y * R.bus[k].sd;
            sr += y * R.bus[k].sr;
        }

        /* delay: one line, two taps (left the full time, right two thirds of it), filtered feedback */
        dly_l = (float)dly_buf[(R.dly_w - dl) & (DLY_LEN - 1u)] * (1.0f / 16384.0f);
        dly_r = (float)dly_buf[(R.dly_w - dr) & (DLY_LEN - 1u)] * (1.0f / 16384.0f);
        R.dly_lp += (dly_l - R.dly_lp) * 0.35f;
        x = clip1(sd + R.dly_lp * fb) * 16384.0f;
        dly_buf[R.dly_w] = (int16_t)x;
        R.dly_w = (R.dly_w + 1u) & (DLY_LEN - 1u);
        sr += (dly_l + dly_r) * 0.15f;

        /* reverb: four damped combs, then two all-passes a side */
        rv = 0.0f;
        sr = sr * 0.25f + 1e-20f;
        for (k = 0; k < 4; k++) {
            float y = (float)comb_buf[k][R.comb_i[k]] * RV_IN;
            R.comb_f[k] = y + (R.comb_f[k] - y) * damp;
            comb_buf[k][R.comb_i[k]] = rv_out(sr + R.comb_f[k] * rfb);
            if (++R.comb_i[k] >= COMB_LEN[k])
                R.comb_i[k] = 0;
            rv += y;
        }
        rl = rr = rv;
        for (k = 0; k < 4; k++) {
            float *io = k < 2 ? &rl : &rr, b = (float)ap_buf[k][R.ap_i[k]] * RV_IN;
            ap_buf[k][R.ap_i[k]] = rv_out(*io + b * 0.5f);
            *io = b - *io;
            if (++R.ap_i[k] >= AP_LEN[k])
                R.ap_i[k] = 0;
        }
        l += dly_l + rl * duck;
        r += dly_r + rr * duck;

        lr[2u * i] = (int32_t)(clip1(l * 0.62f) * gain);
        lr[2u * i + 1u] = (int32_t)(clip1(r * 0.62f) * gain);
    }
}

/* ------------------------------------------------------------- generator --- */
/* What makes a pattern rominimal here: the kick on every beat and nothing else certain. Hats lean on the
 * off-beat, the sub rolls between the kicks, percussion and clicks run on odd lengths with low probabilities,
 * so the bar never repeats exactly. */
static uint32_t urand(uint32_t n) { return xs32(&R.ui_rng) % n; }
static int scale_note(int degree)
{
    const uint8_t *sc = SCALES[R.prj.scale & 3u];
    int oct = 0;
    while (degree < 0) {
        degree += 7;
        oct--;
    }
    while (degree >= 7) {
        degree -= 7;
        oct++;
    }
    return sc[degree] + 12 * oct;
}
static void set_step(romi_track_t *tr, uint32_t i, int acc, int prob, int note);

/* the degree's note, folded into the stab's register: a fifth below the root to an octave above it */
static int stab_note(int degree)
{
    int n = scale_note(degree);
    while (n > 12)
        n -= 12;
    while (n < -7)
        n += 12;
    return n;
}
/* the note dir (+1 or -1) scale steps away from note: the scale's next tone up or down */
static int scale_step(int note, int dir)
{
    int d, best = note + dir * 2;
    for (d = -14; d <= 21; d++) {
        int n = scale_note(d);
        if (dir > 0 && n > note && n < best + (best <= note))
            best = n;
        if (dir < 0 && n < note && n > best - (best >= note))
            best = n;
    }
    return best;
}

/* STAB: a short phrase in the scale. Either chord changes (a progression a minor key knows: i - VI - VII, i - iv -
 * v, ...) or a motif (a line that moves by steps and small leaps, starts on the root or the fifth and comes home at
 * the end). The rhythm is one of a few stab figures off the kick; the first hit carries the accent. */
static void gen_stab(romi_track_t *tr)
{
    static const uint8_t RHYTHM[8][6] = {     /* positions, 255: end */
        {3, 6, 11, 14, 255},       {2, 7, 10, 15, 255},     {3, 10, 255},            {6, 14, 255},
        {3, 6, 9, 14, 255},        {2, 5, 8, 11, 14, 255},  {1, 6, 11, 255},         {3, 7, 11, 13, 255},
    };
    static const int8_t PROG[8][4] = {        /* scale degrees from 0: i, iii, iv, v, VI, VII */
        {0, 5, 6, 0}, {0, 6, 5, 6}, {0, 3, 4, 0}, {0, 2, 3, 6},
        {0, 0, 5, 6}, {0, 3, 0, 4}, {0, 5, 3, 4}, {0, 6, 3, 0},
    };
    uint32_t i, n = 0, pos[6];
    const uint8_t *rh;
    static const uint8_t BY_DENSITY[3][4] = {{2, 3, 6, 2}, {0, 1, 6, 7}, {4, 5, 7, 0}};   /* 2-3, 3-4, 4-5 hits */
    tr->len = urand(4) ? 16 : 12;
    rh = RHYTHM[BY_DENSITY[R.density > 2 ? 2 : R.density][urand(4)]];
    for (i = 0; i < 6 && rh[i] != 255u; i++)
        if (rh[i] < tr->len)
            pos[n++] = rh[i];
    if (n < 2) {                              /* the figure did not fit twelve steps: sixteen it is */
        tr->len = 16;
        for (n = 0, i = 0; i < 6 && rh[i] != 255u; i++)
            pos[n++] = rh[i];
    }
    if (urand(2)) {                           /* chord changes: the progression spread over the hits */
        const int8_t *pg = PROG[urand(8)];
        for (i = 0; i < n; i++) {
            int k = n == 2 ? (int)i * (pg[1] != pg[0] ? 1 : 2) : (int)(i * 4 / n);   /* two hits: two chords */
            set_step(tr, pos[i], i == 0, i == 0 ? 0 : (int)urand(2), stab_note(pg[k]));
        }
    } else {                                  /* a motif: steps and small leaps, home at the end */
        static const int8_t MOVE[8] = {-2, -1, -1, 1, 1, 2, 3, -3};
        int d = urand(3) ? 0 : 4, d0 = d, last;
        for (i = 0; i < n; i++) {
            if (i + 1 == n && n > 1) {        /* the last hit resolves: to the root, or the fifth if it came from there */
                last = d;
                d = (last == 3 || last == 5) && urand(2) ? 4 : 0;
                if (last == 0 || (n == 2 && d == d0))
                    d = d0 == 4 ? 0 : urand(2) ? 4 : -3;   /* (not the same tone again: the fifth, or VI below) */
            }
            set_step(tr, pos[i], i == 0, i == 0 || i + 1 == n ? 0 : (int)urand(2), stab_note(d));
            d += MOVE[urand(8)];
            if (d < -3) d = -3 + (int)urand(2);
            if (d > 7) d = 7 - (int)urand(2);
        }
    }
}

static void step_plain(romi_step_t *st)   /* no shift, no locks */
{
    st->shift = 0;
    int k;
    for (k = 0; k < 8; k++)
        st->lock[k] = 0;
}
static void set_step(romi_track_t *tr, uint32_t i, int acc, int prob, int note)
{
    tr->step[i % ROMI_STEPS].flags = (uint8_t)(ROMI_ST_ON | (acc ? ROMI_ST_ACC : 0u) | ((uint32_t)prob << 4));
    tr->step[i % ROMI_STEPS].note = (int8_t)note;
}
static void euclid(romi_track_t *tr, uint32_t hits, uint32_t rot)
{
    uint32_t i, acc = 0;
    for (i = 0; i < tr->len; i++) {
        acc += hits;
        if (acc >= tr->len) {
            acc -= tr->len;
            set_step(tr, (i + rot) % tr->len, 0, 0, 0);
        }
    }
}

/* ---- the generator: every track new, but in one groove ----
 * A whole NEW first picks the groove's density (sparse, medium, busy; faster tempos lean sparse), then makes the
 * tracks in an order where each can lean on the ones before: the kick is the grid and is tuned to the key; the
 * stab's phrase is the harmony; the sub rolls between the kicks on chord tones; the hats sit on the off-beat; the
 * percussion runs on its own length, rotated off the kick, on tones of the key; the clicks fill in, rarely. Each
 * track's colour (a few sound parameters, never level, pan or sends, never the kick's or the sub's weight) moves
 * within ranges that suit it. UNDO takes all of it back. */

/* a value near v, at most spread away, within 0..127 */
static uint8_t near(int v, int spread)
{
    v += (int)urand((uint32_t)(2 * spread + 1)) - spread;
    return (uint8_t)(v < 0 ? 0 : v > 127 ? 127 : v);
}

/* the kick's note that puts its fundamental on the key's root (a pitch class), a fifth up or down at most */
static int kick_in_key(const romi_track_t *tr, int shift)
{
    float f0 = pmap((float)tr->p[0], 36.0f, 1.0f) * fexp2(((float)tr->q[0] - 24.0f) * (1.0f / 12.0f));
    float fr = note_hz((float)(R.prj.root + shift)), best = 9.0f;
    int n, pick = 0;
    for (n = -6; n <= 5; n++) {
        float r = f0 * fexp2((float)n * (1.0f / 12.0f)) / fr, d;
        while (r >= 2.0f) r *= 0.5f;
        while (r < 1.0f) r *= 2.0f;
        d = r - 1.0f < 2.0f - r ? r - 1.0f : (2.0f - r) * 0.5f;   /* (distance in the octave: ratios, near enough) */
        if (d < best) {
            best = d;
            pick = n;
        }
    }
    return pick;
}

/* n of the steps from cand (weights w), none twice; at least one in every half when n > 1 */
static uint32_t pick_steps(uint32_t *out, uint32_t n, const uint8_t *cand, const uint8_t *w, uint32_t nc, uint32_t len)
{
    uint32_t got = 0, tries = 0, used = 0, i;
    while (got < n && tries++ < 200u) {
        uint32_t total = 0, r, c = 0;
        for (i = 0; i < nc; i++)
            if (cand[i] < len && !(used >> cand[i] & 1u))
                total += w[i];
        if (!total)
            break;
        r = urand(total);
        for (i = 0; i < nc; i++)
            if (cand[i] < len && !(used >> cand[i] & 1u)) {
                if (r < w[i]) {
                    c = cand[i];
                    break;
                }
                r -= w[i];
            }
        used |= 1u << c;
        out[got++] = c;
    }
    return got;
}

static void gen_track(int t)
{
    romi_track_t *tr = &EDT->tr[t];
    uint32_t i, d = R.density > 2 ? 2 : R.density;
    for (i = 0; i < ROMI_STEPS; i++) {
        tr->step[i].flags = 0;
        tr->step[i].note = 0;
        step_plain(&tr->step[i]);
    }
    tr->len = 16;
    switch (t) {
    case ROMI_KICK: {
        static const uint8_t GHOST[3] = {15, 30, 45};   /* % of grooves with a ghost kick */
        int key = kick_in_key(tr, 0);
        for (i = 0; i < 16; i += 4)
            set_step(tr, i, 1, 0, key);
        if (urand(100) < GHOST[d])
            set_step(tr, urand(3) == 0 ? 7 : urand(2) ? 15 : 10, 0, 2, key);
        break;
    }
    case ROMI_SUB: {
        /* between the kicks: never on a quarter (a 12- or 16-step loop keeps it so), the "and" first */
        static const uint8_t CAND[12] = {2, 6, 10, 14, 3, 7, 11, 15, 1, 5, 9, 13};
        static const uint8_t W[12] = {6, 6, 6, 6, 3, 3, 3, 3, 1, 1, 1, 1};
        static const uint8_t COUNT[3][2] = {{3, 4}, {4, 6}, {6, 8}};
        static const int8_t DEG[8] = {0, 0, 0, 0, -1, 2, 4, -3};          /* free: mostly the root */
        static const int8_t CHORD_TONE[8] = {0, 0, 0, 0, 7, 12, 3, -5};   /* following: the chord's own tones */
        uint32_t pos[16], n, k;
        tr->len = urand(4) ? 16 : 12;
        n = pick_steps(pos, COUNT[d][0] + urand(COUNT[d][1] - COUNT[d][0] + 1u), CAND, W, 12, tr->len);
        for (k = 1; k < n; k++) {                       /* in time order: the first hit is the root */
            uint32_t j = k, v = pos[k];
            while (j && pos[j - 1] > v) {
                pos[j] = pos[j - 1];
                j--;
            }
            pos[j] = v;
        }
        for (k = 0; k < n; k++) {
            int note = k == 0 ? 0 : tr->follow ? CHORD_TONE[urand(8)] : scale_note(DEG[urand(8)]);
            set_step(tr, pos[k], (pos[k] & 3u) == 2u && urand(3) == 0, urand(6) == 0 ? 1 : 0, note);
        }
        break;
    }
    case ROMI_HAT: {
        static const uint8_t FILL[3] = {22, 38, 55};    /* % of the other steps with a quiet hat */
        for (i = 2; i < 16; i += 4)
            set_step(tr, i, urand(3) != 0, 0, 0);       /* the off-beat, mostly open */
        for (i = 0; i < 16; i++)
            if (!(tr->step[i].flags & ROMI_ST_ON) && urand(100) < FILL[d]) {
                set_step(tr, i, 0, 1 + (int)urand(3), 0);
                if (urand(8) == 0)
                    tr->step[i].flags |= 1u;            /* now and then a double */
            }
        tr->p[0] = near(42, 14);                        /* decay */
        tr->p[1] = near(70, 18);                        /* tone */
        tr->p[2] = near(80, 25);                        /* metal */
        break;
    }
    case ROMI_PERC: {
        static const uint8_t LEN[6] = {16, 12, 10, 7, 14, 6};
        static const uint8_t HITS[3] = {2, 3, 4};
        static const int8_t TONE[6] = {0, 0, 2, 4, 6, 7};   /* degrees: root, third, fifth, seventh, octave */
        uint32_t rot, best = 0, fewest = 99, h;
        tr->len = LEN[urand(6)];
        h = HITS[d] + urand(2);
        for (rot = 0; rot < tr->len; rot++) {           /* the rotation that meets the kick least, over 4 bars */
            uint32_t acc = 0, hit = 0, g;
            for (i = 0; i < tr->len; i++) {
                acc += h;
                if (acc >= tr->len) {
                    acc -= tr->len;
                    for (g = (i + rot) % tr->len; g < 64u; g += tr->len)
                        hit += (g & 3u) == 0u;
                }
            }
            hit = hit * 8u + urand(8);                  /* (ties broken at random) */
            if (hit < fewest) {
                fewest = hit;
                best = rot;
            }
        }
        euclid(tr, h, best);
        for (i = 0; i < tr->len; i++)
            if (tr->step[i].flags & ROMI_ST_ON) {
                static const int8_t CHORD_TONE[5] = {0, 0, 3, 7, 10};   /* following: the chord's own tones */
                int note = tr->follow ? CHORD_TONE[urand(5)] : scale_note(TONE[urand(6)]);
                set_step(tr, i, urand(4) == 0, (int)urand(3), note);
            }
        tr->p[0] = near(48, 18);                        /* decay */
        tr->p[1] = near(52, 24);                        /* fm */
        tr->p[2] = (uint8_t)(urand(8) * 16u + 4u);      /* ratio: rim, wood, tom, blip */
        tr->p[3] = near(30, 28);                        /* bend */
        break;
    }
    case ROMI_STAB:
        gen_stab(tr);
        tr->p[0] = near(66, 16);                        /* decay */
        tr->p[1] = near(60, 18);                        /* bright */
        tr->p[2] = (uint8_t)(urand(5) * 26u + 4u);      /* chord: min, min7, min9, sus, fifth */
        break;
    default: {
        static const uint8_t LEN[5] = {16, 9, 11, 13, 5};
        static const uint8_t EXTRA[3] = {0, 1, 3};
        tr->len = LEN[urand(5)];
        euclid(tr, 2 + urand(tr->len > 8 ? 2u + EXTRA[d] : 2u), urand(tr->len));
        for (i = 0; i < tr->len; i++)
            if (tr->step[i].flags & ROMI_ST_ON) {
                set_step(tr, i, 0, 1 + (int)urand(3), (int)urand(13) - 6);
                if (urand(5) == 0)
                    tr->step[i].flags |= (uint8_t)(1u + urand(2));   /* a stutter of two or three */
            }
        tr->p[1] = near(78, 22);                        /* freq */
        tr->p[2] = near(84, 22);                        /* reso */
        break;
    }
    }
    tr->eu_rot = 0;
    tr->eu_hits = 0;
    for (i = 0; i < ROMI_STEPS; i++)
        tr->eu_hits += (tr->step[i].flags & ROMI_ST_ON) != 0;
}

/* a whole new groove: its density first (faster tempos lean sparse), then the tracks in the order they lean on */
static void gen_all(void)
{
    static const uint8_t ORDER[ROMI_TRACKS] = {ROMI_KICK, ROMI_STAB, ROMI_SUB, ROMI_HAT, ROMI_PERC, ROMI_CLICK};
    uint32_t r = urand(10), k;
    R.density = (uint8_t)(r < 3 ? 0 : r < 8 ? 1 : 2);
    if (R.prj.bpm >= 130 && R.density)
        R.density--;
    else if (R.prj.bpm <= 116 && R.density < 2 && urand(2))
        R.density++;
    for (k = 0; k < ROMI_TRACKS; k++)
        gen_track(ORDER[k]);
}

/* ---- the variations: B, C and D are made from A, always ----
 * A is the groove; B, C and D are ways of playing it, never other songs. Each is A with one decided change, from
 * dice of its own (var_seed: the same A and seed, the same variation), and is made again whenever A changes:
 *   B  the beat varied: a few hats turned over and one doubled, percussion and clicks turned on their own loops,
 *      a sub hit moved beside itself (never onto the kick), the stab's chords in another order, now and then a
 *      kick beat left out, a ghost kick that comes or goes, a nudge to the colour of hats, percussion and clicks.
 *      The same harmony.
 *   C  rolls into the next bar: hats rolling up to a fourfold ratchet in the last four steps, percussion and
 *      clicks rolling with them, the kick pausing for those four steps (or a kick pickup), a sub pickup.
 *   D  A in a related key: the subdominant, the dominant, the seventh or the third (by its dice); stab, percussion
 *      and a free sub move with it, a following sub follows the stab, the kick is tuned to the new root. */
static uint32_t vr_state;
static uint32_t vrand(uint32_t n) { return xs32(&vr_state) % n; }
static int fold(int n, int lo, int hi)
{
    while (n > hi)
        n -= 12;
    while (n < lo)
        n += 12;
    return n;
}
static uint8_t nudge(uint8_t v, int spread)
{
    int x = (int)v + (int)vrand((uint32_t)(2 * spread + 1)) - spread;
    return (uint8_t)(x < 0 ? 0 : x > 127 ? 127 : x);
}
static void turn_loop(romi_track_t *tr, uint32_t by)   /* the track's loop turned later by `by` steps */
{
    romi_step_t tmp[ROMI_STEPS];
    uint32_t i, n = tr->len ? tr->len : 1u;
    for (i = 0; i < n; i++)
        tmp[(i + by) % n] = tr->step[i];
    for (i = 0; i < n; i++)
        tr->step[i] = tmp[i];
}

/* D's interval in semitones: subdominant, dominant, seventh (below) or third */
static int key_step(void)
{
    static const int8_t STEP[4] = {5, 7, -2, 3};
    uint32_t x = (uint32_t)R.prj.var_seed[2] * 2654435761u | 1u;
    xs32(&x);
    return STEP[x % 4u];
}

static void vary(romi_pattern_t *d)
{
    romi_track_t *h = &d->tr[ROMI_HAT], *sb = &d->tr[ROMI_SUB], *st = &d->tr[ROMI_STAB], *kk = &d->tr[ROMI_KICK];
    uint32_t i, j, n = 2 + vrand(2), on[ROMI_STEPS], non = 0;
    for (j = 0; j < n; j++) {                       /* hats: a few between the off-beats turn over */
        i = vrand(16);
        if ((i & 3u) == 2u)
            continue;
        if (h->step[i].flags & ROMI_ST_ON) {
            h->step[i].flags = 0;
        } else {
            h->step[i].flags = (uint8_t)(ROMI_ST_ON | (1u + vrand(3)) << 4);
            h->step[i].note = 0;
        }
    }
    i = 2u + 4u * vrand(4);                         /* and one off-beat doubles */
    h->step[i].flags = (uint8_t)((h->step[i].flags & ~3u) | 1u);
    turn_loop(&d->tr[ROMI_PERC], 1 + vrand(2));     /* percussion and clicks: turned on their own loops */
    turn_loop(&d->tr[ROMI_CLICK], 1 + vrand(3));
    for (i = 0; i < sb->len; i++)                   /* the sub: one hit beside itself, never on a quarter */
        if (sb->step[i].flags & ROMI_ST_ON)
            on[non++] = i;
    if (non) {
        uint32_t from = on[vrand(non)], to = vrand(2) ? from + 1u : from + sb->len - 1u;
        to %= sb->len;
        if ((to & 3u) && !(sb->step[to].flags & ROMI_ST_ON)) {
            romi_step_t tmp = sb->step[to];
            sb->step[to] = sb->step[from];
            sb->step[from] = tmp;
        }
    }
    for (non = 0, i = 0; i < st->len; i++)          /* the stab: its chords in another order */
        if (st->step[i].flags & ROMI_ST_ON)
            on[non++] = i;
    if (non >= 2) {
        int8_t first = st->step[on[0]].note;
        for (i = 0; i + 1 < non; i++)
            st->step[on[i]].note = st->step[on[i + 1]].note;
        st->step[on[non - 1]].note = first;
    }
    if (kk->len == 16 && vrand(3) == 0)             /* now and then the kick sits out a beat */
        kk->step[vrand(2) ? 8 : 12].flags = 0;
    if (kk->step[15].flags & ROMI_ST_ON) {          /* a ghost kick comes or goes */
        kk->step[15].flags = 0;
    } else if (kk->len == 16) {
        kk->step[15].flags = (uint8_t)(ROMI_ST_ON | 1u << 4);
        kk->step[15].note = kk->step[0].note;
    }
    h->p[0] = nudge(h->p[0], 8);                    /* a nudge to the colour */
    d->tr[ROMI_PERC].p[0] = nudge(d->tr[ROMI_PERC].p[0], 8);
    d->tr[ROMI_CLICK].p[1] = nudge(d->tr[ROMI_CLICK].p[1], 10);
}

static void rolls(romi_pattern_t *d)
{
    static const uint8_t RATCH[4] = {1, 1, 2, 3};   /* x2 x2 x3 x4 */
    romi_track_t *h = &d->tr[ROMI_HAT], *pc = &d->tr[ROMI_PERC], *cl = &d->tr[ROMI_CLICK];
    romi_track_t *kk = &d->tr[ROMI_KICK], *sb = &d->tr[ROMI_SUB];
    uint32_t i, last;
    for (i = 12; i < 16 && i < h->len; i++) {       /* the hats roll up to the bar */
        h->step[i].flags = (uint8_t)(ROMI_ST_ON | RATCH[i - 12] | (i == 15 ? ROMI_ST_ACC : 0u));
        h->step[i].note = (int8_t)(i - 12);
    }
    if (pc->len == 16) {                            /* the percussion with them, rising */
        for (i = 13; i < 16; i++) {
            pc->step[i].flags = (uint8_t)(ROMI_ST_ON | (i == 15 ? 2u | ROMI_ST_ACC : 1u));
            pc->step[i].note = (int8_t)scale_note((int)(i - 13) * 2);
        }
    } else {
        for (last = pc->len; last-- > 0;)
            if (pc->step[last].flags & ROMI_ST_ON) {
                pc->step[last].flags = (uint8_t)((pc->step[last].flags & ~0x33u) | 2u);
                break;
            }
    }
    if (cl->len == 16) {                            /* the clicks too */
        for (i = 14; i < 16; i++)
            cl->step[i].flags = (uint8_t)(ROMI_ST_ON | 2u);
    } else {
        for (i = 0; i < cl->len; i++)
            if (cl->step[i].flags & ROMI_ST_ON)
                cl->step[i].flags = (uint8_t)(cl->step[i].flags & ~0x30u);   /* every one sure */
    }
    if (kk->len == 16 && vrand(2)) {                /* the kick pauses for the bar's last four steps */
        for (i = 12; i < 16; i++)
            kk->step[i].flags = 0;
    } else if (kk->len == 16 && !(kk->step[15].flags & ROMI_ST_ON)) {   /* or plays a pickup */
        kk->step[15].flags = ROMI_ST_ON;
        kk->step[15].note = kk->step[0].note;
    }
    last = sb->len - 1u;                            /* and a sub pickup, an octave up */
    if ((last & 3u) && !(sb->step[last].flags & ROMI_ST_ON)) {
        sb->step[last].flags = ROMI_ST_ON;
        sb->step[last].note = 12;
    }
}

static void to_key(romi_pattern_t *d)
{
    int iv = key_step(), kn;
    uint32_t i;
    romi_track_t *kk = &d->tr[ROMI_KICK], *sb = &d->tr[ROMI_SUB];
    for (i = 0; i < ROMI_STEPS; i++) {
        d->tr[ROMI_STAB].step[i].note = (int8_t)fold(d->tr[ROMI_STAB].step[i].note + iv, -7, 12);
        d->tr[ROMI_PERC].step[i].note = (int8_t)fold(d->tr[ROMI_PERC].step[i].note + iv, -5, 14);
        if (!sb->follow)
            sb->step[i].note = (int8_t)fold(sb->step[i].note + iv, -7, 12);
    }
    kn = kick_in_key(kk, iv);
    for (i = 0; i < ROMI_STEPS; i++)
        if (kk->step[i].flags & ROMI_ST_ON)
            kk->step[i].note = (int8_t)kn;
}

static void derive(int k)                           /* pattern k (1..3: B..D) made from A */
{
    romi_pattern_t *d = &R.prj.pat[k];
    *d = *BASE;
    vr_state = ((uint32_t)R.prj.var_seed[k - 1] << 4 | (uint32_t)k) * 2654435761u | 1u;
    xs32(&vr_state);
    if (k == 1)
        vary(d);
    else if (k == 2)
        rolls(d);
    else
        to_key(d);
}
static void derive_all(void)
{
    int k;
    for (k = 1; k < ROMI_PATTERNS; k++)
        derive(k);
    R.base_changed = 0;
}
static void new_seeds(void)
{
    int k;
    for (k = 0; k < 3; k++)
        R.prj.var_seed[k] = (uint16_t)(xs32(&R.ui_rng) >> 8);
}

/* the EUCLID page: hits spread as evenly as the loop allows, rotated; the notes stay */
static void apply_euclid(int t)
{
    romi_track_t *tr = &EDT->tr[t];
    uint32_t i, n = 0, len = tr->len ? tr->len : 1u;
    if (tr->eu_hits > len)
        tr->eu_hits = (uint8_t)len;
    if (tr->eu_rot >= len)
        tr->eu_rot = (uint8_t)(len - 1u);
    for (i = 0; i < ROMI_STEPS; i++)
        tr->step[i].flags = 0;
    for (i = 0; i < len; i++)
        if (i * tr->eu_hits % len < tr->eu_hits) {
            uint32_t acc = tr->eu_acc && n % tr->eu_acc == 0u ? ROMI_ST_ACC : 0u;
            tr->step[(i + tr->eu_rot) % len].flags = (uint8_t)(ROMI_ST_ON | acc | (3u - (tr->eu_prob & 3u)) << 4);
            n++;
        }
}

static void mutate_track(int t)
{
    romi_track_t *tr = &EDT->tr[t];
    uint32_t i = urand(tr->len ? tr->len : 1u), kind = urand(4);
    romi_step_t *st = &tr->step[i];
    if (t == ROMI_KICK && (i & 3u) == 0u)
        kind = 1;                       /* the four on the floor stays; its probability does not change either */
    if (kind == 0) {
        if (st->flags & ROMI_ST_ON)
            st->flags = (uint8_t)(st->flags & ~ROMI_ST_ON);
        else
            set_step(tr, i, 0, 1 + (int)urand(3), st->note);
    } else if (kind == 1 && t != ROMI_KICK) {
        if (st->flags & ROMI_ST_ON)
            st->flags = (uint8_t)((st->flags & ~0x30u) | (urand(4) << 4));
    } else if (kind == 2) {
        if ((st->flags & ROMI_ST_ON) && t != ROMI_KICK && t != ROMI_HAT && t != ROMI_CLICK) {
            int nn = scale_step(st->note, urand(2) ? 1 : -1);   /* one scale step, so the line stays a line */
            if (nn >= -12 && nn <= 19)
                st->note = (int8_t)nn;
        }
    } else if (st->flags & ROMI_ST_ON) {
        st->flags ^= ROMI_ST_ACC;
    }
}

static void rotate_track(int t, int dir)
{
    romi_track_t *tr = &EDT->tr[t];
    uint32_t i, n = tr->len;
    romi_step_t s;
    if (n < 2u)
        return;
    if (dir > 0) {
        s = tr->step[n - 1u];
        for (i = n - 1u; i > 0; i--)
            tr->step[i] = tr->step[i - 1u];
        tr->step[0] = s;
    } else {
        s = tr->step[0];
        for (i = 0; i + 1u < n; i++)
            tr->step[i] = tr->step[i + 1u];
        tr->step[n - 1u] = s;
    }
}

static void pattern_defaults(romi_pattern_t *p)
{
    static const uint8_t DEF[ROMI_TRACKS][8] = {
        /* p0   p1   p2   p3  level pan  dly  rev */
        {  44,  62,  70,  30, 120,  64,   0,   0},   /* kick: tune decay punch drive */
        {  70,  40,   0,  45, 104,  64,   0,   0},   /* sub: decay fm ratio glide */
        {  42,  70,  80,  64,  90,  74,  18,  20},   /* hat: decay tone metal open */
        {  48,  52,  40,  30,  88,  46,  50,  34},   /* perc: decay fm ratio bend */
        {  66,  60,  30,  40,  78,  64,  70,  60},   /* stab: decay bright chord detune */
        {  40,  78,  84,  90,  86,  64,  40,  30},   /* click: decay freq reso scatter */
    };
    int t, i;
    for (t = 0; t < ROMI_TRACKS; t++) {
        romi_track_t *tr = &p->tr[t];
        for (i = 0; i < 4; i++)
            tr->p[i] = DEF[t][i];
        tr->level = DEF[t][4];
        tr->pan = DEF[t][5];
        tr->dly = DEF[t][6];
        tr->rev = DEF[t][7];
        tr->mute = 0;
        tr->eu_hits = tr->eu_rot = tr->eu_acc = tr->dep_src = tr->dep_mode = 0;
        tr->tshift = 0;
        tr->follow = t == ROMI_SUB ? ROMI_STAB + 1 : 0;   /* the bass follows the stab's chords */
        {   /* SOUND 2: as the sound was before it had the page (kick click 0.25, pitch 22 ms; sub FM 60 ms; perc
             * bend 12 ms; stab attack 2.3 ms); no pitch, drive or crush */
            static const uint8_t Q[ROMI_TRACKS][4] = {{24, 53, 79, 0}, {24, 82, 0, 0}, {24, 0, 0, 0},
                                                      {24, 64, 0, 0}, {24, 38, 0, 0}, {24, 0, 0, 0}};
            for (i = 0; i < 4; i++)
                tr->q[i] = Q[t][i];
        }
        for (i = 0; i < ROMI_LFOS; i++) {
            tr->lfo[i].rate = (uint8_t)(i ? 6 : 4);   /* 1 bar, 4 bars */
            tr->lfo[i].depth = 0;                     /* off until turned */
            tr->lfo[i].target = (uint8_t)(i ? 5 : 1); /* the second parameter (mostly a decay or brightness), pan */
            tr->lfo[i].shape = 0;
        }
        tr->eu_prob = 3;
        tr->sc = t == ROMI_KICK ? 0 : 127;
        tr->len = 16;
        for (i = 0; i < ROMI_STEPS; i++) {
            tr->step[i].flags = 0;
            tr->step[i].note = 0;
            step_plain(&tr->step[i]);
        }
    }
}

/* --------------------------------------------------------------- project --- */
static void prj_sanitize(romi_project_t *p)
{
    int a, t, i;
#define LIM(v, lo, hi) do { if ((v) < (lo)) (v) = (lo); if ((v) > (hi)) (v) = (hi); } while (0)
    LIM(p->bpm, 90, 150);
    LIM(p->swing, 50, 75);
    LIM(p->drift, 0, 127);
    LIM(p->duck, 0, 127);
    LIM(p->root, 24, 47);
    LIM(p->scale, 0, 3);
    LIM(p->dly_time, 0, 2);
    LIM(p->dly_fb, 0, 127);
    LIM(p->rev_size, 0, 127);
    LIM(p->rev_damp, 0, 127);
    LIM(p->clock_out, 0, 1);
    LIM(p->cur_pat, 0, ROMI_PATTERNS - 1);
    LIM(p->chain, 0, 4);
    LIM(p->mode, 0, 1);
    LIM(p->sc_src, 0, ROMI_TRACKS - 1);
    LIM(p->sc_rel, 0, 127);
    for (a = 0; a < ROMI_PATTERNS; a++)
        for (t = 0; t < ROMI_TRACKS; t++) {
            romi_track_t *tr = &p->pat[a].tr[t];
            LIM(tr->len, 1, ROMI_STEPS);
            LIM(tr->mute, 0, 1);
            LIM(tr->level, 0, 127);
            LIM(tr->pan, 0, 127);
            LIM(tr->dly, 0, 127);
            LIM(tr->rev, 0, 127);
            LIM(tr->sc, 0, 127);
            LIM(tr->dep_src, 0, ROMI_TRACKS);
            LIM(tr->dep_mode, 0, 2);
            LIM(tr->tshift, -8, 8);
            LIM(tr->follow, 0, ROMI_TRACKS);
            for (i = 0; i < ROMI_LFOS; i++) {
                LIM(tr->lfo[i].rate, 0, 8);
                LIM(tr->lfo[i].depth, -64, 63);
                LIM(tr->lfo[i].target, 0, 11);
                LIM(tr->lfo[i].shape, 0, 4);
            }
            LIM(tr->eu_hits, 0, tr->len);
            LIM(tr->eu_rot, 0, tr->len - 1);
            LIM(tr->eu_prob, 0, 3);
            LIM(tr->eu_acc, 0, 4);
            for (i = 0; i < 4; i++)
                LIM(tr->p[i], 0, 127);
            LIM(tr->q[0], 0, 48);
            for (i = 1; i < 4; i++)
                LIM(tr->q[i], 0, 127);
            for (i = 0; i < ROMI_STEPS; i++) {
                int k;
                LIM(tr->step[i].note, ROMI_NOTE_MIN, ROMI_NOTE_MAX);
                LIM(tr->step[i].shift, -ROMI_SHIFT_MAX, ROMI_SHIFT_MAX);
                for (k = 0; k < 8; k++)
                    LIM(tr->step[i].lock[k], 0, 128);
                if (tr->step[i].lock[4] > 49)
                    tr->step[i].lock[4] = 49;
            }
        }
#undef LIM
}

static int lock_count_track(const romi_track_t *tr)
{
    int i, k, n = 0;
    for (i = 0; i < ROMI_STEPS; i++)
        for (k = 0; k < 8; k++)
            n += tr->step[i].lock[k] != 0;
    return n;
}
static int lock_count(const romi_pattern_t *p)
{
    int t, n = 0;
    for (t = 0; t < ROMI_TRACKS; t++)
        n += lock_count_track(&p->tr[t]);
    return n;
}

/* ---- the store: packed objects, byte by byte (no struct dumped: the layout is the format) ----
 *   header   'R' 'M' kind ('S' settings, 'P' a pattern) version index
 *   settings bpm swing drift duck root scale dly_time dly_fb rev_size rev_damp clock_out cur_pat chain sc_src sc_rel
 *   pattern  per track: len mute p0..p3 level pan dly rev eu_hits eu_rot eu_prob eu_acc sc dep_src tshift dep_mode
 *            follow, its two LFOs (rate depth target shape each), q0..q3 (SOUND 2), then its 16 steps, two
 *            bytes each:
 *              b0 = flags (on, accent, chance, ratchet: bits 7..4, 1..0) | shift's high bits << 2
 *              b1 = note + 32 (6 bits) | shift's low bits << 6          (shift stored + 8: 1..15)
 *            then the locks: their count, and each as track << 4 | step, parameter, value
 *   trailer  Adler-32 of all before it, little-endian */
static uint32_t adler(const uint8_t *b, uint32_t n)
{
    uint32_t i, a = 1, c = 0;
    for (i = 0; i < n; i++) {
        a = (a + b[i]) % 65521u;
        c = (c + a) % 65521u;
    }
    return c << 16 | a;
}

static uint32_t pack(int obj, uint8_t *d)   /* d holds ROMI_OBJ_MAX bytes; returns the length */
{
    uint32_t n = 0, sum;
    int t, i, k;
    d[n++] = 'R';
    d[n++] = 'M';
    d[n++] = obj ? 'P' : 'S';
    d[n++] = (uint8_t)ROMI_VERSION;
    d[n++] = (uint8_t)(obj ? obj - 1 : 0);
    if (!obj) {
        const romi_project_t *p = &R.prj;
        d[n++] = p->bpm; d[n++] = p->swing; d[n++] = p->drift; d[n++] = p->duck; d[n++] = p->root;
        d[n++] = p->scale; d[n++] = p->dly_time; d[n++] = p->dly_fb; d[n++] = p->rev_size; d[n++] = p->rev_damp;
        d[n++] = p->clock_out; d[n++] = p->cur_pat; d[n++] = p->chain; d[n++] = p->sc_src; d[n++] = p->sc_rel;
        for (k = 0; k < 3; k++) {
            d[n++] = (uint8_t)p->var_seed[k];
            d[n++] = (uint8_t)(p->var_seed[k] >> 8);
        }
        d[n++] = p->mode;
    } else {
        const romi_pattern_t *pt = &R.prj.pat[obj - 1];
        uint32_t nl = 0, at;
        for (t = 0; t < ROMI_TRACKS; t++) {
            const romi_track_t *tr = &pt->tr[t];
            d[n++] = tr->len; d[n++] = tr->mute;
            for (k = 0; k < 4; k++)
                d[n++] = tr->p[k];
            d[n++] = tr->level; d[n++] = tr->pan; d[n++] = tr->dly; d[n++] = tr->rev;
            d[n++] = tr->eu_hits; d[n++] = tr->eu_rot; d[n++] = tr->eu_prob; d[n++] = tr->eu_acc;
            d[n++] = tr->sc; d[n++] = tr->dep_src; d[n++] = (uint8_t)tr->tshift; d[n++] = tr->dep_mode;
            d[n++] = tr->follow;
            for (k = 0; k < ROMI_LFOS; k++) {
                d[n++] = tr->lfo[k].rate; d[n++] = (uint8_t)tr->lfo[k].depth;
                d[n++] = tr->lfo[k].target; d[n++] = tr->lfo[k].shape;
            }
            for (k = 0; k < 4; k++)
                d[n++] = tr->q[k];
            for (i = 0; i < ROMI_STEPS; i++) {
                const romi_step_t *st = &tr->step[i];
                uint32_t sh = (uint32_t)(st->shift + 8), nt = (uint32_t)(st->note - ROMI_NOTE_MIN);
                d[n++] = (uint8_t)((st->flags & 0xF3u) | ((sh >> 2) & 3u) << 2);
                d[n++] = (uint8_t)((nt & 0x3Fu) | (sh & 3u) << 6);
            }
        }
        at = n++;                       /* the count, once known */
        for (t = 0; t < ROMI_TRACKS; t++)
            for (i = 0; i < ROMI_STEPS; i++)
                for (k = 0; k < 8; k++)
                    if (pt->tr[t].step[i].lock[k] && nl < ROMI_MAX_LOCKS) {
                        d[n++] = (uint8_t)(t << 4 | i);
                        d[n++] = (uint8_t)k;
                        d[n++] = (uint8_t)(pt->tr[t].step[i].lock[k] - 1u);
                        nl++;
                    }
        d[at] = (uint8_t)nl;
    }
    sum = adler(d, n);
    d[n++] = (uint8_t)sum; d[n++] = (uint8_t)(sum >> 8); d[n++] = (uint8_t)(sum >> 16); d[n++] = (uint8_t)(sum >> 24);
    return n;
}

static uint8_t pk[ROMI_OBJ_MAX];        /* (static: not on the stack of a small device; main loop only) */

uint32_t romi_store_get(int obj, void *dst, uint32_t max)
{
    uint32_t n, i;
    if (obj < 0 || obj >= ROMI_NOBJ)
        return 0;
    n = pack(obj, pk);
    if (n > max)
        return 0;
    for (i = 0; i < n; i++)
        ((uint8_t *)dst)[i] = pk[i];
    return n;
}

int romi_store_set(int obj, const void *src, uint32_t len)
{
    static romi_pattern_t in;
    const uint8_t *b = (const uint8_t *)src;
    uint32_t want = obj ? 5u + ROMI_TRACKS * (19u + 4u * ROMI_LFOS + 4u + 2u * ROMI_STEPS) + 1u : 5u + 22u, n = 5, nl, j;
    int t, i, k;
    if (obj < 0 || obj >= ROMI_NOBJ || len < want + 4u || len > ROMI_OBJ_MAX)
        return -1;
    if (b[0] != 'R' || b[1] != 'M' || b[2] != (obj ? 'P' : 'S') || b[3] != ROMI_VERSION ||
        b[4] != (obj ? obj - 1 : 0))
        return -2;
    if (obj)
        want += 3u * b[want - 1u];
    if (len != want + 4u || adler(b, want) != ((uint32_t)b[want] | (uint32_t)b[want + 1u] << 8 |
                                               (uint32_t)b[want + 2u] << 16 | (uint32_t)b[want + 3u] << 24))
        return -3;
    if (!obj) {
        romi_project_t *p = &R.prj;
        p->bpm = b[n++]; p->swing = b[n++]; p->drift = b[n++]; p->duck = b[n++]; p->root = b[n++];
        p->scale = b[n++]; p->dly_time = b[n++]; p->dly_fb = b[n++]; p->rev_size = b[n++]; p->rev_damp = b[n++];
        p->clock_out = b[n++]; p->cur_pat = b[n++]; p->chain = b[n++]; p->sc_src = b[n++]; p->sc_rel = b[n++];
        for (k = 0; k < 3; k++, n += 2)
            p->var_seed[k] = (uint16_t)(b[n] | b[n + 1] << 8);
        p->mode = b[n++];
    } else {
        for (t = 0; t < ROMI_TRACKS; t++) {
            romi_track_t *tr = &in.tr[t];
            tr->len = b[n++]; tr->mute = b[n++];
            for (k = 0; k < 4; k++)
                tr->p[k] = b[n++];
            tr->level = b[n++]; tr->pan = b[n++]; tr->dly = b[n++]; tr->rev = b[n++];
            tr->eu_hits = b[n++]; tr->eu_rot = b[n++]; tr->eu_prob = b[n++]; tr->eu_acc = b[n++];
            tr->sc = b[n++]; tr->dep_src = b[n++]; tr->tshift = (int8_t)b[n++]; tr->dep_mode = b[n++];
            tr->follow = b[n++];
            for (k = 0; k < ROMI_LFOS; k++) {
                tr->lfo[k].rate = b[n++]; tr->lfo[k].depth = (int8_t)b[n++];
                tr->lfo[k].target = b[n++]; tr->lfo[k].shape = b[n++];
            }
            for (k = 0; k < 4; k++)
                tr->q[k] = b[n++];
            for (i = 0; i < ROMI_STEPS; i++) {
                romi_step_t *st = &tr->step[i];
                uint32_t b0 = b[n++], b1 = b[n++], sh = ((b0 >> 2) & 3u) << 2 | b1 >> 6;
                st->flags = (uint8_t)(b0 & 0xF3u);
                st->note = (int8_t)((int)(b1 & 0x3Fu) + ROMI_NOTE_MIN);
                st->shift = (int8_t)((int)sh - 8);
                for (k = 0; k < 8; k++)
                    st->lock[k] = 0;
            }
        }
        nl = b[n++];
        for (j = 0; j < nl; j++, n += 3) {
            uint32_t tt = b[n] >> 4, ss = b[n] & 15u, kk = b[n + 1];
            if (tt < ROMI_TRACKS && kk < 8u && b[n + 2] < 128u)
                in.tr[tt].step[ss].lock[kk] = (uint8_t)(b[n + 2] + 1u);
        }
        if (obj > 1 && !R.prj.mode) {   /* LAZY: a HARD pattern, kept aside */
            R.aside[obj - 2] = in;
            R.aside_ok |= (uint8_t)(1u << (obj - 2));
        } else {
            R.prj.pat[obj - 1] = in;
        }
        if (R.undo_pat == obj - 1)
            R.undo_ok = 0;
    }
    prj_sanitize(&R.prj);
    if (!R.prj.mode)
        derive_all();
    R.saved_sum[obj] = adler(b, want);
    R.playing = 0;
    R.pending_pat = 0xFFu;
    R.unsaved = 0;
    R.dirty = ~0u;
    return 0;
}

uint32_t romi_save_wanted(void)
{
    uint32_t mask = 0;
    int k;
    if (!R.save_wanted)
        return 0;
    R.save_wanted = 0;
    R.unsaved = 0;
    for (k = 0; k < (R.prj.mode ? ROMI_NOBJ : 2); k++) {   /* LAZY: the settings and A (B..D come from them) */
        uint32_t n = pack(k, pk);
        if (adler(pk, n - 4u) != R.saved_sum[k])
            mask |= 1u << k;
    }
    return mask;
}

void romi_store_saved(int obj)
{
    if (obj >= 0 && obj < ROMI_NOBJ) {
        uint32_t n = pack(obj, pk);
        R.saved_sum[obj] = adler(pk, n - 4u);
    }
}

romi_project_t *romi_project(void) { return &R.prj; }

void romi_init(uint32_t seed)
{
    uint32_t i;
    uint8_t *z = (uint8_t *)&R;

    for (i = 0; i < sizeof R; i++)
        z[i] = 0;
    sin_init();
    romi_panic();
    R.rng = seed | 1u;
    R.ui_rng = (seed * 2654435761u) | 1u;
    R.pending_pat = 0xFFu;
    R.solo = -1;
    R.prj.bpm = 126;
    R.prj.swing = 56;
    R.prj.drift = 48;
    R.prj.duck = 70;
    R.prj.sc_src = ROMI_KICK;
    R.prj.sc_rel = 54;                  /* about 90 ms */
    R.prj.root = 29;                    /* F1 */
    R.prj.scale = 0;
    R.prj.dly_time = 2;
    R.prj.dly_fb = 62;
    R.prj.rev_size = 70;
    R.prj.rev_damp = 60;
    R.prj.clock_out = 1;
    R.prj.cur_pat = 0;                  /* A, and B..D made from it */
    pattern_defaults(BASE);
    gen_all();
    new_seeds();
    derive_all();
    R.dirty = ~0u;
}

/* ---------------------------------------------------------------- canvas --- */
#define RGB(r, g, b) ((uint16_t)((((r) >> 3) << 11) | (((g) >> 2) << 5) | ((b) >> 3)))
#define C_BG 0x0000u
#define C_FG RGB(228, 224, 212)         /* warm white: what is set */
#define C_MID RGB(150, 147, 138)
#define C_DIM RGB(92, 90, 84)
#define C_LINE RGB(44, 43, 40)          /* empty steps, rules */
#define C_ACC RGB(255, 98, 44)          /* the one colour: where the groove is, what is selected */

static uint16_t *cv;
static int cv_y0;

static void rect(int x, int y, int w, int h, uint16_t c)
{
    int xx, yy, x1 = x + w, y1 = y + h;
    y -= cv_y0;
    y1 -= cv_y0;
    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (x1 > ROMI_W) x1 = ROMI_W;
    if (y1 > ROMI_STRIP_H) y1 = ROMI_STRIP_H;
    for (yy = y; yy < y1; yy++)
        for (xx = x; xx < x1; xx++)
            cv[yy * ROMI_W + xx] = c;
}

/* 5 x 7, columns, bit 0 at the top: 0x20 .. 0x5F, then a l m o r */
static const uint8_t FONT[69][5] = {
    {0x00,0x00,0x00,0x00,0x00},{0x00,0x00,0x5F,0x00,0x00},{0x00,0x07,0x00,0x07,0x00},{0x14,0x7F,0x14,0x7F,0x14},
    {0x24,0x2A,0x7F,0x2A,0x12},{0x23,0x13,0x08,0x64,0x62},{0x36,0x49,0x55,0x22,0x50},{0x00,0x05,0x03,0x00,0x00},
    {0x00,0x1C,0x22,0x41,0x00},{0x00,0x41,0x22,0x1C,0x00},{0x14,0x08,0x3E,0x08,0x14},{0x08,0x08,0x3E,0x08,0x08},
    {0x00,0x50,0x30,0x00,0x00},{0x08,0x08,0x08,0x08,0x08},{0x00,0x60,0x60,0x00,0x00},{0x20,0x10,0x08,0x04,0x02},
    {0x3E,0x51,0x49,0x45,0x3E},{0x00,0x42,0x7F,0x40,0x00},{0x42,0x61,0x51,0x49,0x46},{0x21,0x41,0x45,0x4B,0x31},
    {0x18,0x14,0x12,0x7F,0x10},{0x27,0x45,0x45,0x45,0x39},{0x3C,0x4A,0x49,0x49,0x30},{0x01,0x71,0x09,0x05,0x03},
    {0x36,0x49,0x49,0x49,0x36},{0x06,0x49,0x49,0x29,0x1E},{0x00,0x36,0x36,0x00,0x00},{0x00,0x56,0x36,0x00,0x00},
    {0x08,0x14,0x22,0x41,0x00},{0x14,0x14,0x14,0x14,0x14},{0x00,0x41,0x22,0x14,0x08},{0x02,0x01,0x51,0x09,0x06},
    {0x32,0x49,0x79,0x41,0x3E},{0x7E,0x11,0x11,0x11,0x7E},{0x7F,0x49,0x49,0x49,0x36},{0x3E,0x41,0x41,0x41,0x22},
    {0x7F,0x41,0x41,0x22,0x1C},{0x7F,0x49,0x49,0x49,0x41},{0x7F,0x09,0x09,0x09,0x01},{0x3E,0x41,0x49,0x49,0x7A},
    {0x7F,0x08,0x08,0x08,0x7F},{0x00,0x41,0x7F,0x41,0x00},{0x20,0x40,0x41,0x3F,0x01},{0x7F,0x08,0x14,0x22,0x41},
    {0x7F,0x40,0x40,0x40,0x40},{0x7F,0x02,0x0C,0x02,0x7F},{0x7F,0x04,0x08,0x10,0x7F},{0x3E,0x41,0x41,0x41,0x3E},
    {0x7F,0x09,0x09,0x09,0x06},{0x3E,0x41,0x51,0x21,0x5E},{0x7F,0x09,0x19,0x29,0x46},{0x46,0x49,0x49,0x49,0x31},
    {0x01,0x01,0x7F,0x01,0x01},{0x3F,0x40,0x40,0x40,0x3F},{0x1F,0x20,0x40,0x20,0x1F},{0x3F,0x40,0x38,0x40,0x3F},
    {0x63,0x14,0x08,0x14,0x63},{0x07,0x08,0x70,0x08,0x07},{0x61,0x51,0x49,0x45,0x43},{0x00,0x7F,0x41,0x41,0x00},
    {0x02,0x04,0x08,0x10,0x20},{0x00,0x41,0x41,0x7F,0x00},{0x04,0x02,0x01,0x02,0x04},{0x40,0x40,0x40,0x40,0x40},
    {0x20,0x54,0x54,0x54,0x78},{0x00,0x41,0x7F,0x40,0x00},{0x7C,0x04,0x18,0x04,0x78},{0x38,0x44,0x44,0x44,0x38},
    {0x7C,0x08,0x04,0x04,0x08},
};

static int text(int x, int y, const char *s, uint16_t c, int sc)
{
    for (; *s; s++) {
        int ch = (uint8_t)*s, g, col, row;
        if (ch == 'a') g = 64;
        else if (ch == 'l') g = 65;
        else if (ch == 'm') g = 66;
        else if (ch == 'o') g = 67;
        else if (ch == 'r') g = 68;
        else {
            if (ch >= 'a' && ch <= 'z')
                ch -= 32;
            g = ch >= 0x20 && ch <= 0x5F ? ch - 0x20 : '?' - 0x20;
        }
        for (col = 0; col < 5; col++)
            for (row = 0; row < 7; row++)
                if (FONT[g][col] >> row & 1)
                    rect(x + col * sc, y + row * sc, sc, sc, c);
        x += 6 * sc;
    }
    return x;
}
static int text_w(const char *s, int sc)
{
    int n = 0;
    while (s[n])
        n++;
    return n ? n * 6 * sc - sc : 0;
}

static void cat(char *d, const char *s)
{
    while (*d)
        d++;
    while (*s)
        *d++ = *s++;
    *d = 0;
}
static void cat_int(char *d, int v)
{
    char t[12];
    int n = 0;
    uint32_t u = (uint32_t)(v < 0 ? -v : v);
    while (*d)
        d++;
    do
        t[n++] = (char)('0' + u % 10u);
    while ((u /= 10u) && n < 11);
    if (v < 0)
        *d++ = '-';
    while (n)
        *d++ = t[--n];
    *d = 0;
}

/* ------------------------------------------------------------ parameters --- */
enum { F_NUM, F_BPM, F_PCT, F_PAN, F_ROOT, F_SCALE, F_DTIME, F_ONOFF, F_SUBRATIO, F_PRATIO, F_CHORD, F_CHAIN, F_EPROB, F_EACC, F_TRACK, F_DEPSRC, F_DEPMODE, F_SHIFT, F_LRATE, F_LDEPTH, F_LTARGET, F_LSHAPE, F_PITCH, F_MODE };
typedef struct { const char *name; uint8_t *v; uint8_t lo, hi, fmt, big; } param_t;

static const char *const TRACK_NAME[ROMI_TRACKS] = {"KICK", "SUB", "HAT", "PERC", "STAB", "CLICK"};
static const char *const PAGE_NAME[ROMI_NPAGES] = {"GROOVE", "SOUND", "MIX", "FX", "GLOBAL", "EUCLID", "SIDECHAIN", "LINK", "TIMING", "LFO 1", "LFO 2", "SOUND 2",
                                                    "GLOBAL 2"};
static const char *const SOUND_NAME[ROMI_TRACKS][4] = {
    {"TUNE", "DECAY", "PUNCH", "DRIVE"}, {"DECAY", "FM", "RATIO", "GLIDE"}, {"DECAY", "TONE", "METAL", "OPEN"},
    {"DECAY", "FM", "RATIO", "BEND"}, {"DECAY", "BRIGHT", "CHORD", "DETUNE"}, {"DECAY", "FREQ", "RESO", "SCATTER"},
};
static const char *const SOUND2_NAME[ROMI_TRACKS][4] = {
    {"PITCH", "CLICK", "P.TIME", "CRUSH"}, {"PITCH", "FM.TIME", "DRIVE", "CRUSH"}, {"PITCH", "ATTACK", "DRIVE", "CRUSH"},
    {"PITCH", "B.TIME", "DRIVE", "CRUSH"}, {"PITCH", "ATTACK", "DRIVE", "CRUSH"}, {"PITCH", "ATTACK", "DRIVE", "CRUSH"},
};
static const char *const NOTE_NAME[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

static int page_params(param_t p[4])
{
    romi_track_t *tr = &EDT->tr[R.track];
    int i;
    for (i = 0; i < 4; i++) {
        p[i].name = 0;
        p[i].v = 0;
        p[i].lo = 0;
        p[i].hi = 127;
        p[i].fmt = F_NUM;
        p[i].big = 1;
    }
#define P(i, n, ptr, l, h, f, b) (p[i].name = (n), p[i].v = (ptr), p[i].lo = (l), p[i].hi = (h), p[i].fmt = (f), p[i].big = (b))
    switch (R.page) {
    case ROMI_PG_HOME:
        P(0, "TEMPO", &R.prj.bpm, 90, 150, F_BPM, 0);
        P(1, "SWING", &R.prj.swing, 50, 75, F_PCT, 0);
        P(2, "DRIFT", &R.prj.drift, 0, 127, F_NUM, 1);
        P(3, "DUCK", &R.prj.duck, 0, 127, F_NUM, 1);
        break;
    case ROMI_PG_SOUND:
        for (i = 0; i < 4; i++)
            P(i, SOUND_NAME[R.track][i], &tr->p[i], 0, 127, F_NUM, 1);
        if (R.track == ROMI_SUB)
            p[2].fmt = F_SUBRATIO;
        if (R.track == ROMI_PERC)
            p[2].fmt = F_PRATIO;
        if (R.track == ROMI_STAB)
            p[2].fmt = F_CHORD;
        break;
    case ROMI_PG_MIX:
        P(0, "LEVEL", &tr->level, 0, 127, F_NUM, 1);
        P(1, "PAN", &tr->pan, 0, 127, F_PAN, 1);
        P(2, "DELAY", &tr->dly, 0, 127, F_NUM, 1);
        P(3, "REVERB", &tr->rev, 0, 127, F_NUM, 1);
        break;
    case ROMI_PG_FX:
        P(0, "D.TIME", &R.prj.dly_time, 0, 2, F_DTIME, 0);
        P(1, "D.FDBK", &R.prj.dly_fb, 0, 127, F_NUM, 1);
        P(2, "R.SIZE", &R.prj.rev_size, 0, 127, F_NUM, 1);
        P(3, "R.DAMP", &R.prj.rev_damp, 0, 127, F_NUM, 1);
        break;
    case ROMI_PG_EUCLID:
        P(0, "HITS", &tr->eu_hits, 0, tr->len, F_NUM, 0);
        P(1, "ROTATE", &tr->eu_rot, 0, (uint8_t)(tr->len - 1u), F_NUM, 0);
        P(2, "CHANCE", &tr->eu_prob, 0, 3, F_EPROB, 0);
        P(3, "ACCENT", &tr->eu_acc, 0, 4, F_EACC, 0);
        break;
    case ROMI_PG_TIMING: {              /* (signed values: F_SHIFT is handled apart, -8..8) */
        static char name[10];
        name[0] = 0;
        cat(name, "STEP ");
        cat_int(name, R.cursor + 1);
        P(0, name, (uint8_t *)&tr->step[R.cursor & 15u].shift, 0, 2 * ROMI_SHIFT_MAX, F_SHIFT, 0);
        P(1, "TRACK", (uint8_t *)&tr->tshift, 0, 16, F_SHIFT, 0);
        break;
    }
    case ROMI_PG_SOUND2:
        P(0, SOUND2_NAME[R.track][0], &tr->q[0], 0, 48, F_PITCH, 0);
        for (i = 1; i < 4; i++)
            P(i, SOUND2_NAME[R.track][i], &tr->q[i], 0, 127, F_NUM, 1);
        break;
    case ROMI_PG_LFO1:
    case ROMI_PG_LFO2: {
        romi_lfo_t *l = &tr->lfo[R.page - ROMI_PG_LFO1];
        P(0, "RATE", &l->rate, 0, 8, F_LRATE, 0);
        P(1, "DEPTH", (uint8_t *)&l->depth, 0, 128, F_LDEPTH, 1);
        P(2, "TARGET", &l->target, 0, 11, F_LTARGET, 0);
        P(3, "SHAPE", &l->shape, 0, 4, F_LSHAPE, 0);
        break;
    }
    case ROMI_PG_LINK:
        P(0, "SOURCE", &tr->dep_src, 0, ROMI_TRACKS, F_DEPSRC, 0);
        P(1, "MODE", &tr->dep_mode, 0, 2, F_DEPMODE, 0);
        P(2, "FOLLOW", &tr->follow, 0, ROMI_TRACKS, F_DEPSRC, 0);
        break;
    case ROMI_PG_SC:
        P(0, "SOURCE", &R.prj.sc_src, 0, ROMI_TRACKS - 1, F_TRACK, 0);
        P(1, "DEPTH", &R.prj.duck, 0, 127, F_NUM, 1);
        P(2, "RELEASE", &R.prj.sc_rel, 0, 127, F_NUM, 1);
        P(3, "AMOUNT", &tr->sc, 0, 127, F_NUM, 1);
        break;
    case ROMI_PG_GLOBAL2:
        P(0, "MODE", &R.prj.mode, 0, 1, F_MODE, 0);
        break;
    default:
        P(0, "ROOT", &R.prj.root, 24, 47, F_ROOT, 0);
        P(1, "SCALE", &R.prj.scale, 0, 3, F_SCALE, 0);
        P(2, "CLOCK", &R.prj.clock_out, 0, 1, F_ONOFF, 0);
        P(3, "CHAIN", &R.prj.chain, 0, 4, F_CHAIN, 0);
        break;
    }
#undef P
    return 4;
}

static void param_text(const param_t *p, char *t)
{
    static const char *const SCALE[4] = {"MIN", "DOR", "PHR", "PEN"};
    static const char *const DTIME[3] = {"1/16", "1/8", "3/16"};
    static const char *const CHORD[5] = {"MIN", "MIN7", "MIN9", "SUS", "5TH"};
    static const char *const CHAIN[5] = {"OFF", "A-B", "A-C", "A-D", "EVOLVE"};
    static const char *const EPROB[4] = {"25%", "50%", "75%", "100%"};
    static const char *const EACC[5] = {"OFF", "ALL", "2ND", "3RD", "4TH"};
    static const char *const DEPMODE[3] = {"WITH", "GAPS", "AFTER"};
    int v = *p->v;
    t[0] = 0;
    switch (p->fmt) {
    case F_PCT: cat_int(t, v); cat(t, "%"); break;
    case F_PAN:
        if (v == 64) cat(t, "C");
        else { cat(t, v < 64 ? "L" : "R"); cat_int(t, v < 64 ? 64 - v : v - 64); }
        break;
    case F_ROOT: cat(t, NOTE_NAME[v % 12]); cat_int(t, v / 12 - 1); break;
    case F_SCALE: cat(t, SCALE[v & 3]); break;
    case F_DTIME: cat(t, DTIME[v > 2 ? 2 : v]); break;
    case F_ONOFF: cat(t, v ? "ON" : "OFF"); break;
    case F_SUBRATIO: cat(t, "X"); cat_int(t, 1 + v * 3 / 128); break;
    case F_PRATIO: cat(t, "R"); cat_int(t, 1 + (v >> 4)); break;
    case F_CHORD: cat(t, CHORD[v * 5 / 128]); break;
    case F_CHAIN: cat(t, CHAIN[v > 4 ? 4 : v]); break;
    case F_EPROB: cat(t, EPROB[v & 3]); break;
    case F_EACC: cat(t, EACC[v > 4 ? 4 : v]); break;
    case F_TRACK: cat(t, TRACK_NAME[v % ROMI_TRACKS]); break;
    case F_DEPSRC: cat(t, v && v <= ROMI_TRACKS ? TRACK_NAME[v - 1] : "OFF"); break;
    case F_DEPMODE: cat(t, DEPMODE[v > 2 ? 2 : v]); break;
    case F_LRATE: {
        static const char *const RATE[9] = {"1/16", "1/8", "1/4", "1/2", "1 BAR", "2 BAR", "4 BAR", "8 BAR", "16 BAR"};
        cat(t, RATE[v > 8 ? 8 : v]);
        break;
    }
    case F_LTARGET: {
        static const char *const MIXT[4] = {"LEVEL", "PAN", "DELAY", "REVERB"};
        cat(t, v < 4 ? SOUND_NAME[R.track][v] : v < 8 ? MIXT[(v - 4) & 3] : SOUND2_NAME[R.track][(v - 8) & 3]);
        break;
    }
    case F_LSHAPE: {
        static const char *const SHAPE[5] = {"SINE", "TRI", "SAW", "SQR", "RAND"};
        cat(t, SHAPE[v > 4 ? 4 : v]);
        break;
    }
    case F_MODE: cat(t, v ? "HARD" : "LAZY"); break;
    case F_PITCH:                       /* semitones, 24 = none */
        if (v > 24)
            cat(t, "+");
        cat_int(t, v - 24);
        break;
    case F_LDEPTH:
    case F_SHIFT:                       /* - early, + late */
        v = (int8_t)*p->v;
        if (v > 0)
            cat(t, "+");
        cat_int(t, v);
        break;
    default: cat_int(t, v); break;
    }
}

/* ------------------------------------------------------------------ draw --- */
#define GRID_Y 25
#define LANE_H 20
#define CELL_X 46
#define CELL_W 12
#define PARAM_Y 152
#define FOOT_Y 214

static int held_step(void)              /* the lowest held white key in step mode: the step being edited, or -1 */
{
    static const uint8_t WK[16] = {0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26};
    int i;
    if (R.keys_mode || R.page == ROMI_PG_TIMING)
        return -1;
    for (i = 0; i < 16; i++)
        if (R.keys >> WK[i] & 1u)
            return i;
    return -1;
}

void romi_draw(uint16_t *px, int strip)
{
    char t[32];
    int i, lane, hs = held_step();
    param_t pp[4];
    cv = px;
    cv_y0 = strip * ROMI_STRIP_H;
    rect(0, cv_y0, ROMI_W, ROMI_STRIP_H, C_BG);

    /* header: the name, the pattern, the tempo, the transport */
    i = text(4, 5, "ro:", C_MID, 2);
    i = text(i, 5, "MINI", C_FG, 2);
    text(i, 5, "mal", C_MID, 2);
    t[0] = (char)('A' + R.prj.cur_pat);
    t[1] = 0;
    text(140, 5, t, R.pending_pat != 0xFFu ? C_DIM : C_FG, 2);
    if (R.pending_pat != 0xFFu) {
        t[0] = (char)('A' + R.pending_pat);
        text(153, 5, ">", C_DIM, 1);
        text(160, 5, t, C_ACC, 1);
    }
    t[0] = 0;
    cat_int(t, R.prj.bpm);
    text(176, 5, t, C_FG, 2);
    if (R.playing) {
        for (i = 0; i < 7; i++)         /* a triangle */
            rect(220 + i, 5 + i, 1, 14 - 2 * i, C_ACC);
    } else {
        rect(220, 7, 10, 10, C_DIM);
    }
    rect(0, 23, ROMI_W, 1, C_LINE);

    /* the grid: a lane a track, each as long as its own loop */
    for (lane = 0; lane < ROMI_TRACKS; lane++) {
        const romi_track_t *tr = &PAT->tr[lane];
        int y = GRID_Y + lane * LANE_H, cur = lane == R.track;
        int quiet = tr->mute || (R.solo >= 0 && R.solo != lane);
        if (cur)
            rect(0, y, 42, 17, R.solo == lane ? C_ACC : C_FG);
        text(3, y + 5, TRACK_NAME[lane], cur ? C_BG : R.solo == lane ? C_ACC : quiet ? C_DIM : C_MID, 1);
        if (tr->mute)
            rect(2, y + 8, text_w(TRACK_NAME[lane], 1) + 2, 1, cur ? C_BG : C_DIM);
        if ((tr->dep_src && tr->dep_src - 1 != lane) || (tr->follow && tr->follow - 1 != lane))
            rect(37, y + 7, 3, 3, C_ACC);   /* linked to another track (its steps or its notes) */
        for (i = 0; i < ROMI_STEPS; i++) {
            int x = CELL_X + i * CELL_W, on, play;
            const romi_step_t *sp = &tr->step[i];
            uint8_t f = sp->flags;
            static const uint16_t SHADE[4] = {C_FG, RGB(176, 173, 163), RGB(124, 122, 114), RGB(84, 82, 77)};
            uint16_t c;
            if (i >= tr->len) {
                rect(x + 4, y + 8, 2, 2, C_LINE);
                continue;
            }
            on = (f & ROMI_ST_ON) != 0;
            play = R.playing && R.pos[lane] == i;
            c = quiet ? C_DIM : SHADE[ROMI_ST_PROB(f)];
            if (play && on && !quiet)
                c = C_ACC;
            if (on)                     /* microtiming: the cell sits a pixel or two off its place */
                x += sp->shift / 3;
            if (!on)
                rect(x, y + 6, 10, 10, (i & 3) == 0 ? RGB(60, 58, 54) : C_LINE);
            else if (f & ROMI_ST_ACC)
                rect(x, y, 10, 16, c);  /* an accent stands taller */
            else
                rect(x, y + 6, 10, 10, c);
            if (on && (sp->lock[0] | sp->lock[1] | sp->lock[2] | sp->lock[3] | sp->lock[4] | sp->lock[5] |
                       sp->lock[6] | sp->lock[7]))
                rect(x + 3, y + 12, 4, 3, play && !quiet ? C_BG : C_ACC);   /* its own sound */
            if (on) {                   /* a ratchet splits its step */
                int n = (int)ROMI_ST_RATCH(f), j;
                for (j = 1; j < n; j++)
                    rect(x + 10 * j / n, y + 6, 1, 10, C_BG);
            }
            if (play)
                rect(x, y + 17, 10, 2, C_ACC);
            if (cur && (hs == i || (R.page == ROMI_PG_TIMING && R.cursor == i)))
                rect(x, y + 17, 10, 2, C_FG);
        }
    }
    rect(0, 147, ROMI_W, 1, C_LINE);

    /* the page: what K1 .. K4 turn */
    t[0] = 0;
    cat(t, PAGE_NAME[R.page]);
    if (R.page == ROMI_PG_SOUND || R.page == ROMI_PG_MIX || R.page == ROMI_PG_EUCLID || R.page == ROMI_PG_SC ||
        R.page == ROMI_PG_LINK || R.page == ROMI_PG_TIMING || R.page == ROMI_PG_LFO1 || R.page == ROMI_PG_LFO2 ||
        R.page == ROMI_PG_SOUND2) {
        cat(t, " ");
        cat(t, TRACK_NAME[R.track]);
    }
    text(4, PARAM_Y, t, C_ACC, 1);
    if (hs >= 0 && (R.page == ROMI_PG_SOUND || R.page == ROMI_PG_SOUND2)) {   /* a step held: its own values */
        const romi_step_t *st = &EDT->tr[R.track].step[hs];
        const romi_track_t *ct = &EDT->tr[R.track];
        int base = R.page == ROMI_PG_SOUND2 ? 4 : 0;
        t[0] = 0;
        cat(t, "STEP ");
        cat_int(t, hs + 1);
        cat(t, " LOCKS");
        text(236 - text_w(t, 1), PARAM_Y, t, C_FG, 1);
        for (i = 0; i < 4; i++) {
            int x = 4 + i * 60, lk = st->lock[base + i], pitch = base && i == 0;
            int v = lk ? lk - 1 : base ? ct->q[i] : ct->p[i];
            text(x, PARAM_Y + 14, base ? SOUND2_NAME[R.track][i] : SOUND_NAME[R.track][i], lk ? C_ACC : C_MID, 1);
            t[0] = 0;
            if (pitch && v > 24)
                cat(t, "+");
            cat_int(t, pitch ? v - 24 : v);
            text(x, PARAM_Y + 26, t, lk ? C_FG : C_DIM, 2);
            rect(x, PARAM_Y + 46, 52, 3, C_LINE);
            rect(x, PARAM_Y + 46, v * 52 / (pitch ? 48 : 127), 3, lk ? C_ACC : C_DIM);
        }
    } else if (hs >= 0) {               /* a step is held: the knobs edit it */
        const romi_step_t *st = &EDT->tr[R.track].step[hs];
        static const char *const PROB[4] = {"100%", "75%", "50%", "25%"};
        t[0] = 0;
        cat(t, "STEP ");
        cat_int(t, hs + 1);
        cat(t, st->shift < 0 ? "  EARLY " : st->shift > 0 ? "  LATE " : "");
        if (st->shift)
            cat_int(t, st->shift < 0 ? -st->shift : st->shift);
        text(236 - text_w(t, 1), PARAM_Y, t, C_FG, 1);
        text(4, PARAM_Y + 14, "NOTE", C_MID, 1);
        t[0] = 0;
        if (st->note > 0)
            cat(t, "+");
        cat_int(t, st->note);
        text(4, PARAM_Y + 26, t, C_FG, 2);
        text(64, PARAM_Y + 14, "CHANCE", C_MID, 1);
        text(64, PARAM_Y + 26, PROB[ROMI_ST_PROB(st->flags)], C_FG, 2);
        text(124, PARAM_Y + 14, "ACCENT", C_MID, 1);
        text(124, PARAM_Y + 26, st->flags & ROMI_ST_ACC ? "ON" : "OFF", C_FG, 2);
        text(184, PARAM_Y + 14, "RATCHET", C_MID, 1);
        t[0] = 0;
        cat(t, "X");
        cat_int(t, (int)ROMI_ST_RATCH(st->flags));
        text(184, PARAM_Y + 26, t, C_FG, 2);
    } else {
        page_params(pp);
        for (i = 0; i < 4; i++) {
            int x = 4 + i * 60;
            if (!pp[i].name)
                continue;
            text(x, PARAM_Y + 14, pp[i].name, C_MID, 1);
            param_text(&pp[i], t);
            text(x, PARAM_Y + 26, t, C_FG, text_w(t, 2) > 54 ? 1 : 2);
            rect(x, PARAM_Y + 46, 52, 3, C_LINE);
            if (pp[i].fmt == F_SHIFT || pp[i].fmt == F_LDEPTH) {   /* signed: from the middle */
                int v = (int8_t)*pp[i].v, m = pp[i].hi / 2;
                rect(x + 25, PARAM_Y + 44, 2, 7, C_MID);
                if (v < 0)
                    rect(x + 26 + v * 26 / m, PARAM_Y + 46, -v * 26 / m, 3, C_ACC);
                else
                    rect(x + 26, PARAM_Y + 46, v * 26 / m, 3, C_ACC);
            } else if (pp[i].hi > pp[i].lo)
                rect(x, PARAM_Y + 46, (*pp[i].v - pp[i].lo) * 52 / (pp[i].hi - pp[i].lo), 3, C_FG);
        }
    }
    rect(0, FOOT_Y - 4, ROMI_W, 1, C_LINE);

    /* the foot: a message for a moment, else where we are */
    if (R.msg_until) {
        i = text(4, FOOT_Y + 2, R.msg[0], C_ACC, 2);
        text(i + 6, FOOT_Y + 2, R.msg[1], C_FG, 2);
    } else {
        t[0] = 0;
        cat(t, TRACK_NAME[R.track]);
        cat(t, " LEN ");
        cat_int(t, PAT->tr[R.track].len);
        text(4, FOOT_Y, t, C_FG, 1);
        text(236 - text_w(R.keys_mode ? "KEYS" : "STEPS", 1), FOOT_Y, R.keys_mode ? "KEYS" : "STEPS",
             R.keys_mode ? C_ACC : C_MID, 1);
        if (R.unsaved)
            text(150, FOOT_Y, "UNSAVED", C_DIM, 1);
        t[0] = 0;
        if (R.prj.mode && R.prj.cur_pat)
            cat(t, "HARD: EDITS GO TO THIS PATTERN");
        else if (R.prj.cur_pat == 1)
            cat(t, "B: A VARIED  NEW: ANOTHER");
        else if (R.prj.cur_pat == 2)
            cat(t, "C: A WITH ROLLS  NEW: ANOTHER");
        else if (R.prj.cur_pat == 3) {
            cat(t, "D: A IN ");
            cat(t, NOTE_NAME[(R.prj.root + key_step() + 120) % 12]);
            cat(t, "  NEW: ANOTHER");
        }
        text(4, FOOT_Y + 13, R.keys_mode ? "KEYS PLAY THE TRACK  REC: STEPS" :
             R.page == ROMI_PG_TIMING ? "SELECT: NEXT HIT  KEY: PICK STEP" :
             t[0] ? t : "SEL MUTE/SOLO  ARP MUTATE  LFO 1/2", R.prj.cur_pat && !R.keys_mode ? C_MID : C_DIM, 1);
    }
}

/* ----------------------------------------------------------------- input --- */
#define STRIP_ALL 0x1Fu
#define STRIP_GRID 0x07u                /* rows 0 .. 143: header and grid */
#define STRIP_PAGE 0x18u                /* rows 144 .. 239 */

void romi_message(const char *a, const char *b)
{
    int i;
    for (i = 0; i < 19 && a && a[i]; i++)
        R.msg[0][i] = a[i];
    R.msg[0][i] = 0;
    for (i = 0; i < 19 && b && b[i]; i++)
        R.msg[1][i] = b[i];
    R.msg[1][i] = 0;
    R.msg_until = R.now + 1100u;
    if (!R.msg_until)
        R.msg_until = 1;
    R.dirty |= STRIP_PAGE;
}

static void changed(void)
{
    R.unsaved = 1;
    R.base_changed = 1;                 /* (B..D follow A at the end of this frame) */
    R.dirty |= STRIP_ALL;
}
static void keep_undo(void)
{
    R.undo = *EDT;
    R.undo_pat = R.prj.mode ? R.prj.cur_pat : 0;
    R.undo_ok = 1;
}
static int clampi(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }

/* LAZY <-> HARD. Into HARD: B..D are the HARD patterns kept aside (if there are), else copies of A ("all the same,
 * vary them yourself"). Into LAZY: B..D go aside (nothing is lost) and are made from A again. */
static void set_mode(uint8_t pro)
{
    int k;
    R.prj.mode = pro ? 1u : 0u;
    for (k = 1; k < ROMI_PATTERNS; k++) {
        if (pro) {
            R.prj.pat[k] = R.aside_ok >> (k - 1) & 1u ? R.aside[k - 1] : *BASE;
        } else {
            R.aside[k - 1] = R.prj.pat[k];
            R.aside_ok |= (uint8_t)(1u << (k - 1));
        }
    }
    if (!pro)
        derive_all();
    R.undo_ok = 0;
    romi_message("MODE", pro ? "HARD" : "LAZY");
    R.unsaved = 1;
    R.dirty |= STRIP_ALL;
}

void romi_input(uint32_t buttons, uint32_t keys, const int32_t enc[ROMI_NE], uint32_t now_ms)
{
    static const uint8_t WK[16] = {0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26};
    static const uint8_t BK[11] = {1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25};
    uint32_t pressed = buttons & ~R.btn, kdown = keys & ~R.keys, kup = R.keys & ~keys;
    romi_track_t *tr;
    int i, hs, e_sel = (int)enc[ROMI_E_SELECT], e_pre = (int)enc[ROMI_E_PRESET];
    R.now = now_ms;
    hs = held_step();                   /* from the keys as they were: a step held since before this call */
    R.btn = buttons;
    R.keys = keys;

    if (R.msg_until && (int32_t)(now_ms - R.msg_until) >= 0) {
        R.msg_until = 0;
        R.dirty |= STRIP_PAGE;
    }
    if (R.gstep_ui != R.seen_gstep) {   /* the playhead moved */
        R.seen_gstep = R.gstep_ui;
        R.dirty |= STRIP_GRID;
    }

    /* transport and pages */
    if (pressed & 1u << ROMI_B_PLAY) {
        if (R.playing)
            R.want_stop = 1;
        else
            R.want_play = 1;
        R.dirty |= STRIP_ALL;
    }
    {
        static const uint8_t PAGE_BTN[ROMI_NPAGES] = {ROMI_B_HOME, ROMI_B_EDIT, ROMI_B_ENV, ROMI_B_FX, ROMI_B_GLO,
                                                  ROMI_B_SEQ, ROMI_B_FX, ROMI_B_SEQ, ROMI_B_SEQ, ROMI_B_LFO,
                                                  ROMI_B_LFO, ROMI_B_EDIT, ROMI_B_GLO};
        uint8_t was = R.page;
        for (i = 0; i < ROMI_PG_EUCLID; i++)
            if (pressed & 1u << PAGE_BTN[i]) {
                R.page = (uint8_t)i;
                R.dirty |= STRIP_ALL;
            }
        if ((pressed & 1u << ROMI_B_FX) && was == ROMI_PG_FX)
            R.page = ROMI_PG_SC;        /* FX again: the sidechain */
        if ((pressed & 1u << ROMI_B_EDIT) && was == ROMI_PG_SOUND)
            R.page = ROMI_PG_SOUND2;    /* EDIT again: SOUND 2 */
        if ((pressed & 1u << ROMI_B_GLO) && was == ROMI_PG_GLOBAL)
            R.page = ROMI_PG_GLOBAL2;   /* GLO again: GLOBAL 2 */
        if (pressed & 1u << ROMI_B_LFO) {   /* LFO: the first LFO's page; again: the second's */
            R.page = was == ROMI_PG_LFO1 ? ROMI_PG_LFO2 : ROMI_PG_LFO1;
            R.dirty |= STRIP_ALL;
        }
    }
    if (pressed & 1u << ROMI_B_SEQ) {   /* back to the steps, and the page that spreads them */
        R.keys_mode = 0;
        /* SEQ again: the link to another track; and again: the timing of single hits and of the track */
        R.page = R.page == ROMI_PG_EUCLID ? ROMI_PG_LINK : R.page == ROMI_PG_LINK ? ROMI_PG_TIMING : ROMI_PG_EUCLID;
        R.eu_armed = 1;
        R.dirty |= STRIP_ALL;
    }
    if (pressed & 1u << ROMI_B_REC) {
        R.keys_mode ^= 1u;
        R.dirty |= STRIP_ALL;
        romi_message("KEYS", R.keys_mode ? "PLAY" : "STEPS");
    }
    if (pressed & 1u << ROMI_B_SAVE) {  /* (no copying between patterns: B..D are made from A) */
        R.save_wanted = 1;
        romi_message("SAVED", "");
        R.dirty |= STRIP_ALL;
    }

    if (hs >= 0 && e_sel) {             /* a step held: SELECT nudges it early or late */
        romi_step_t *st = &EDT->tr[R.track].step[hs];
        st->shift = (int8_t)clampi(st->shift + e_sel, -ROMI_SHIFT_MAX, ROMI_SHIFT_MAX);
        st->flags |= ROMI_ST_ON;
        R.step_edited = 1;
        e_sel = 0;
        changed();
    }

    if (R.page == ROMI_PG_TIMING && !R.keys_mode && e_sel) {   /* SELECT walks the cursor from hit to hit */
        const romi_track_t *ct = &EDT->tr[R.track];
        int n = e_sel < 0 ? -e_sel : e_sel, dir = e_sel < 0 ? -1 : 1, len = ct->len ? ct->len : 1, k;
        while (n--)
            for (k = 1; k <= len; k++) {
                int c = ((int)R.cursor + dir * k % len + len) % len;
                if (ct->step[c].flags & ROMI_ST_ON) {
                    R.cursor = (uint8_t)c;
                    break;
                }
            }
        e_sel = 0;
        R.dirty |= STRIP_ALL;
    }

    /* the track */
    i = e_sel;
    if (R.keys_mode) {
        int o = R.octave + !!(pressed & 1u << ROMI_B_OCTUP) - !!(pressed & 1u << ROMI_B_OCTDN);
        R.octave = (int8_t)clampi(o, -2, 2);
    } else {
        i += !!(pressed & 1u << ROMI_B_OCTUP) - !!(pressed & 1u << ROMI_B_OCTDN);
    }
    if (i) {
        R.track = (uint8_t)clampi((int)R.track + i, 0, ROMI_TRACKS - 1);
        R.eu_armed = 1;
        R.dirty |= STRIP_ALL;
    }
    tr = &EDT->tr[R.track];
    if (R.cursor >= tr->len)
        R.cursor = (uint8_t)(tr->len ? tr->len - 1u : 0u);

    if (enc[ROMI_E_ALGO]) {             /* the loop's length */
        tr->len = (uint8_t)clampi((int)tr->len + (int)enc[ROMI_E_ALGO], 1, ROMI_STEPS);
        if (tr->eu_hits > tr->len)
            tr->eu_hits = tr->len;
        if (tr->eu_rot >= tr->len)
            tr->eu_rot = (uint8_t)(tr->len - 1u);
        if (R.page == ROMI_PG_EUCLID)   /* on its page the spread follows the length */
            apply_euclid(R.track);
        changed();
    }
    if (e_pre) {                        /* the pattern: at the next bar while playing */
        int cur = R.pending_pat != 0xFFu ? R.pending_pat : R.prj.cur_pat;
        int p = clampi(cur + e_pre, 0, ROMI_PATTERNS - 1);
        R.eu_armed = 1;
        if (R.playing)
            R.pending_pat = (uint8_t)(p == R.prj.cur_pat ? 0xFF : p);
        else
            R.prj.cur_pat = (uint8_t)p;
        R.dirty |= STRIP_ALL;
    }

    /* the pattern's helpers */
    if (hs >= 0 && (pressed & 1u << ROMI_B_SEL)) {   /* a step held: SEL takes its shift and locks away */
        step_plain(&tr->step[hs]);
        R.step_edited = 1;
        romi_message("STEP", "PLAIN");
        changed();
    } else if (pressed & 1u << ROMI_B_SEL) {   /* decided at the release: see below */
        R.sel_t = now_ms ? now_ms : 1u;
        R.sel_used = 0;
    }
    if (pressed & 1u << ROMI_B_ARP) {
        keep_undo();
        mutate_track(R.track);
        romi_message("MUTATE", TRACK_NAME[R.track]);
        changed();
    }
    if (R.new_t && (R.keys_mode || !(keys >> 22 & 1u)))   /* NEW let go (black key 10: key 22) */
        R.new_t = 0;
    if (R.new_t && now_ms - R.new_t >= 450u) {        /* NEW held: the whole groove (UNDO: back to before the press) */
        R.new_t = 0;
        gen_all();
        romi_message("NEW", "GROOVE");
        changed();
    }
    /* SEL let go: a tap mutes the selected track, a hold (half a second) solos it; but if track keys were pressed
     * while it was held (each muting its own track), nothing more */
    if (R.sel_t && !(buttons & 1u << ROMI_B_SEL)) {
        if (R.sel_used) {
            /* (the track keys did it) */
        } else if (now_ms - R.sel_t < 450u) {
            tr->mute ^= 1u;
            changed();
        } else {
            R.solo = (int8_t)(R.solo == (int)R.track ? -1 : (int)R.track);
            romi_message("SOLO", R.solo < 0 ? "OFF" : TRACK_NAME[R.track]);
            R.dirty |= STRIP_ALL;
        }
        R.sel_t = 0;
    }

    /* K1 .. K4: the held step, or the page */
    if (hs >= 0 && (R.page == ROMI_PG_SOUND || R.page == ROMI_PG_SOUND2)) {   /* the step's own sound: locks */
        romi_step_t *st = &tr->step[hs];
        int base = R.page == ROMI_PG_SOUND2 ? 4 : 0;
        for (i = 0; i < 4; i++) {
            int d = (int)enc[ROMI_E_K1 + i], li = base + i, pitch = base && i == 0;
            int v = st->lock[li] ? st->lock[li] - 1 : base ? tr->q[i] : tr->p[i];
            if (!d)
                continue;
            if (!st->lock[li] && lock_count(EDT) >= ROMI_MAX_LOCKS) {   /* a new lock: is there room? */
                romi_message("LOCKS", "FULL");
                continue;
            }
            st->lock[li] = (uint8_t)(clampi(v + (pitch ? d : d * (d > 1 || d < -1 ? 4 : 2)), 0, pitch ? 48 : 127) + 1);
            st->flags |= ROMI_ST_ON;
            R.step_edited = 1;
            changed();
        }
    } else if (hs >= 0) {
        romi_step_t *st = &tr->step[hs];
        int any = 0;
        if (enc[ROMI_E_K1]) {
            st->note = (int8_t)clampi(st->note + (int)enc[ROMI_E_K1], -24, 24);
            any = 1;
        }
        if (enc[ROMI_E_K2]) {           /* clockwise: more likely */
            int p = clampi((int)ROMI_ST_PROB(st->flags) - (int)enc[ROMI_E_K2], 0, 3);
            st->flags = (uint8_t)((st->flags & ~0x30u) | (uint32_t)p << 4);
            any = 1;
        }
        if (enc[ROMI_E_K3]) {
            st->flags = (uint8_t)(enc[ROMI_E_K3] > 0 ? st->flags | ROMI_ST_ACC : st->flags & ~ROMI_ST_ACC);
            any = 1;
        }
        if (enc[ROMI_E_K4]) {
            int n = clampi((int)(st->flags & 3u) + (int)enc[ROMI_E_K4], 0, 3);
            st->flags = (uint8_t)((st->flags & ~3u) | (uint32_t)n);
            any = 1;
        }
        if (any) {
            st->flags |= ROMI_ST_ON;    /* editing a step sets it */
            R.step_edited = 1;
            changed();
        }
    } else {
        param_t pp[4];
        uint8_t mode_was = R.prj.mode;
        page_params(pp);
        for (i = 0; i < 4; i++) {
            int d = (int)enc[ROMI_E_K1 + i];
            if (!d || !pp[i].v)
                continue;
            if (pp[i].big)              /* 0..127: two a detent, more when turned fast */
                d *= d > 1 || d < -1 ? 4 : 2;
            if (R.page == ROMI_PG_EUCLID && R.eu_armed) {
                keep_undo();            /* what the steps were before the page spread them */
                R.eu_armed = 0;
            }
            if (pp[i].fmt == F_SHIFT || pp[i].fmt == F_LDEPTH)   /* signed */
                *pp[i].v = (uint8_t)(int8_t)clampi((int)(int8_t)*pp[i].v + d, -(int)pp[i].hi / 2,
                                                   pp[i].fmt == F_LDEPTH ? pp[i].hi / 2 - 1 : pp[i].hi / 2);
            else
                *pp[i].v = (uint8_t)clampi((int)*pp[i].v + d, pp[i].lo, pp[i].hi);
            if (R.page == ROMI_PG_EUCLID)
                apply_euclid(R.track);
            changed();
        }
        if (R.prj.mode != mode_was)
            set_mode(R.prj.mode);
    }

    /* the keys */
    if (R.keys_mode) {
        for (i = 0; i < ROMI_NKEYS; i++)
            if (kdown >> i & 1u) {
                int note = i - 7 + 12 * R.octave;   /* key 7 is C4: the base note */
                tq_push(R.track, note, 110);
                if (R.playing) {        /* written into the step it fell on */
                    uint32_t len = tr->len ? tr->len : 1u;
                    set_step(tr, R.pos[R.track] % len, 0, 0, clampi(note, ROMI_NOTE_MIN, ROMI_NOTE_MAX));
                    changed();
                }
            }
    } else {
        for (i = 0; i < 16; i++)        /* a white key is a step: a tap toggles it */
            if (kup >> WK[i] & 1u) {
                if (R.page == ROMI_PG_TIMING) {   /* on the timing page a key picks the step, and leaves it as it is */
                    if (i < tr->len)
                        R.cursor = (uint8_t)i;
                    R.dirty |= STRIP_ALL;
                } else if (R.step_edited) {
                    if (!(keys & 0x7FFFFFFu))
                        R.step_edited = 0;
                } else if (i < tr->len) {
                    tr->step[i].flags ^= ROMI_ST_ON;
                    changed();
                }
            }
        if (kdown || kup)
            R.dirty |= STRIP_GRID | STRIP_PAGE;
        for (i = 0; i < 11; i++) {
            if (!(kdown >> BK[i] & 1u))
                continue;
            if (i < ROMI_TRACKS && (buttons & 1u << ROMI_B_SEL) && R.sel_t) {
                /* SEL held: the track key mutes its track or lets it play, the selection stays */
                EDT->tr[i].mute ^= 1u;
                R.sel_used = 1;
                romi_message(EDT->tr[i].mute ? "MUTE" : "PLAY", TRACK_NAME[i]);
                changed();
            } else if (i < ROMI_TRACKS) {   /* the first six black keys: the tracks, heard as chosen */
                R.track = (uint8_t)i;
                R.eu_armed = 1;
                tr = &EDT->tr[R.track];
                if (!R.playing)
                    tq_push(i, 0, 110);
                R.dirty |= STRIP_ALL;
            } else if (i == 6) {
                int k;
                keep_undo();
                for (k = 0; k < ROMI_STEPS; k++) {
                    tr->step[k].flags = 0;
                    step_plain(&tr->step[k]);
                }
                romi_message("CLEAR", TRACK_NAME[R.track]);
                changed();
            } else if (i == 7 || i == 8) {
                keep_undo();
                rotate_track(R.track, i == 8 ? 1 : -1);
                changed();
            } else if (i == 9 && R.prj.cur_pat && !R.prj.mode) {   /* LAZY, NEW on B..D: that variation again */
                static const char *const VAR[3] = {"VARIATION", "ROLLS", "KEY"};
                R.prj.var_seed[R.prj.cur_pat - 1] = (uint16_t)(xs32(&R.ui_rng) >> 8);
                derive(R.prj.cur_pat);
                romi_message("NEW", VAR[R.prj.cur_pat - 1]);
                R.new_t = now_ms ? now_ms : 1u;
                R.unsaved = 1;
                R.dirty |= STRIP_ALL;
            } else if (i == 9) {            /* NEW: the selected track, at once; held, the whole groove */
                keep_undo();
                gen_track(R.track);
                romi_message("NEW", TRACK_NAME[R.track]);
                R.new_t = now_ms ? now_ms : 1u;
                changed();
            } else if (R.undo_ok && R.undo_pat == (R.prj.mode ? R.prj.cur_pat : 0)) {
                static romi_pattern_t now;      /* (static: not on a small stack) */
                now = *EDT;
                *EDT = R.undo;
                R.undo = now;           /* undo again: redo */
                romi_message("UNDO", "");
                changed();
            }
        }
    }
    if (R.evolve) {                     /* EVOLVE came round: new variations of A */
        R.evolve = 0;
        if (!R.prj.mode) {
            new_seeds();
            R.base_changed = 1;
            R.unsaved = 1;
        }
    }
    if (R.base_changed) {
        if (!R.prj.mode)
            derive_all();
        R.base_changed = 0;
        R.dirty |= STRIP_ALL;
    }
}

uint32_t romi_dirty(void)
{
    uint32_t d = R.dirty & STRIP_ALL;
    R.dirty = 0;
    return d;
}

void romi_lights(uint32_t *buttons, uint32_t *keys, uint32_t *dim_buttons, uint32_t *dim_keys)
{
    static const uint8_t WK[16] = {0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26};
    static const uint8_t BK[11] = {1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25};
    static const uint8_t PAGE_BTN[ROMI_NPAGES] = {ROMI_B_HOME, ROMI_B_EDIT, ROMI_B_ENV, ROMI_B_FX, ROMI_B_GLO,
                                                  ROMI_B_SEQ, ROMI_B_FX, ROMI_B_SEQ, ROMI_B_SEQ, ROMI_B_LFO,
                                                  ROMI_B_LFO, ROMI_B_EDIT, ROMI_B_GLO};
    const romi_track_t *tr = &PAT->tr[R.track];
    uint32_t b = 1u << PAGE_BTN[R.page], k = 0, dk = 0;
    int i;
    if (R.playing)
        b |= 1u << ROMI_B_PLAY;
    if (R.keys_mode)
        b |= 1u << ROMI_B_REC;
    if (tr->mute || R.solo >= 0)
        b |= 1u << ROMI_B_SEL;
    if (R.unsaved)
        b |= 1u << ROMI_B_SAVE;
    if (R.keys_mode) {
        k = R.keys;
    } else {
        for (i = 0; i < 16; i++) {
            if (i >= tr->len)
                continue;
            if (tr->step[i].flags & ROMI_ST_ON)
                k |= 1u << WK[i];
            else
                dk |= 1u << WK[i];      /* the loop's length shows as a glow */
            if (R.playing && R.pos[R.track] == i)
                k ^= 1u << WK[i];       /* the playhead inverts its step */
        }
        for (i = 0; i < ROMI_TRACKS; i++) {
            if (i == R.track || R.flash[i])
                k |= 1u << BK[i];
            else if (!PAT->tr[i].mute && R.solo < 0)
                dk |= 1u << BK[i];
            R.flash[i] = 0;
        }
    }
    *buttons = b;
    *keys = k;
    *dim_buttons = ~b & ((1u << ROMI_NB) - 1u);
    *dim_keys = dk & ~k;
}

int romi_state(int what)
{
    const romi_track_t *tr = &PAT->tr[R.track];
    int i, n = 0;
    switch (what) {
    case ROMI_Q_PLAYING: return R.playing;
    case ROMI_Q_TRACK: return R.track;
    case ROMI_Q_PAGE: return R.page;
    case ROMI_Q_BPM: return R.prj.bpm;
    case ROMI_Q_GSTEP: return (int)R.gstep;
    case ROMI_Q_PATTERN: return R.prj.cur_pat;
    case ROMI_Q_KEYS_MODE: return R.keys_mode;
    case ROMI_Q_LEN: return tr->len;
    case ROMI_Q_STEPS_ON:
        for (i = 0; i < ROMI_STEPS; i++)
            n += (tr->step[i].flags & ROMI_ST_ON) != 0;
        return n;
    case ROMI_Q_MUTE: return tr->mute;
    case ROMI_Q_UNSAVED: return R.unsaved;
    case ROMI_Q_POS: return R.pos[R.track];
    case ROMI_Q_SOLO: return R.solo;
    case ROMI_Q_CURSOR: return R.cursor;
    case ROMI_Q_DENSITY: return R.density;
    case ROMI_Q_KEY_STEP: return key_step();
    case ROMI_Q_LFO_PAGE: return R.page == ROMI_PG_LFO1 ? 1 : R.page == ROMI_PG_LFO2 ? 2 : 0;
    case ROMI_Q_HITS + 0: case ROMI_Q_HITS + 1: case ROMI_Q_HITS + 2: case ROMI_Q_HITS + 3: case ROMI_Q_HITS + 4:
    case ROMI_Q_HITS + 5: return (int)R.hits[what - ROMI_Q_HITS];
    case ROMI_Q_NOTE + 0: case ROMI_Q_NOTE + 1: case ROMI_Q_NOTE + 2: case ROMI_Q_NOTE + 3: case ROMI_Q_NOTE + 4:
    case ROMI_Q_NOTE + 5: return R.last_note[what - ROMI_Q_NOTE];
    default: return -1;
    }
}
