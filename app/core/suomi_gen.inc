/* SPDX-License-Identifier: MIT
 * ro:MINImal, style SUOMI: the generator. Included by romi.c after its own generator (ROMI_SUOMI 1).
 *
 * What makes a pattern suomisaundi here: the kick on every beat; under it the pumping bass of psytrance, three
 * sixteenths after each kick (the roll) or two (the gallop), on the root, jumping the octave at the end of the bar
 * and ducked hard by the kick; an acid line and a chip melody on loops of their own lengths that walk over the
 * chord; ro:MINImal's clicks on odd lengths (KLIKKI). The rest is ro:MINImal's: B, C and D made from A, the trig
 * conditions, the links. */

/* d degrees above the root, 7 and more an octave up */
static int su_motif(int d)
{
    return scale_note(d);
}
static int su_bass_shift(void)          /* the bass keeps low: a root above F# goes an octave down */
{
    return R.prj.root % 12 > 6 ? -12 : 0;
}

static void su_gen(romi_track_t *tr, int t, uint32_t d)
{
    uint32_t i;
    switch (t) {
    case ROMI_KICK: {
        int key = kick_in_key(tr, 0), k = (int)urand(5);
        for (i = 0; i < 16; i += 4)
            set_step(tr, i, 1, 0, key);
        if (k == 0) {
            set_step(tr, 14, 0, 2, key);        /* a ghost before the bar, half the time */
        } else if (k == 1) {
            tr->step[12].flags |= 1u;           /* a double on the last beat, half the time */
            tr->step[12].chance = 50;
        }
        break;
    }
    case ROMI_SUB: {
        /* the pump: 0 rest (the kick's place), 1 the root, 2 its octave, 3 the fifth, 4 the note below, 5 the third.
         * The roll (kick, bass, bass, bass) is psytrance's own; the gallop (kick, -, bass, bass) is the older one */
        static const uint8_t LINE[6][16] = {
            {0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 2},   /* the roll */
            {0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 2, 1},   /* the roll, the octave a step early */
            {0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 2},   /* the gallop */
            {0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 2, 1, 3},   /* the roll with a turn */
            {0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 2, 1},   /* gallop and roll */
            {0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 2, 2},   /* the short roll */
        };
        static const uint8_t PICK[10] = {0, 0, 0, 1, 1, 2, 2, 3, 4, 5};   /* mostly the roll */
        static const int8_t DEG[6] = {0, 0, 7, 4, -1, 2};
        const uint8_t *ln = LINE[PICK[urand(10)]];
        uint32_t odd = urand(3) == 0 ? 12u + urand(4) : 99u;   /* one note off the root at the end, one line in three */
        int sh = su_bass_shift();
        for (i = 0; i < 16; i++) {
            int kind = ln[i], note;
            if (!kind)
                continue;
            if (i == odd && kind == 1)
                kind = 3 + (int)urand(3);
            note = su_motif(DEG[kind]) + sh;
            /* the pump's weight: the sixteenth after the kick soft, the off-beat (the "and") accented */
            set_step(tr, i, (i & 3u) == 2u || kind != 1, (i & 3u) == 1u && urand(4) == 0 ? 1 : 0, note);
            if (kind != 1 && i && ln[i - 1u] && urand(5) < 2u)
                tr->slide |= (uint16_t)(1u << i);   /* into the octave on a slide */
        }
        tr->p[0] = near(52, 10);                /* cutoff */
        tr->p[3] = near(30, 6);                 /* decay: short, so it pumps */
        break;
    }
    case ROMI_HAT: {
        static const uint8_t FILL[3] = {38, 50, 62};
        for (i = 2; i < 16; i += 4)
            set_step(tr, i, urand(3) != 0, 0, 0);   /* the off-beat, mostly open */
        for (i = 0; i < 16; i++)
            if (!(tr->step[i].flags & ROMI_ST_ON) && urand(100) < FILL[d]) {
                set_step(tr, i, 0, (int)urand(3), 0);
                if (urand(16) == 0)
                    tr->step[i].flags |= 1u;    /* seldom a double (few rolls) */
            }
        break;
    }
    case ROMI_PERC: {
        /* HAPPO, the acid line: a rhythm cell of eight steps and a motif of eight notes over the chord, played round
         * the loop; the second time round the motif's second half moves up a third now and then */
        static const uint8_t LEN[6] = {16, 16, 16, 12, 14, 8};
        static const uint8_t RHY[6][8] = {{1, 1, 0, 1, 1, 0, 1, 1}, {1, 0, 1, 1, 0, 1, 1, 0}, {1, 1, 1, 0, 1, 1, 0, 1},
                                          {0, 1, 1, 1, 0, 1, 0, 1}, {1, 0, 1, 0, 1, 1, 1, 1}, {1, 1, 0, 1, 0, 1, 1, 0}};
        static const int8_t MOT[8][8] = {
            {0, 0, 7, 0, 4, 0, 7, 2},           /* a pedal with jumps */
            {0, 2, 4, 7, 4, 2, 0, -1},          /* up and down the chord */
            {0, 7, 0, 6, 0, 4, 3, 2},
            {0, 0, 2, 3, 4, 3, 2, 0},           /* a walk */
            {7, 4, 0, 4, 7, 9, 7, 4},
            {0, 1, 0, 4, 0, 6, 0, 7},           /* the phrygian squeak */
            {4, 2, 0, -3, 0, 2, 4, 7},
            {0, 4, 7, 4, 0, 4, 9, 7},
        };
        const uint8_t *rh = RHY[urand(6)];
        const int8_t *mo = MOT[urand(8)];
        int prev = -99, lift = urand(2) ? 2 : 0;
        uint32_t n = 0;
        tr->len = LEN[urand(6)];
        for (i = 0; i < tr->len; i++) {
            int on = rh[i & 7u], dg, note;
            if (urand(10) == 0)
                on = !on;                       /* a step more or less than the cell */
            if (!on) {
                prev = -99;
                continue;
            }
            dg = mo[n & 7u] + (n >= 8u && (n & 7u) >= 4u ? lift : 0);
            note = su_motif(dg < -6 ? -6 : dg);
            set_step(tr, i, dg >= 7 || (n & 3u) == 0u ? urand(3) != 0 : urand(6) == 0, urand(7) == 0 ? 1 : 0, note);
            if (prev > -99 && (note - prev >= 5 || prev - note >= 5) && urand(2))
                tr->slide |= (uint16_t)(1u << i);   /* the big jumps glide */
            prev = note;
            n++;
        }
        tr->p[0] = near(58, 14);                /* cutoff */
        tr->p[2] = near(74, 16);                /* envmod */
        break;
    }
    default:                            /* (KLIKKI: ro:MINImal's clicks, in gen_track) */
        break;
    }
}

