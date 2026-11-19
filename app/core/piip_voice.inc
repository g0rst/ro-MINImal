/* SPDX-License-Identifier: MIT
 * PIIP, suom1saundi's sound chip voice, as an engine of tracks 5 and 6 in either style (GROOVE 2: HOME twice): pulses
 * of three widths, a 4-bit triangle, a saw, pitched noise; its chord a note a frame, vibrato, a pitch bend at the
 * start. Two of it, one a track. Included by romi.c ahead of trig() (always: it is not part of ROMI_SUOMI).
 *   SOUND   WAVE DECAY ARP VIBRATO      SOUND 2  PITCH SPEED DRIVE CRUSH   (PWM 30, BEND none, DETUNE 0 fixed)
 * GLIDE (TIMING) and SLIDE steps as the stab's. */
typedef struct {
    float ph, ph2, nph, f, ft, gc, amp, ac, att, vph, vinc, vdep, pwm, bend, benv, bc, det, vel, nz, mul[3];
    int32_t arp_n, arp_i, arp_cnt, arp_len;
    uint32_t lfsr;
    uint8_t wave;
} piip_v;
static piip_v PI[2];

/* PIIP's arpeggios, a note a frame as on a sound chip: none, octave, minor, major, sus4, fifth and octave, diminished */
static const int8_t PIIP_ARP[7][3] = {{0, 0, 0}, {0, 12, 0}, {0, 3, 7}, {0, 4, 7}, {0, 5, 7}, {0, 7, 12}, {0, 3, 6}};
static const uint8_t PIIP_ARP_N[7] = {1, 2, 3, 3, 3, 3, 3};
static float semis(float n) { return fexp2(n * (1.0f / 12.0f)); }

static void piip_trig(int s, int t, int note, float vel, int acc, int slide, const uint8_t *sp, const uint8_t *q,
                      float root)
{
    const romi_track_t *tr = &PAT->tr[t];
    piip_v *P = &PI[s];
    uint8_t s8[8] = {sp[0], sp[1], sp[2], sp[3], q[1], 30, 64, 0};   /* + SPEED (SOUND 2), PWM, BEND, DETUNE */
    int i;
    if (!P->lfsr)
        P->lfsr = 0x4321u + (uint32_t)s;
    int a = s8[2] * 7 / 128;
    float hz = note_hz(root + 36.0f + (float)note), rate = pmap((float)s8[4], 8.0f, 3.0f);
    P->ft = hz;
    P->wave = (uint8_t)(s8[0] * 6 / 128);
    P->ac = decay_coef(pmap(drifted(t, 0, s8[1]), 0.02f, 5.5f));
    P->arp_n = PIIP_ARP_N[a];
    for (i = 0; i < 3; i++)
        P->mul[i] = semis((float)PIIP_ARP[a][i]);
    P->arp_len = (int32_t)((float)ROMI_SR / rate);
    P->vinc = rate * (0.25f * INV_SR);
    P->vdep = drifted(t, 1, s8[3]) * (0.06f / 127.0f);
    P->pwm = (float)s8[5] * (0.4f / 127.0f);
    P->det = (float)s8[7] * (0.02f / 127.0f);
    P->vel = vel * (acc ? 1.0f : 0.8f);
    if (slide && P->amp > 0.02f) {        /* a slide: portamento, the note goes on */
        P->gc = tr->glide ? 1.0f - decay_coef(pmap((float)tr->glide, 0.002f, 6.0f)) : 0.0012f;
        P->amp = P->amp * 0.5f + 0.5f;
        return;
    }
    P->bend = ((float)s8[6] - 64.0f) * (1.0f / 64.0f);   /* from below (-) or above (+), up to an octave */
    P->bend = P->bend >= 0.0f ? P->bend : P->bend * 0.5f;
    P->benv = 1.0f;
    P->bc = decay_coef(0.03f);
    if (tr->glide && P->amp > 0.05f) {    /* GLIDE: a note over the last one glides there */
        P->gc = 1.0f - decay_coef(pmap((float)tr->glide, 0.002f, 6.0f));
    } else {
        P->f = hz;
        P->gc = 1.0f;
    }
    P->arp_i = P->arp_cnt = 0;
    if (P->amp < 0.05f)
        P->att = 0.0f;
    P->amp = 1.0f;
}

static inline float piip_run(int s)
{
    piip_v *P = &PI[s];
    float x = 0.0f;
    /* PIIP: the waves of a sound chip, naive on purpose: pulses of three widths, a 4-bit triangle, a saw,
     * pitched noise; its chord a note a frame, vibrato, a pitch bend at the start */
    if (P->amp > 1e-4f) {
        float f, duty, lfo;
        P->f += (P->ft - P->f) * P->gc;
        if (P->arp_n > 1 && ++P->arp_cnt >= P->arp_len) {
            P->arp_cnt = 0;
            P->arp_i = (P->arp_i + 1) % P->arp_n;
        }
        P->vph += P->vinc;
        if (P->vph >= 1.0f)
            P->vph -= 1.0f;
        lfo = fsin(P->vph);
        f = P->f * P->mul[P->arp_i] * (1.0f + P->vdep * lfo) * (1.0f + P->bend * P->benv) * INV_SR;
        P->benv *= P->bc;
        P->ph += f;
        if (P->ph >= 1.0f)
            P->ph -= 1.0f;
        P->ph2 += f * (1.0f + P->det);
        if (P->ph2 >= 1.0f)
            P->ph2 -= 1.0f;
        duty = P->wave == 0 ? 0.125f : P->wave == 1 ? 0.25f : 0.5f;
        duty += P->pwm * lfo * duty;
        switch (P->wave) {
        case 3: {
            float tr = P->ph < 0.5f ? 4.0f * P->ph : 4.0f - 4.0f * P->ph;   /* 0..2 */
            x = (float)(int)(tr * 7.99f) * (1.0f / 7.5f) - 1.0f;
            break;
        }
        case 4:
            x = 2.0f * P->ph - 1.0f;
            if (P->det > 0.0f)
                x = (x + 2.0f * P->ph2 - 1.0f) * 0.5f;
            x *= 0.8f;
            break;
        case 5:
            P->nph += f * 12.0f;
            if (P->nph >= 1.0f) {
                uint32_t b = (P->lfsr ^ P->lfsr >> 6) & 1u;   /* the short sequence: it has a pitch */
                P->nph -= (float)(int)P->nph;
                P->lfsr = P->lfsr >> 1 | b << 14;
                P->nz = P->lfsr & 1u ? 0.8f : -0.8f;
            }
            x = P->nz;
            break;
        default:
            x = P->ph < duty ? 0.7f : -0.7f;
            if (P->det > 0.0f)
                x = (x + (P->ph2 < duty ? 0.7f : -0.7f)) * 0.5f;
            break;
        }
        x *= P->amp * P->att * P->vel * 0.9f;
        P->att += (1.0f - P->att) * 0.05f;
        P->amp *= P->ac;
    }
    return x;
}
