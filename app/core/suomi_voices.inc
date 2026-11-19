/* SPDX-License-Identifier: MIT
 * ro:MINImal, style SUOMI: the six voices of suom1saundi (github.com/g0rst/suom1saundi), on ro:MINImal's tracks.
 * Included by romi.c ahead of trig() when ROMI_SUOMI is 1. The first thing to go if the FM-1 runs short of time:
 * build with ROMI_SUOMI 0 (or make it a firmware of its own) and ro:MINImal is as it was.
 *
 *   track   0 POTKU  1 BASSO  2 HATTU  3 HAPPO  4 PIIP  5 KLIKKI (ro:MINImal: KICK SUB HAT PERC STAB CLICK)
 *   KLIKKI is ro:MINImal's click (suom1saundi's OUTO, the FM zaps, left out: it fits better).
 *
 * suom1saundi has eight sound parameters a track; here SOUND holds its first four, SOUND 2 keeps ro:MINImal's shape
 * (PITCH, one of the track's own, DRIVE, CRUSH) and the other three of suom1saundi's second page stay at its
 * defaults. The glide of BASSO, HAPPO and PIIP is the track's GLIDE (TIMING page), their slides its SLIDE steps. */

/* BASSO and HAPPO: one oscillator (saw to square, band-limited) into a resonant low-pass whose cutoff an envelope
 * moves; an accent opens it further, a slide glides to the note without a new attack */
typedef struct {
    float ph, sph, f, ft, gc, amp, ac, att, fenv, fc16, cut, emod, k, wave, sub, drive, norm, vel;
    float a1, a2, a3, g1, ic1, ic2, lp;
    uint32_t ctl;
} acid_t;

static struct {
    struct { float ph, amp, ac, penv, pc, f0, pd, drive, norm, vel, click_g, body; int32_t click, hold; } kick;
    acid_t basso, happo;
    struct { float ph, mph, ph2, mph2, f, amp, ac, metal, lp, vel, chip, cph, nz, att, atc, pan, cut; uint32_t lfsr; } hat;
    struct { float ph, ph2, nph, f, ft, gc, amp, ac, att, vph, vinc, vdep, pwm, bend, benv, bc, det, vel, nz, mul[3];
             int32_t arp_n, arp_i, arp_cnt, arp_len; uint32_t lfsr; uint8_t wave; } piip;
} SU;

/* PIIP's arpeggios, a note a frame as on a sound chip: none, octave, minor, major, sus4, fifth and octave, diminished */
static const int8_t PIIP_ARP[7][3] = {{0, 0, 0}, {0, 12, 0}, {0, 3, 7}, {0, 4, 7}, {0, 5, 7}, {0, 7, 12}, {0, 3, 6}};
static const uint8_t PIIP_ARP_N[7] = {1, 2, 3, 3, 3, 3, 3};
/* suom1saundi's second page, the three that are not on SOUND 2 here: (the one in SOUND 2's second place is -1) */
static const int16_t SU_EXTRA[ROMI_TRACKS][4] = {
    {-1, -1, 20, 10},                   /* POTKU: SNAP (SOUND 2 P.TIME), CLICK (SOUND 2), HOLD, BODY */
    {-1, 40, -1, 40},                   /* BASSO: WAVE (SOUND 2), SUB, GLIDE (TIMING), DRIVE */
    {-1, 0, 20, 50},                    /* HATTU: CHIP (SOUND 2), SHAKE, SPREAD, CUT */
    {-1, 90, -1, 60},                   /* HAPPO: WAVE (SOUND 2), ACCENT, GLIDE (TIMING), DRIVE */
    {-1, 30, 64, 0},                    /* PIIP: SPEED (SOUND 2), PWM, BEND, DETUNE */
    {-1, -1, -1, -1},                   /* (KLIKKI: ro:MINImal's click) */
};

static void su_panic(void)
{
    SU.kick.amp = SU.basso.amp = SU.hat.amp = SU.happo.amp = SU.piip.amp = 0.0f;
    if (!SU.hat.lfsr)
        SU.hat.lfsr = SU.piip.lfsr = 0x4321u;
}

/* the filter's coefficients from its envelope: every 16 samples */
static void acid_ctl(acid_t *a)
{
    float fc = a->cut * fexp2(a->emod * a->fenv), w, g;
    if (fc > 15000.0f)
        fc = 15000.0f;
    w = fc * (0.5f * INV_SR);
    g = fsin(w) / fsin(w + 0.25f);      /* tan(pi fc / sr) */
    a->a1 = 1.0f / (1.0f + g * (g + a->k));
    a->a2 = g * a->a1;
    a->a3 = g * a->a2;
    a->g1 = g / (1.0f + g);
    a->fenv *= a->fc16;
}

