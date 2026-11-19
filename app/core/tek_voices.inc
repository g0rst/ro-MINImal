/* SPDX-License-Identifier: MIT
 * ro:MINImal, style FRE3tek: the voices of memetek (github.com/g0rst/memetek-fm1, by the same hands, used here by its
 * author's leave) on tracks 0..2. Included by suomi_voices.inc (ROMI_SUOMI 1); track 3 (TRIBE) is ro:MINImal's
 * percussion, tracks 5 and 6 their engines.
 *
 *   KICK  memetek's TEK-KICK: a sine whose pitch falls exponentially from far above to the key, held at full level for
 *         a third of its tail, then down 60 dB; a high-passed noise click; a tanh drive, normalised
 *         TUNE DECAY SWEEP (the drop, x1..x12) DRIVE | PITCH CLICK SNAP (the drop's time) CRUSH
 *   ACID  memetek's 8-bit bass: a naive square, pulse, saw, triangle or seven-saw (aliasing on purpose), a TPT
 *         state-variable low-pass whose cutoff an envelope closes, a triangle an octave under it, a tanh
 *         CUTOFF RESO ENVMOD DECAY | PITCH WAVE DRIVE CRUSH; an accent opens it, a slide glides (GLIDE)
 *   HAT   memetek's hats: six detuned squares (the 808's) and noise through a band-pass at 10 kHz and a high-pass at
 *         7.5 kHz; two voices, so an open hat rings under the next closed one until that one chokes it
 *         DECAY TONE METAL OPEN | PITCH CHIP DRIVE CRUSH */

typedef struct { float g, k, a1, a2, a3, ic1, ic2; } tsvf_t;

static void tsvf_set(tsvf_t *f, float hz, float q)
{
    float w;
    if (hz < 20.0f) hz = 20.0f;
    if (hz > 18000.0f) hz = 18000.0f;
    if (q < 0.3f) q = 0.3f;
    w = hz * (0.5f * INV_SR);
    f->g = fsin(w) / fsin(w + 0.25f);   /* tan(pi hz / sr) */
    f->k = 1.0f / q;
    f->a1 = 1.0f / (1.0f + f->g * (f->g + f->k));
    f->a2 = f->g * f->a1;
    f->a3 = f->g * f->a2;
}

static inline float tsvf_run(tsvf_t *f, float x, int mode)   /* 0 low, 1 band, 2 high */
{
    float v3 = x - f->ic2, v1 = f->a1 * f->ic1 + f->a2 * v3, v2 = f->ic2 + f->a2 * f->ic1 + f->a3 * v3;
    f->ic1 = 2.0f * v1 - f->ic1;
    f->ic2 = 2.0f * v2 - f->ic2;
    return mode == 0 ? v2 : mode == 1 ? v1 : x - f->k * v1 - v2;
}

static inline float ttanh(float x)      /* tanh, rational, exact enough to drive with */
{
    float x2;
    if (x > 3.0f) return 1.0f;
    if (x < -3.0f) return -1.0f;
    x2 = x * x;
    return x * (27.0f + x2) / (27.0f + 9.0f * x2);
}

#define TK_NHAT 2
#ifndef TK_BASS_G
#define TK_BASS_G 4.0f                  /* memetek's balance: the bass the body, the hats over it */
#endif
#ifndef TK_HAT_G
#define TK_HAT_G 8.0f
#endif
static const float TK_HATF[6] = {263.0f, 400.0f, 421.0f, 474.0f, 587.0f, 845.0f};
static const float TK_SSD[7] = {-0.110f, -0.063f, -0.020f, 0.0f, 0.020f, 0.062f, 0.107f};

typedef struct { float amp, kd, vel, metal, chip, sh, shc, shr, ph[6], inc[6]; int on; tsvf_t bp, hp; } tk_hat_t;

static struct {
    struct { float ph, f, fend, kf, amp, ka, click, kc, hpx, hpy, k, nk, vel; int32_t hold; } kick;
    struct { float ph[7], phs, f, ft, gc, amp, peak, ka, cut, kc, floorc, cut0, q, vel, k, nk, sub; int32_t att; uint32_t cr;
             int wave, on; tsvf_t lp; } bass;
    tk_hat_t hat[TK_NHAT];
    uint32_t hat_rr;
} TK;

