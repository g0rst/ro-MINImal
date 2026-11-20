/* SPDX-License-Identifier: MIT
 * ro:MINImal, style psydub (HOME held 2 s in suom1saundi): psytrance and dub. Included by romi.c after sch_gen.inc
 * (ROMI_SUOMI 1: it plays suom1saundi's kick, bass, hat and acid voices; the rest is its own rules).
 *
 * What the forums and the guides agree on, and what is built from it: about 138 BPM, minor keys (D, A, C), the
 * minor pentatonic as the bass's and the melody's scale with the phrygian flat second kept as the dark colour; a bass
 * that keeps to the root and leaves air (a dub bass is slow, long, sub-heavy); the chords small minor triads, stabbed
 * on the off-beat and left to the echo (the delay is the instrument: two or three sends, the time a dotted eighth, the
 * feedback long and darkened) and a spring-like reverb; the kick four on the floor and the rest sparse.
 *
 *   track   0 KICK    POTKU: four on the floor, the gap before the bar now and then
 *           1 DUB     BASSO: a long root on the off-beats, a pentatonic step now and then, sliding
 *           2 HAT     HATTU: the off-beat open, a few closed ones between, very sparse
 *           3 BUBBLE  HAPPO: a pentatonic phrase on a loop of its own (12, 14, 15 or 16 steps) that bubbles through the delay
 *           4 CHORD   STAB: minor triads on the off-beat (the engine's rules)       5 PING  PIIP: a bell through the echo
 * 138 BPM, D phrygian (the bass and the bubble keep to the pentatonic's degrees). */

static void psy_gen(romi_track_t *tr, int t, uint32_t d)
{
    uint32_t i;
    switch (t) {
    case ROMI_KICK: {
        int key = kick_in_key(tr, 0);
        for (i = 0; i < 16; i += 4)
            set_step(tr, i, i == 0, 0, key);
        if (urand(4) == 0)
            set_step(tr, 14, 0, 2, key);        /* a ghost before the bar, one time in four */
        break;
    }
    case ROMI_SUB: {                            /* DUB: 0 rest, 1 the root, 2 the minor third, 3 the fourth, 4 the fifth,
                                                 * 5 the flat seventh, 6 the octave: the pentatonic's degrees */
        static const uint8_t LINE[5][16] = {
            {0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0},   /* the off-beats, the root */
            {0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 4, 0},   /* the fifth answers at the end */
            {0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 5, 0},   /* the third beat leaning, a flat seventh */
            {0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 6},   /* a dotted pair, the octave at the bar */
            {0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 3, 0, 1, 0},   /* the fourth turns it */
        };
        static const uint8_t PICK[10] = {0, 0, 0, 1, 1, 1, 2, 3, 3, 4};
        static const int8_t DEG[7] = {0, 0, 2, 3, 4, 6, 7};
        const uint8_t *ln = LINE[d < 1 ? 0 : PICK[urand(10)]];
        int sh = su_bass_shift();
        uint32_t prev = 99;
        tr->len = 16;
        for (i = 0; i < 16; i++) {
            int kind = ln[i];
            if (!kind)
                continue;
            set_step(tr, i, (i & 3u) == 2u && kind == 1, 0, su_motif(DEG[kind]) + sh);
            if (kind != 1 && prev != 99u && urand(2))
                tr->slide |= (uint16_t)(1u << i);   /* the step to a new note slides */
            prev = i;
        }
        tr->p[0] = near(36, 6);                 /* cutoff: low, a sub with a little head */
        tr->p[3] = near(74, 8);                 /* decay: long, a note that sings under the echo */
        break;
    }
    case ROMI_HAT:
        for (i = 2; i < 16; i += 4)
            set_step(tr, i, 1, 0, 0);           /* the off-beat, open (the delay sends it round) */
        for (i = 0; i < 16; i++)
            if (!(tr->step[i].flags & ROMI_ST_ON) && (i & 1u) && urand(100) < 14u + d * 8u)
                set_step(tr, i, 0, 2 + (int)urand(2), 0);   /* a few closed ones, at 50 or 25 % */
        break;
    case ROMI_PERC: {                           /* BUBBLE: a pentatonic phrase, sparse, on its own loop */
        static const uint8_t LEN[4] = {12, 14, 15, 16};
        static const int8_t PEN[6] = {0, 2, 3, 4, 6, 7};   /* the degrees of the minor pentatonic, and the octave */
        uint32_t hits, n = 0, at, k;
        int pos = 0, prev = -99;
        tr->len = LEN[urand(4)];
        hits = 4u + urand(3);
        for (k = 0; k < hits; k++) {
            at = urand(tr->len);
            if (tr->step[at].flags & ROMI_ST_ON)
                continue;
            pos += (int)urand(3) - 1;           /* a walk: a step up, down or none */
            pos = pos < 0 ? 0 : pos > 5 ? 5 : pos;
            set_step(tr, at, n == 0, urand(6) == 0 ? 1 : 0, su_motif(PEN[pos]) + 12);
            n++;
        }
        for (i = 0; i < tr->len; i++)
            if (tr->step[i].flags & ROMI_ST_ON) {
                int nt = tr->step[i].note;
                if (prev > -99 && (nt - prev >= 5 || prev - nt >= 5) && urand(2))
                    tr->slide |= (uint16_t)(1u << i);   /* the big steps glide */
                prev = nt;
            }
        tr->p[0] = near(50, 8);                 /* cutoff: round, the echo brightens it */
        tr->p[2] = near(58, 10);                /* envmod */
        break;
    }
    default:
        break;
    }
}