static inline float blep(float t, float dt)   /* the step of a saw, band-limited */
{
    if (t < dt) {
        t /= dt;
        return t + t - t * t - 1.0f;
    }
    if (t > 1.0f - dt) {
        t = (t - 1.0f) / dt;
        return t * t + t + t + 1.0f;
    }
    return 0.0f;
}

static inline float acid_run(acid_t *a)
{
    float dt, saw, p2, x, v1, v2, v3;
    if (a->amp <= 1e-4f) {
        a->ic1 = a->ic2 = a->lp = 0.0f;
        return 0.0f;
    }
    if ((a->ctl++ & 15u) == 0u)
        acid_ctl(a);
    a->f += (a->ft - a->f) * a->gc;
    dt = a->f * INV_SR;
    a->ph += dt;
    if (a->ph >= 1.0f)
        a->ph -= 1.0f;
    saw = 2.0f * a->ph - 1.0f - blep(a->ph, dt);
    x = saw;
    if (a->wave > 0.0f) {               /* a square is a saw less the same saw half a cycle on */
        p2 = a->ph + 0.5f;
        if (p2 >= 1.0f)
            p2 -= 1.0f;
        x += (-(2.0f * p2 - 1.0f - blep(p2, dt))) * a->wave;
    }
    if (a->sub > 0.0f) {                /* a sine an octave below */
        a->sph += dt * 0.5f;
        if (a->sph >= 1.0f)
            a->sph -= 1.0f;
        x += fsin(a->sph) * a->sub;
    }
    x = clip1(x * a->drive) * a->norm;
    v3 = x - a->ic2;
    v1 = a->a1 * a->ic1 + a->a2 * v3;
    v2 = a->ic2 + a->a2 * a->ic1 + a->a3 * v3;
    a->ic1 = 2.0f * v1 - a->ic1;
    a->ic2 = 2.0f * v2 - a->ic2;
    a->lp += (v2 - a->lp) * a->g1;      /* a third pole: 18 dB an octave */
    x = clip1(a->lp * 0.8f) * a->amp * a->att * a->vel;
    a->att += (1.0f - a->att) * 0.02f;
    a->amp *= a->ac;
    return x;
}

/* s: CUTOFF RESO ENVMOD DECAY | WAVE SUB-or-ACCENT GLIDE DRIVE */
static void acid_trig(acid_t *a, int t, const uint8_t *s, float hz, float vel, int acc, int slide, int is_bass)
{
    float g = 1.0f + (float)s[7] * (5.0f / 127.0f), accent = is_bass ? 0.5f : (float)s[5] * (1.0f / 127.0f);
    float dec = pmap(drifted(t, 1, s[3]), 0.03f, 5.0f);
    a->ft = hz;
    a->cut = pmap(drifted(t, 0, s[0]), is_bass ? 45.0f : 70.0f, 6.5f);
    a->k = 2.0f - (float)s[1] * (1.93f / 127.0f);
    a->emod = (float)s[2] * (5.0f / 127.0f) + (acc ? accent * 1.6f : 0.0f);
    a->wave = (float)s[4] * (1.0f / 127.0f);
    a->sub = is_bass ? (float)s[5] * (0.9f / 127.0f) : 0.0f;
    a->drive = g;
    a->norm = 1.0f / clip1(g);
    a->vel = vel * (acc ? 1.0f + accent * 0.35f : 1.0f);
    a->ac = decay_coef(acc && !is_bass ? dec * 1.5f : dec);
    a->fc16 = decay_coef(dec * 0.6f / 16.0f);
    a->gc = s[6] ? 1.0f - decay_coef(pmap((float)s[6], 0.004f, 5.0f)) : 1.0f;
    if (slide && a->amp > 0.02f) {      /* a slide: the note glides, the envelopes go on */
        if (!s[6])
            a->gc = 1.0f - decay_coef(0.05f);
        a->amp = a->amp * 0.5f + 0.5f;
        return;
    }
    if (a->amp < 0.05f) {
        a->att = 0.0f;
        a->ph = a->sph = 0.0f;
        a->f = hz;
    } else if (!s[6]) {
        a->f = hz;                      /* (with GLIDE, a note over the last one glides there) */
    }
    a->amp = 1.0f;
    a->fenv = 1.0f;
    a->ctl = 0;
}

static float semis(float n) { return fexp2(n * (1.0f / 12.0f)); }