static void tk_panic(void)
{
    int i;
    TK.kick.amp = TK.bass.amp = 0.0f;
    TK.bass.on = 0;
    TK.bass.att = 0;
    for (i = 0; i < TK_NHAT; i++) {
        TK.hat[i].amp = 0.0f;
        TK.hat[i].on = 0;
    }
}

static void tk_trig(int t, int note, float vel, int acc, int slide, const uint8_t *p, const uint8_t *q, float root,
                    uint8_t glide)
{
    switch (t) {
    case ROMI_KICK: {                   /* TUNE DECAY SWEEP DRIVE | CLICK SNAP */
        float tail = pmap((float)p[1], 0.1f, 3.0f), d = (float)p[3] * (1.0f / 127.0f);
        TK.kick.fend = in_tune(pmap((float)p[0], 36.0f, 1.0f)) * fexp2((float)note * (1.0f / 12.0f));
        TK.kick.f = TK.kick.fend * (1.0f + (float)p[2] * (11.0f / 127.0f)) * (acc ? 1.3f : 1.0f);
        TK.kick.kf = decay_coef(pmap((float)q[2], 0.01f, 4.0f) * 0.33f);
        TK.kick.amp = acc ? 1.15f : 1.0f;
        TK.kick.hold = (int32_t)(tail * 0.35f * (float)ROMI_SR);
        TK.kick.ka = decay_coef(tail * 0.65f / 6.9078f);   /* -60 dB in the rest of the tail */
        TK.kick.click = (float)q[1] * (1.0f / 127.0f);
        TK.kick.kc = decay_coef(0.002f);
        TK.kick.k = 1.0f + d * 14.0f;
        TK.kick.nk = 1.0f / ttanh(TK.kick.k);
        TK.kick.ph = 0.0f;
        TK.kick.vel = vel;
        break;
    }
    case ROMI_SUB: {                    /* CUTOFF RESO ENVMOD DECAY | WAVE */
        float hz = note_hz(root + 12.0f + (float)note), ln = pmap(drifted(t, 1, p[3]), 0.02f, 5.0f), fenv, endf, upd;
        int w = q[1] * 5 / 128, k;
        TK.bass.ft = hz;
        if ((glide || slide) && TK.bass.amp > 0.02f)
            TK.bass.gc = 1.0f - decay_coef(glide ? pmap((float)glide, 0.004f, 5.0f) : 0.04f);
        else {
            TK.bass.f = hz;
            TK.bass.gc = 1.0f;
        }
        if (!TK.bass.on || w != TK.bass.wave)
            for (k = 0; k < 7; k++)
                TK.bass.ph[k] = w == 4 ? frand(&R.rng) : 0.0f;   /* a supersaw starts unaligned: no flam */
        TK.bass.wave = w;
        TK.bass.on = 1;
        TK.bass.att = (int32_t)(0.003f * (float)ROMI_SR);
        TK.bass.peak = 0.8f;
        if (!(slide && TK.bass.amp > 0.02f))
            TK.bass.amp = 0.0f;
        TK.bass.ka = decay_coef(ln * 0.95f / 6.9078f);
        fenv = (float)p[2] * (1.0f / 127.0f);
        TK.bass.cut0 = pmap(drifted(t, 0, p[0]), 100.0f, 5.64f) * (acc ? 1.6f : 1.0f);
        TK.bass.q = fexp2((0.5f + (float)p[1] * (19.5f / 127.0f)) * (1.0f / 6.0206f)) * (acc ? 1.3f : 1.0f);
        TK.bass.cut = 1.0f;             /* the envelope, as a factor of CUTOFF: 1 down to 1 - envmod * .92 */
        endf = 1.0f - fenv * 0.92f;
        TK.bass.floorc = endf < 0.02f ? 0.02f : endf;
        upd = ln * 0.8f * (float)ROMI_SR / 16.0f;
        if (upd < 1.0f) upd = 1.0f;
        TK.bass.kc = fexp2(-6.0f / upd); /* (about to the floor in the time: the floor holds it) */
        TK.bass.sub = 0.5f;
        TK.bass.vel = vel * (acc ? 1.25f : 1.0f);
        TK.bass.k = 1.2f;
        TK.bass.nk = 1.0f / ttanh(1.2f);
        TK.bass.cr = 0;
        break;
    }
    case ROMI_HAT: {                    /* DECAY TONE METAL OPEN | PITCH CHIP */
        int open = acc, v, k;
        float tn = fexp2((float)note * (1.0f / 24.0f)), tone = pmap((float)p[1], 0.3f, 2.32f);
        float dec = pmap(drifted(t, 0, p[0]), 0.01f, 3.3f) * (open ? 1.0f + (float)p[3] * (11.0f / 127.0f) : 1.0f);
        tk_hat_t *h;
        if (!open)                      /* a closed hat chokes an open one */
            for (v = 0; v < TK_NHAT; v++)
                if (TK.hat[v].on == 2) {
                    TK.hat[v].kd = decay_coef(0.002f);
                    TK.hat[v].on = 1;
                }
        h = &TK.hat[TK.hat_rr++ % TK_NHAT];
        {
            h->on = open ? 2 : 1;
            h->amp = (open ? 0.7f : 0.9f);
            h->vel = vel;
            h->kd = decay_coef(dec / 6.9078f);
            h->metal = drifted(t, 1, p[2]) * (0.24f / 127.0f);
            h->chip = (float)q[1] * (1.0f / 127.0f);
            for (k = 0; k < 6; k++) {
                h->inc[k] = TK_HATF[k] * 1.6f * tn * INV_SR;
                h->ph[k] = frand(&R.rng);
            }
            tsvf_set(&h->hp, 7500.0f * tn * tone, 1.0f);
            tsvf_set(&h->bp, 10000.0f * tn, 1.0f);
            h->hp.ic1 = h->hp.ic2 = h->bp.ic1 = h->bp.ic2 = 0.0f;
            h->shr = 0.18f * tn * 1.0884f;      /* (memetek's sample and hold, at 44.1 kHz) */
            h->shc = h->sh = 0.0f;
        }
        break;
    }
    default:
        break;
    }
}

