/* SPDX-License-Identifier: MIT
 * ro:MINImal, style schr4nz (GLO held 2 s in FRE3tek): Schranz, the hard German techno of around 2000 and its
 * return. Included by romi.c after tek_gen.inc (ROMI_SUOMI 1). What the style is, by the book: about 150 BPM, a
 * relentless straight four, minimal melody, everything percussion; loops compressed and distorted; under the kick the
 * rumble (the kick's own reverb, low-passed, pumping on the off-beats against it); hats loud on the sixteenths; a
 * clap on 2 and 4; a metallic loop that grinds against the four; one alarm-like stab at most.
 *
 *   track   0 KICK    memetek's TEK-KICK, short and driven hard: four on the floor, now and then a double at the bar
 *           1 RUMBLE  the ghost of the kick on the sixteenths after it, ducked by it to a pump (tek_voices.inc)
 *           2 HAT     closed on every sixteenth off the kick, open (accented) on the off-beat: the machine gun
 *           3 METAL   ro:MINImal's FM percussion at an inharmonic ratio: one of four grinding loops (3-3-2 and kin)
 *           4 CLAP    NOISE as a clap on 2 and 4                    5 ALARM  PIIP as a square with a siren's wobble
 * 150 BPM, G minor, one chord (the alarm keeps to its tones). The sum through memetek's master, the drive harder and
 * the crusher finer than FRE3tek's (romi.c). */

static void sch_gen(romi_track_t *tr, int t, uint32_t d)
{
    uint32_t i;
    switch (t) {
    case ROMI_KICK: {
        int key = kick_in_key(tr, 0);
        for (i = 0; i < 16; i += 4)
            set_step(tr, i, i == 0, 0, key);
        if (urand(4) == 0)
            set_step(tr, 15, 0, 2, key);        /* the double into the bar, half the time */
        break;
    }
    case ROMI_SUB: {                            /* RUMBLE: per beat one of four, the off-beat accented */
        static const uint8_t RB[4][4] = {{0, 1, 1, 1}, {0, 0, 1, 1}, {0, 1, 0, 1}, {0, 0, 1, 0}};
        const uint8_t *b = RB[d < 1 ? 0 : urand(4)];
        tr->len = 16;
        for (i = 0; i < 16; i++)
            if (b[i & 3u])
                set_step(tr, i, (i & 3u) == 2u, 0, 0);   /* the root: the kick's own tone */
        break;
    }
    case ROMI_HAT:
        for (i = 0; i < 16; i++) {
            if ((i & 3u) == 2u)
                set_step(tr, i, 1, 0, 0);       /* open on the off-beat */
            else if ((i & 3u) != 0u)
                set_step(tr, i, 0, d > 1 && urand(4) == 0 ? 2 : 0, 0);   /* closed on the other two */
            else if (d > 0 && urand(4) == 0)
                set_step(tr, i, 0, 3, 0);       /* now and then a ghost on the kick, at 25 % */
        }
        break;
    case ROMI_PERC: {                           /* METAL: the schranz loop */
        static const uint16_t LOOP[4] = {
            0x5249u,                            /* x..x..x..x..x.x.  3 3 3 3 2 2 */
            0xC924u,                            /* ..x..x..x..x..xx  against it */
            0xB5ADu,                            /* x.xx.x.xx.x.xx.x  gnarled, dense */
            0x5252u,                            /* .x..x.x..x..x.x.  3-3-2 off the beat */
        };
        uint16_t m = LOOP[d < 1 ? 0 : urand(4)];
        uint32_t n = 0;
        tr->len = 16;
        for (i = 0; i < 16; i++)
            if (m >> i & 1u) {
                set_step(tr, i, n == 0, 0, scale_note(n % 3u == 2u ? 4 : 0) + 12);   /* root, root, fifth */
                n++;
            }
        tr->p[0] = near(24, 6);                 /* decay: short, a hit on metal */
        tr->p[1] = near(72, 10);                /* fm: much */
        tr->p[2] = 96;                          /* ratio 4.07: no harmonic, metal */
        tr->p[3] = near(6, 4);                  /* hardly a bend */
        break;
    }
    default:
        break;
    }
}

/* schr4nz's sound at the start: the kick short and ground, the rumble pumping, the hats sharp, the metal */
static void sch_defaults(romi_pattern_t *p)
{
    static const uint8_t DEF[4][9] = {
        /* p0   p1   p2   p3 level pan  dly  rev  q1 */
        {  44,  67,  64, 112, 112,  64,   0,   0,  44},   /* KICK: TUNE DECAY (0.3 s) SWEEP (x6.5) DRIVE (q1 CLICK) */
        {  84,  70,  60,  51,  74,  64,   0,   0,  72},   /* RUMBLE: TONE (190 Hz) SMEAR GRIT DECAY (q1 ATTACK 8 ms) */
        {  40,  70,  90,  70,  74,  72,   0,   6,  10},   /* HAT: DECAY (21 ms) TONE METAL OPEN (q1 CHIP) */
        {  24,  72,  96,   6,  70,  50,  12,  24,  30},   /* METAL: DECAY FM RATIO BEND (q1 B.TIME) */
    };
    static const uint8_t SC[4] = {0, 127, 40, 50};
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
        tr->q[2] = t == ROMI_KICK ? 70 : t == ROMI_PERC ? 30 : 0;   /* KICK: SNAP; METAL: some drive */
        tr->q[3] = 0;
        tr->glide = 0;
        tr->follow = 0;
        tr->sc = SC[t];
    }
}

/* tracks 5 and 6: the clap (NOISE, as it loads: on 2 and 4) a little driven, the alarm (PIIP, a square that wobbles) */
static void sch_engines(romi_pattern_t *p)
{
    romi_track_t *c = &p->tr[ROMI_STAB], *a = &p->tr[ROMI_CLICK];
    c->level = 68;
    c->rev = 34;
    c->q[2] = 40;                               /* DRIVE: a 909 clap through a pedal */
    a->p[0] = 30;                               /* WAVE: square */
    a->p[1] = 40;
    a->p[2] = 0;                                /* no arpeggio */
    a->p[3] = 96;                               /* VIBRATO: the siren's wobble */
    a->level = 48;
    a->dly = 50;
    a->rev = 40;
    a->mute = 1;                                /* it comes in by hand (the mixer) */
}