/* a hit: p the SOUND page (locks and LFOs applied), q SOUND 2's; note as ro:MINImal hands it (PITCH added) */
static void su_trig(int t, int note, float vel, int acc, int slide, const uint8_t *p, const uint8_t *q, float root)
{
    const romi_track_t *tr = &PAT->tr[t];
    uint8_t s[8];
    int i;
    for (i = 0; i < 4; i++) {
        s[i] = p[i];
        s[4 + i] = SU_EXTRA[t][i] >= 0 ? (uint8_t)SU_EXTRA[t][i] : q[1];
    }
    if (t == ROMI_KICK) {               /* POTKU: SNAP is SOUND 2's third (P.TIME, as ro:MINImal's kick) */
        s[4] = q[2];
        s[5] = q[1];
    } else if (t == ROMI_SUB || t == ROMI_PERC) {
        s[6] = tr->glide;               /* BASSO, HAPPO: GLIDE on the TIMING page */
    }
    switch (t) {
    case ROMI_KICK: {                   /* TUNE DECAY SWEEP DRIVE | SNAP CLICK HOLD BODY */
        float g = 1.0f + (float)s[3] * (6.0f / 127.0f);
        SU.kick.f0 = pmap((float)s[0], 36.0f, 1.0f) * semis((float)note);
        SU.kick.ac = decay_coef(pmap(drifted(t, 0, s[1]), 0.04f, 3.2f));
        SU.kick.pd = (float)s[2] * (40.0f / 127.0f);
        SU.kick.pc = decay_coef(pmap((float)s[4], 0.004f, 3.5f));
        SU.kick.penv = 1.0f;
        SU.kick.drive = g;
        SU.kick.norm = 1.0f / clip1(g);
        SU.kick.amp = 1.0f;
        SU.kick.ph = 0.0f;
        SU.kick.click = 70;
        SU.kick.click_g = (float)s[5] * (0.5f / 127.0f);
        SU.kick.hold = (int32_t)s[6] * 30;           /* up to 86 ms at full level before it falls */
        SU.kick.body = (float)s[7] * (0.6f / 127.0f);   /* the second harmonic: a fuller, boxier kick */
        SU.kick.vel = vel;
        break;
    }
    case ROMI_SUB:
        acid_trig(&SU.basso, t, s, note_hz(root + (float)note), vel, acc, slide, 1);
        break;
    case ROMI_HAT: {                    /* DECAY TONE METAL OPEN | CHIP SHAKE SPREAD CUT */
        float open = acc ? 1.0f + (float)s[3] * (7.0f / 127.0f) : 1.0f;
        SU.hat.f = pmap((float)s[1], 3000.0f, 1.6f) * fexp2((float)note * (1.0f / 24.0f));
        SU.hat.ac = decay_coef(pmap(drifted(t, 0, s[0]), 0.006f, 4.0f) * open);
        SU.hat.metal = drifted(t, 1, s[2]) * (1.0f / 127.0f);
        SU.hat.chip = (float)s[4] * (1.0f / 127.0f);
        SU.hat.atc = s[5] ? 1.0f - decay_coef(pmap((float)s[5], 0.0005f, 6.0f)) : 1.0f;
        SU.hat.att = s[5] ? 0.0f : 1.0f;
        SU.hat.pan = 0.5f + brand(&R.rng) * (float)s[6] * (0.5f / 127.0f);   /* SPREAD: each hit somewhere else */
        SU.hat.cut = 0.2f + (float)s[7] * (0.6f / 127.0f);   /* CUT: the high-pass, higher is thinner */
        SU.hat.amp = 1.0f;
        SU.hat.vel = vel;
        break;
    }
    case ROMI_PERC:
        acid_trig(&SU.happo, t, s, note_hz(root + 12.0f + (float)note), vel, acc, slide, 0);
        break;
    case ROMI_STAB: {                   /* WAVE DECAY ARP VIBRATO | SPEED PWM BEND DETUNE */
        int a = s[2] * 7 / 128;
        float hz = note_hz(root + 36.0f + (float)note), rate = pmap((float)s[4], 8.0f, 3.0f);
        SU.piip.ft = hz;
        SU.piip.wave = (uint8_t)(s[0] * 6 / 128);
        SU.piip.ac = decay_coef(pmap(drifted(t, 0, s[1]), 0.02f, 5.5f));
        SU.piip.arp_n = PIIP_ARP_N[a];
        for (i = 0; i < 3; i++)
            SU.piip.mul[i] = semis((float)PIIP_ARP[a][i]);
        SU.piip.arp_len = (int32_t)((float)ROMI_SR / rate);
        SU.piip.vinc = rate * (0.25f * INV_SR);
        SU.piip.vdep = drifted(t, 1, s[3]) * (0.06f / 127.0f);
        SU.piip.pwm = (float)s[5] * (0.4f / 127.0f);
        SU.piip.det = (float)s[7] * (0.02f / 127.0f);
        SU.piip.vel = vel * (acc ? 1.0f : 0.8f);
        if (slide && SU.piip.amp > 0.02f) {        /* a slide: portamento, the note goes on */
            SU.piip.gc = tr->glide ? 1.0f - decay_coef(pmap((float)tr->glide, 0.002f, 6.0f)) : 0.0012f;
            SU.piip.amp = SU.piip.amp * 0.5f + 0.5f;
            break;
        }
        SU.piip.bend = ((float)s[6] - 64.0f) * (1.0f / 64.0f);   /* from below (-) or above (+), up to an octave */
        SU.piip.bend = SU.piip.bend >= 0.0f ? SU.piip.bend : SU.piip.bend * 0.5f;
        SU.piip.benv = 1.0f;
        SU.piip.bc = decay_coef(0.03f);
        if (tr->glide && SU.piip.amp > 0.05f) {    /* GLIDE: a note over the last one glides there */
            SU.piip.gc = 1.0f - decay_coef(pmap((float)tr->glide, 0.002f, 6.0f));
        } else {
            SU.piip.f = hz;
            SU.piip.gc = 1.0f;
        }
        SU.piip.arp_i = SU.piip.arp_cnt = 0;
        if (SU.piip.amp < 0.05f)
            SU.piip.att = 0.0f;
        SU.piip.amp = 1.0f;
        break;
    }
    default:                            /* (KLIKKI: ro:MINImal's click, in trig) */
        break;
    }
}

