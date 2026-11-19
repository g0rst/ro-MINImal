/* SPDX-License-Identifier: MIT
 * NOISE (SUHINA in suom1saundi), an engine of tracks 5 and 6 in either style: hiss, risers and downlifters. White
 * noise through a resonant state-variable filter whose cutoff sweeps over the note's LENGTH (a sixteenth to eight
 * bars), up (a riser) or down (a downlifter); its level swells to the end, falls from the start, or rises and falls.
 * LENGTH all the way left is CLAP: three bursts of noise 9 ms apart and a tail, through the filter as a band-pass
 * (TONE its centre, about 1.3 kHz from the generator; RESO how narrow; SWEEP the tail, 60 to 500 ms).
 *   SOUND   LENGTH SWEEP TONE RESO        SOUND 2  PITCH SWELL DRIVE CRUSH
 * About 20 instructions a sample. Included by romi.c ahead of trig(). */
typedef struct {
    float amp, cut, k16, f, q, low, band, vel, peak, sw, nf, tail, dc;
    uint32_t pos, len, ctl, clap;
} noise_v;
static noise_v NZ[2];
static const uint8_t NOISE_LEN[9] = {0, 1, 2, 4, 8, 16, 32, 64, 128};   /* steps (0: CLAP): a sixteenth .. eight bars */
#define NLEN_V(i) ((uint8_t)((i) * 128 / 9 + 1))   /* LENGTH's knob value for position i (0 CLAP .. 8 eight bars) */
#define CLAP_BURST 397u                 /* 9 ms */

static void noise_trig(int s, int note, float vel, const uint8_t *p, const uint8_t *q, float step)
{
    noise_v *N = &NZ[s];
    float sweep = ((float)p[1] - 64.0f) * (1.0f / 64.0f);   /* up to six octaves up or down */
    N->clap = p[0] * 9 / 128 == 0;
    N->len = (uint32_t)(step * (float)NOISE_LEN[p[0] * 9 / 128]);
    if (N->len < 64u)
        N->len = 64u;
    N->nf = fexp2((float)note * (1.0f / 12.0f));
    N->cut = pmap((float)p[2], 60.0f, 8.0f) * N->nf;
    N->sw = 1.0f;                       /* the sweep so far */
    N->k16 = fexp2(sweep * 6.0f * 16.0f / (float)N->len);   /* the cutoff's step every 16 samples */
    N->q = 1.0f - (float)p[3] * (0.93f / 127.0f);
    N->peak = (float)q[1] * (1.0f / 127.0f);             /* SWELL: 0 falls from the start, 1 swells to the end */
    N->pos = 0;
    N->ctl = 0;
    N->amp = 1.0f;
    N->vel = vel;
    if (N->clap) {                      /* the clap: three bursts and a tail; no sweep */
        N->k16 = 1.0f;
        N->tail = 0.8f;
        N->dc = decay_coef(pmap((float)p[1], 0.06f, 3.0f));   /* the tail: 60 to 500 ms */
        N->len = 3u * CLAP_BURST + (uint32_t)(pmap((float)p[1], 0.06f, 3.0f) * 3.0f * (float)ROMI_SR);
    }
}

/* the knobs while a sweep runs (each block): TONE, SWEEP, RESO and SWELL are heard at once, not from the next
 * note on (a riser can be bars long); LENGTH counts from the next */
static void noise_live(int s, const uint8_t *p, const uint8_t *q)
{
    noise_v *N = &NZ[s];
    float sweep = ((float)p[1] - 64.0f) * (1.0f / 64.0f);
    N->cut = pmap((float)p[2], 60.0f, 8.0f) * N->nf;
    N->q = 1.0f - (float)p[3] * (0.93f / 127.0f);
    if (N->clap) {
        N->dc = decay_coef(pmap((float)p[1], 0.06f, 3.0f));
        return;
    }
    N->k16 = fexp2(sweep * 6.0f * 16.0f / (float)N->len);
    N->q = 1.0f - (float)p[3] * (0.93f / 127.0f);
    N->peak = (float)q[1] * (1.0f / 127.0f);
}

static inline float noise_run(int s)
{
    noise_v *N = &NZ[s];
    float t, e, hp;
    if (N->amp <= 0.0f) {
        N->low = N->band = 0.0f;
        return 0.0f;
    }
    if ((N->ctl++ & 15u) == 0u) {
        float fc = N->cut * N->sw;
        fc = fc > 16000.0f ? 16000.0f : fc < 30.0f ? 30.0f : fc;
        N->f = 2.0f * fsin(fc * 0.5f * INV_SR);
        if (N->f > 0.95f)
            N->f = 0.95f;
        N->sw *= N->k16;
    }
    if (N->clap) {                      /* three bursts, each falling fast, then the tail */
        if (N->pos < 3u * CLAP_BURST) {
            float u = 1.0f - (float)(N->pos % CLAP_BURST) * (1.0f / (float)CLAP_BURST);
            e = u * u * u;
        } else {
            e = N->tail;
            N->tail *= N->dc;
        }
        N->low += N->f * N->band;
        hp = brand(&R.rng) - N->low - N->q * N->band;
        N->band += N->f * hp;
        if (++N->pos >= N->len || (N->pos > 3u * CLAP_BURST && N->tail < 1e-4f))
            N->amp = 0.0f;
        return N->band * e * N->vel * 1.6f;
    }
    t = (float)N->pos / (float)N->len;
    e = N->peak <= 0.0f ? 1.0f - t : N->peak >= 1.0f ? t
      : t < N->peak ? t / N->peak : (1.0f - t) / (1.0f - N->peak);   /* up to the peak, down after it */
    e *= e;
    N->low += N->f * N->band;
    hp = brand(&R.rng) - N->low - N->q * N->band;
    N->band += N->f * hp;
    if (++N->pos >= N->len)
        N->amp = 0.0f;
    return (N->band + 0.5f * hp) * e * N->vel * 0.7f;
}