/* psydub's sound at the start: the kick round, the bass long and low, the hats going into the delay, the bubble
 * in the echo; the bass ducked only a little by the kick (a dub bass breathes, it does not pump) */
static void psy_defaults(romi_pattern_t *p)
{
    static const uint8_t DEF[ROMI_TRACKS][9] = {
        /* p0   p1   p2   p3 level pan  dly  rev  q1 */
        {  48,  64,  58,  26,  92,  64,   0,   6,  44},   /* POTKU: TUNE DECAY SWEEP DRIVE (q1 CLICK) */
        {  36,  30,  44,  74, 112,  64,  16,   8,   0},   /* DUB (BASSO): CUTOFF RESO ENVMOD DECAY (q1 WAVE: saw) */
        {  46,  66,  64,  78,  76,  76,  56,  34,   0},   /* HATTU: DECAY TONE METAL OPEN (q1 CHIP) */
        {  50,  52,  58,  60,  74,  40,  78,  52,  20},   /* BUBBLE (HAPPO): CUTOFF RESO ENVMOD DECAY (q1 WAVE) */
        {  30,  46,  40,  30,  76,  80,  70,  40,  64},   /* (tracks 5 and 6: psy_engines) */
        {  40,  78,  84,  90,  86,  64,  40,  30,   0},
    };
    static const uint8_t GLIDE[ROMI_TRACKS] = {0, 50, 0, 60, 0, 0};
    int t, i;
    for (t = 0; t < ROMI_TRACKS; t++) {
        romi_track_t *tr = &p->tr[t];
        for (i = 0; i < 4; i++)
            tr->p[i] = DEF[t][i];
        tr->level = DEF[t][4];
        tr->pan = DEF[t][5];
        tr->dly = DEF[t][6];
        tr->rev = DEF[t][7];
        tr->q[0] = 24;
        tr->q[1] = DEF[t][8];
        tr->q[2] = t == ROMI_KICK ? 36 : 0;     /* POTKU: SNAP */
        tr->q[3] = 0;
        tr->glide = GLIDE[t];
        tr->follow = 0;
        tr->sc = t == ROMI_KICK ? 0 : t == ROMI_SUB ? 90 : 40;
    }
}

/* tracks 5 and 6: the chord (STAB, small and dark, almost all of it in the delay and the reverb) and the ping
 * (PIIP, a bell-like sine through the echo) */
static void psy_engines(romi_pattern_t *p)
{
    romi_track_t *c = &p->tr[ROMI_STAB], *g = &p->tr[ROMI_CLICK];
    c->p[0] = 38;                               /* DECAY: a stab, the echo is the tail */
    c->p[1] = 52;                               /* BRIGHT: dark */
    c->level = 70;
    c->dly = 110;                               /* the send: the chord is the delay's */
    c->rev = 84;
    g->p[0] = 8;                                /* WAVE: sine */
    g->p[1] = 30;
    g->p[2] = 0;                                /* no arpeggio */
    g->p[3] = 18;                               /* a little vibrato */
    g->level = 58;
    g->dly = 96;
    g->rev = 72;
}