/* how loud a voice sounds now, 0..1 (the ENV follower) */
static float su_env(int t)
{
    switch (t) {
    case ROMI_KICK: return SU.kick.amp * SU.kick.vel;
    case ROMI_SUB: return SU.basso.amp * SU.basso.vel;
    case ROMI_HAT: return SU.hat.amp * SU.hat.vel;
    case ROMI_PERC: return SU.happo.amp * SU.happo.vel;
    default: return SU.piip.amp * SU.piip.vel;
    }
}

/* the six voices, a sample */
static inline void su_voices(float *v)
{
    float x;
    /* POTKU: a sine falling fast from far above, a click, a soft clipper */
    x = 0.0f;
    if (SU.kick.amp > 1e-4f) {
        SU.kick.ph += SU.kick.f0 * (1.0f + SU.kick.pd * SU.kick.penv) * INV_SR;
        if (SU.kick.ph >= 1.0f)
            SU.kick.ph -= 1.0f;
        x = fsin(SU.kick.ph);
        if (SU.kick.body > 0.0f)
            x += fsin(SU.kick.ph * 2.0f) * SU.kick.body;
        if (SU.kick.click > 0) {
            x += brand(&R.rng) * SU.kick.click_g * (float)SU.kick.click * (1.0f / 70.0f);
            SU.kick.click--;
        }
        x = clip1(x * SU.kick.amp * SU.kick.drive) * SU.kick.norm * SU.kick.vel;
        SU.kick.penv *= SU.kick.pc;
        if (SU.kick.hold > 0)
            SU.kick.hold--;
        else
            SU.kick.amp *= SU.kick.ac;
    }
    v[ROMI_KICK] = x;

    v[ROMI_SUB] = acid_run(&SU.basso);
    v[ROMI_PERC] = acid_run(&SU.happo) * 0.8f;

    /* HATTU: two inharmonic FM pairs against noise, or a sound chip's shift register, high-passed */
    x = 0.0f;
    if (SU.hat.amp > 1e-4f) {
        float f = SU.hat.f * INV_SR, m;
        SU.hat.ph += f;
        SU.hat.mph += f * 1.4471f;
        SU.hat.ph2 += f * 1.6170f;
        SU.hat.mph2 += f * 2.3890f;
        if (SU.hat.ph >= 1.0f) SU.hat.ph -= 1.0f;
        if (SU.hat.mph >= 1.0f) SU.hat.mph -= 1.0f;
        if (SU.hat.ph2 >= 1.0f) SU.hat.ph2 -= 1.0f;
        if (SU.hat.mph2 >= 1.0f) SU.hat.mph2 -= 1.0f;
        m = (fsin(SU.hat.ph + fsin(SU.hat.mph) * 0.9f) + fsin(SU.hat.ph2 + fsin(SU.hat.mph2) * 0.7f)) * 0.5f;
        m = m * SU.hat.metal + brand(&R.rng) * (1.0f - SU.hat.metal);
        if (SU.hat.chip > 0.0f) {
            SU.hat.cph += f * 3.0f;
            if (SU.hat.cph >= 1.0f) {
                uint32_t b = (SU.hat.lfsr ^ SU.hat.lfsr >> 1) & 1u;
                SU.hat.cph -= (float)(int)SU.hat.cph;
                SU.hat.lfsr = SU.hat.lfsr >> 1 | b << 14;
                SU.hat.nz = SU.hat.lfsr & 1u ? 0.8f : -0.8f;
            }
            m += (SU.hat.nz - m) * SU.hat.chip;
        }
        SU.hat.lp += (m - SU.hat.lp) * SU.hat.cut;
        x = (m - SU.hat.lp) * SU.hat.amp * SU.hat.att * SU.hat.vel * 1.6f;
        SU.hat.att += (1.0f - SU.hat.att) * SU.hat.atc;
        SU.hat.amp *= SU.hat.ac;
    }
    v[ROMI_HAT] = x;

    /* PIIP: the waves of a sound chip, naive on purpose: pulses of three widths, a 4-bit triangle, a saw,
     * pitched noise; its chord a note a frame, vibrato, a pitch bend at the start */
    x = 0.0f;
    if (SU.piip.amp > 1e-4f) {
        float f, duty, lfo;
        SU.piip.f += (SU.piip.ft - SU.piip.f) * SU.piip.gc;
        if (SU.piip.arp_n > 1 && ++SU.piip.arp_cnt >= SU.piip.arp_len) {
            SU.piip.arp_cnt = 0;
            SU.piip.arp_i = (SU.piip.arp_i + 1) % SU.piip.arp_n;
        }
        SU.piip.vph += SU.piip.vinc;
        if (SU.piip.vph >= 1.0f)
            SU.piip.vph -= 1.0f;
        lfo = fsin(SU.piip.vph);
        f = SU.piip.f * SU.piip.mul[SU.piip.arp_i] * (1.0f + SU.piip.vdep * lfo) * (1.0f + SU.piip.bend * SU.piip.benv) * INV_SR;
        SU.piip.benv *= SU.piip.bc;
        SU.piip.ph += f;
        if (SU.piip.ph >= 1.0f)
            SU.piip.ph -= 1.0f;
        SU.piip.ph2 += f * (1.0f + SU.piip.det);
        if (SU.piip.ph2 >= 1.0f)
            SU.piip.ph2 -= 1.0f;
        duty = SU.piip.wave == 0 ? 0.125f : SU.piip.wave == 1 ? 0.25f : 0.5f;
        duty += SU.piip.pwm * lfo * duty;
        switch (SU.piip.wave) {
        case 3: {
            float tr = SU.piip.ph < 0.5f ? 4.0f * SU.piip.ph : 4.0f - 4.0f * SU.piip.ph;   /* 0..2 */
            x = (float)(int)(tr * 7.99f) * (1.0f / 7.5f) - 1.0f;
            break;
        }
        case 4:
            x = 2.0f * SU.piip.ph - 1.0f;
            if (SU.piip.det > 0.0f)
                x = (x + 2.0f * SU.piip.ph2 - 1.0f) * 0.5f;
            x *= 0.8f;
            break;
        case 5:
            SU.piip.nph += f * 12.0f;
            if (SU.piip.nph >= 1.0f) {
                uint32_t b = (SU.piip.lfsr ^ SU.piip.lfsr >> 6) & 1u;   /* the short sequence: it has a pitch */
                SU.piip.nph -= (float)(int)SU.piip.nph;
                SU.piip.lfsr = SU.piip.lfsr >> 1 | b << 14;
                SU.piip.nz = SU.piip.lfsr & 1u ? 0.8f : -0.8f;
            }
            x = SU.piip.nz;
            break;
        default:
            x = SU.piip.ph < duty ? 0.7f : -0.7f;
            if (SU.piip.det > 0.0f)
                x = (x + (SU.piip.ph2 < duty ? 0.7f : -0.7f)) * 0.5f;
            break;
        }
        x *= SU.piip.amp * SU.piip.att * SU.piip.vel * 0.9f;
        SU.piip.att += (1.0f - SU.piip.att) * 0.05f;
        SU.piip.amp *= SU.piip.ac;
    }
    v[ROMI_STAB] = x;
}
