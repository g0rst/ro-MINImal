/* SPDX-License-Identifier: MIT
 * ro:MINImal, style FRE3tek (HOME held 2 s): free tekno, acid, mental, tribe. Included by romi.c after suomi_gen.inc
 * (ROMI_SUOMI 1: it plays suom1saundi's kick, acid and hat, and ro:MINImal's percussion as its toms).
 *
 *   track   0 KICK   the bass is the kick: distorted, a long tonal tail, four on the floor, tuned to the key
 *           1 ACID   a 303 line of rolling sixteenths, accents on a three-step cycle against the four, slides
 *           2 HAT    open hats on the off-beat, a sixteenth ride under them at a chance
 *           3 TRIBE  FM toms, polyrhythmic (five or seven in twelve or sixteen), root, fifth and octave
 *           4 SCREAM  PIIP as a saw with vibrato: the mental screams        5 SIREN  NOISE: risers and falls
 * 180 BPM, F phrygian. B, C, D as ever: C rolls the toms up to the bar instead of the hats alone. One chord over all of
 * it (the drone of the kick and the acid): the scream's melody keeps to its tones. The sum through a compressor (romi.c). */

static void tek_gen(romi_track_t *tr, int t, uint32_t d)
{
    uint32_t i;
    switch (t) {
    case ROMI_KICK: {
        int key = kick_in_key(tr, 0);
        for (i = 0; i < 16; i += 4)
            set_step(tr, i, i == 0, 0, key);
        if (urand(4) == 0)
            set_step(tr, 14, 0, 2, key);        /* the tekno double before the bar, half the time */
        break;
    }
    case ROMI_SUB: {                            /* ACID: sixteenths that roll, a few rests, the accent every third */
        /* the root most, its octave, the fifth, the minor seventh below and the minor third; the flat second (the
         * phrygian sting) seldom: a line that stays on the kick's drone */
        static const int8_t DEG[12] = {0, 0, 0, 0, 0, 7, 7, 4, -1, 2, 0, 1};
        uint32_t rests = 2u + urand(3u - (d > 2 ? 2 : d)), cyc = 3u + urand(2);
        tr->len = urand(3) == 0 ? 12 : 16;
        for (i = 0; i < tr->len; i++) {
            int deg = (i & 3u) == 0u ? 0 : DEG[urand(12)];
            set_step(tr, i, i % cyc == 0u, (i & 1u) && urand(5) == 0 ? 1 : 0, scale_note(deg));
            if (i && urand(5) == 0)
                tr->slide |= (uint16_t)(1u << i);
        }
        for (i = 0; i < rests; i++)
            tr->step[1u + urand(tr->len - 1u)].flags = 0;
        break;
    }
    case ROMI_HAT:
        for (i = 0; i < 16; i++) {
            if ((i & 3u) == 2u)
                set_step(tr, i, 1, 0, 0);       /* open on the off-beat */
            else if ((i & 3u) != 0u && urand(3u - (d > 2 ? 2 : d)) == 0)
                set_step(tr, i, 0, 2 + (int)urand(2), 0);   /* the ride under it, at 50 or 25 % */
        }
        break;
    case ROMI_PERC: {                           /* TRIBE: toms against the four */
        static const uint8_t LEN[4] = {12, 12, 16, 6};
        static const int8_t TOM[4] = {7, 4, 0, -3};     /* octave, fifth, root, below: falling like toms */
        uint32_t hits;
        tr->len = LEN[urand(4)];
        hits = tr->len == 6 ? 3u + urand(2) : tr->len == 12 ? 5u + urand(2) * 2u : 7u;
        euclid(tr, hits, urand(tr->len));
        {
            uint32_t n = 0;
            for (i = 0; i < tr->len; i++)
                if (tr->step[i].flags & ROMI_ST_ON) {
                    set_step(tr, i, n == 0, n && urand(4) == 0 ? 1 : 0, scale_note(TOM[n % 4u]));
                    n++;
                }
        }
        tr->p[0] = near(44, 10);                /* decay */
        tr->p[1] = near(14, 8);                 /* fm: little, a skin */
        tr->p[2] = (uint8_t)(urand(2) * 16u + 4u);   /* ratio: the tom's */
        tr->p[3] = near(60, 12);                /* bend: the drop of a tom */
        break;
    }
    default:
        break;
    }
}

/* FRE3tek's sound at the start: the kick long and driven, the acid squelching, the toms */
static void tek_defaults(romi_pattern_t *p)
{
    static const uint8_t DEF[4][9] = {
        /* p0   p1   p2   p3 level pan  dly  rev  q1 */
        {  44,  84,  28,  70, 100,  64,   0,   0,  60},   /* KICK: TUNE DECAY (the tail) SWEEP DRIVE (q1 CLICK) */
        {  60,  80,  64,  48,  90,  64,  34,   8,  30},   /* ACID: CUTOFF RESO ENVMOD DECAY (q1 WAVE): the mids */
        {  28,  66,  58,  44,  54,  76,   8,  14,   0},   /* HAT: DECAY TONE METAL OPEN (q1 CHIP): less fizz */
        {  44,  14,   8,  60,  70,  40,  16,  30,  64},   /* TRIBE: DECAY FM RATIO BEND (q1 B.TIME) */
    };
    static const uint8_t SC[4] = {0, 100, 60, 60};
    int t, i;
    for (t = 0; t < 4; t++) {
        romi_track_t *tr = &p->tr[t];
        for (i = 0; i < 4; i++)
            tr->p[i] = DEF[t][i];
        tr->level = DEF[t][4];
        tr->pan = DEF[t][5];
        tr->dly = DEF[t][6];
        tr->rev = DEF[t][7];
        tr->q[0] = 24;
        tr->q[1] = DEF[t][8];
        tr->q[2] = t == ROMI_KICK ? 50 : 0;     /* KICK: SNAP */
        tr->q[3] = 0;
        tr->glide = t == ROMI_SUB ? 40 : 0;
        tr->follow = 0;
        tr->sc = SC[t];
    }
}

/* tracks 5 and 6: the screech (PIIP, a saw with vibrato) and the siren (NOISE, a riser) */
static void tek_engines(romi_pattern_t *p)
{
    romi_track_t *s = &p->tr[ROMI_STAB], *n = &p->tr[ROMI_CLICK];
    s->p[0] = 86;                               /* WAVE: SAW */
    s->p[1] = 60;
    s->p[2] = 0;                                /* no arpeggio */
    s->p[3] = 34;                               /* VIBRATO: the scream, still in tune */
    s->level = 54;                              /* the scream plays (the mids), the siren comes in by hand (SEL) */
    s->dly = 60;
    s->rev = 50;
    n->p[0] = NLEN_V(5);                        /* a bar */
    n->p[1] = 110;                              /* rising */
    n->p[2] = 60;
    n->p[3] = 70;
    n->q[1] = 127;                              /* swelling to the end */
    n->level = 62;
    n->mute = 1;
}