/* suom1saundi's sound, at the start and when the style is chosen: its first page on SOUND, one of its second on
 * SOUND 2 (the rest in SU_EXTRA); the bass ducked fully by the kick (the pump), the rest half */
static void su_defaults(romi_pattern_t *p)
{
    static const uint8_t DEF[ROMI_TRACKS][9] = {
        /* p0   p1   p2   p3 level pan  dly  rev  q1 */
        {  48,  58,  62,  40,  92,  64,   0,   0,  50},   /* POTKU (q1 CLICK; SNAP is q2; level 92: 72 %) */
        {  52,  40,  60,  34, 108,  64,   0,   0,   0},   /* BASSO (q1 WAVE: saw) */
        {  40,  72,  70,  64,  84,  76,  14,  14,   0},   /* HATTU (q1 CHIP) */
        {  58,  96,  74,  44,  84,  52,  60,  20,   0},   /* HAPPO (q1 WAVE) */
        {  30,  46,  40,  30,  76,  80,  70,  40,  64},   /* PIIP (q1 SPEED) */
        {  40,  78,  84,  90,  86,  64,  40,  30,   0},   /* KLIKKI: ro:MINImal's click (q1 ATTACK) */
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
        tr->q[2] = t == ROMI_KICK ? 40 : 0;     /* POTKU: SNAP */
        tr->q[3] = 0;
        tr->glide = GLIDE[t];
        tr->follow = 0;                         /* the bass on the chord's root, its own line */
        tr->sc = t == ROMI_KICK ? 0 : t == ROMI_SUB ? 127 : 50;
    }
}