static float tk_env(int t)
{
    switch (t) {
    case ROMI_KICK: return TK.kick.amp * TK.kick.vel;
    case ROMI_SUB: return TK.bass.amp * TK.bass.vel * 1.25f;
    default: {
        float e = 0.0f;
        int v;
        for (v = 0; v < TK_NHAT; v++)
            if (TK.hat[v].on && TK.hat[v].amp * TK.hat[v].vel > e)
                e = TK.hat[v].amp * TK.hat[v].vel;
        return e;
    }
    }
}

static inline void tk_voices(float *v)
{
    float x = 0.0f;
    int i, k;
    if (TK.kick.amp > 5e-4f) {          /* KICK */
        TK.kick.f = TK.kick.fend + (TK.kick.f - TK.kick.fend) * TK.kick.kf;
        TK.kick.ph += TK.kick.f * INV_SR;
        if (TK.kick.ph >= 1.0f)
            TK.kick.ph -= 1.0f;
        x = fsin(TK.kick.ph) * TK.kick.amp;
        if (TK.kick.hold > 0)
            TK.kick.hold--;
        else
            TK.kick.amp *= TK.kick.ka;
        if (TK.kick.click > 5e-4f) {
            float n = brand(&R.rng) * TK.kick.click;
            TK.kick.click *= TK.kick.kc;
            TK.kick.hpy = 0.70f * (TK.kick.hpy + n - TK.kick.hpx);
            TK.kick.hpx = n;
            x += TK.kick.hpy;
        }
        x = x > 1.0f ? 1.0f : x < -1.0f ? -1.0f : x;
        x = ttanh(TK.kick.k * x) * TK.kick.nk * TK.kick.vel;
    }
    v[ROMI_KICK] = x;

    x = 0.0f;
    if (TK.bass.on) {                   /* ACID: memetek's 8-bit bass */
        float f, o, s;
        if ((TK.bass.cr++ & 15u) == 0u) {
            float fc = TK.bass.cut0 * TK.bass.cut;
            tsvf_set(&TK.bass.lp, fc < 50.0f ? 50.0f : fc > 12000.0f ? 12000.0f : fc, TK.bass.q);
            TK.bass.cut *= TK.bass.kc;
            if (TK.bass.cut < TK.bass.floorc)
                TK.bass.cut = TK.bass.floorc;
        }
        TK.bass.f += (TK.bass.ft - TK.bass.f) * TK.bass.gc;
        f = TK.bass.f * INV_SR;
        if (TK.bass.wave == 4) {        /* seven saws, detuned */
            o = 0.0f;
            for (k = 0; k < 7; k++) {
                TK.bass.ph[k] += f * (1.0f + TK_SSD[k] * 0.52f);
                if (TK.bass.ph[k] >= 1.0f)
                    TK.bass.ph[k] -= 1.0f;
                o += (2.0f * TK.bass.ph[k] - 1.0f) * (k == 3 ? 1.0f : 0.6f);
            }
            o *= 0.3f;
        } else {
            float p;
            TK.bass.ph[0] += f;
            if (TK.bass.ph[0] >= 1.0f)
                TK.bass.ph[0] -= 1.0f;
            p = TK.bass.ph[0];
            o = TK.bass.wave == 0 ? (p < 0.5f ? 1.0f : -1.0f) : TK.bass.wave == 1 ? (p < 0.25f ? 1.0f : -1.0f)
              : TK.bass.wave == 2 ? 2.0f * p - 1.0f : (p < 0.5f ? 4.0f * p - 1.0f : 3.0f - 4.0f * p);
        }
        TK.bass.phs += f * 0.5f;        /* the triangle an octave under */
        if (TK.bass.phs >= 1.0f)
            TK.bass.phs -= 1.0f;
        s = (TK.bass.phs < 0.5f ? 4.0f * TK.bass.phs - 1.0f : 3.0f - 4.0f * TK.bass.phs) * TK.bass.sub;
        x = tsvf_run(&TK.bass.lp, o, 0) + s;
        if (TK.bass.att > 0) {
            TK.bass.amp += TK.bass.peak / (0.003f * (float)ROMI_SR);
            TK.bass.att--;
        } else {
            TK.bass.amp *= TK.bass.ka;
        }
        x = ttanh(TK.bass.k * x * TK.bass.amp) * TK.bass.nk * TK.bass.vel;
        if (!TK.bass.att && TK.bass.amp < 5e-4f) {
            TK.bass.on = 0;
            TK.bass.amp = 0.0f;
        }
    }
    v[ROMI_SUB] = x * TK_BASS_G;

    x = 0.0f;
    for (i = 0; i < TK_NHAT; i++) {     /* HAT: six squares and noise, band-passed, high-passed */
        float m = 0.0f, y;
        if (!TK.hat[i].on)
            continue;
        for (k = 0; k < 6; k++) {
            TK.hat[i].ph[k] += TK.hat[i].inc[k];
            if (TK.hat[i].ph[k] >= 1.0f)
                TK.hat[i].ph[k] -= 1.0f;
            m += TK.hat[i].ph[k] < 0.5f ? 1.0f : -1.0f;
        }
        y = m * TK.hat[i].metal + brand(&R.rng) * 0.5f;
        if (TK.hat[i].chip > 0.0f) {    /* CHIP: memetek's sample-and-hold hat into it */
            TK.hat[i].shc += TK.hat[i].shr;
            if (TK.hat[i].shc >= 1.0f) {
                TK.hat[i].shc -= 1.0f;
                TK.hat[i].sh = brand(&R.rng);
            }
            y += (TK.hat[i].sh - y) * TK.hat[i].chip;
        }
        y = tsvf_run(&TK.hat[i].bp, y, 1);
        y = tsvf_run(&TK.hat[i].hp, y, 2);
        x += y * TK.hat[i].amp * TK.hat[i].vel;
        TK.hat[i].amp *= TK.hat[i].kd;
        if (TK.hat[i].amp < 5e-4f)
            TK.hat[i].on = 0;
    }
    v[ROMI_HAT] = x * TK_HAT_G;
}
