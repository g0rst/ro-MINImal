/* SPDX-License-Identifier: MIT
 * PIIP's generator, for track 5 or 6 when it plays the engine PIIP (8-BIT), in either style: a melody by the book.
 * A bar in two halves, question and answer, on the same rhythm: the answer repeats the question's motif and closes
 * it. The line moves mostly by steps; on the strong beats it lands on a tone of the chord that sounds there (the
 * stab's, or a minor key's i - VI - VII - i when no stab plays); the question ends open (on the fifth or the second),
 * the answer comes home (to the root, now and then the third). In suom1saundi it leaves room where the acid plays.
 * Included by romi.c ahead of gen_track(). */

/* the harmony at a step: the degree (0..6) of the stab chord sounding there, or i - VI - VII - i over the bar */
static int harmony_at(uint32_t i, uint32_t len)
{
    static const int8_t FALL[4] = {0, 5, 6, 0};
    int k;
    if (R.prj.style >= 2)
        return 0;                       /* FRE3tek, schr4nz: one chord, the drone of the kick */
    for (k = ROMI_STAB; k < ROMI_TRACKS; k++) {
        const romi_track_t *st = &EDT->tr[k];
        uint32_t sl = st->len ? st->len : 1u, j;
        if (st->engine != ROMI_ENG_STAB)
            continue;
        for (j = 0; j < sl; j++) {      /* its last hit at or before the step */
            uint32_t p = (i % sl + sl - j) % sl;
            if (st->step[p].flags & ROMI_ST_ON) {
                int d;
                if (note_degree(st->step[p].note, &d))
                    return (d % 7 + 7) % 7;
                break;
            }
        }
    }
    return FALL[(i * 4u / (len ? len : 16u)) & 3u];
}

/* the degree nearest d whose place over h is one of the mask's (bit k: k degrees over h, 0..6) */
static int nearest_deg(int d, int h, uint32_t mask)
{
    int k;
    for (k = 0; k <= 3; k++) {
        if (mask >> (((d - k - h) % 7 + 7) % 7) & 1u)
            return d - k;
        if (mask >> (((d + k - h) % 7 + 7) % 7) & 1u)
            return d + k;
    }
    return d;
}

static void piip_gen(romi_track_t *tr, int t)
{
    /* rhythms for a half bar, bit k on step k: the sparse ones for ro:MINImal's sparse grooves */
    static const uint8_t RH[3][4] = {{73, 89, 101, 209}, {53, 43, 89, 101}, {173, 85, 43, 209}};
    static const int8_t MOVE[8] = {-1, -1, 1, 1, 1, -2, 2, 0};
    const romi_track_t *acid = &EDT->tr[ROMI_PERC];
    uint32_t i, half, m, nh = 0, alen = acid->len ? acid->len : 1u, pos[8];
    uint32_t rh = RH[R.density > 2 ? 2 : R.density][urand(4)];
    int q[8], d, prev = 0, oct = urand(3) == 0 ? 7 : 0;
    (void)t;
    tr->len = 16;
    for (i = 0; i < 8; i++)
        if (rh >> i & 1u)
            pos[nh++] = i;
    d = nearest_deg(urand(2) ? 2 : 0, harmony_at(0, 16), 0x15u);   /* starts on a chord tone */
    for (half = 0; half < 2; half++)
        for (m = 0; m < nh; m++) {
            uint32_t s = half * 8u + pos[m];
            int last = m + 1 == nh, h = harmony_at(s, 16);
            if (half == 0 && m == 0) {
                /* the opening tone, as chosen */
            } else if (last) {          /* the cadence: open, or home */
                d = half == 0 ? nearest_deg(d, 0, urand(3) ? 0x10u : 0x02u)        /* the fifth (or the second) */
                              : nearest_deg(d, 0, urand(4) ? 0x01u : 0x04u);       /* the root (or the third) */
            } else if (half == 1 && urand(4)) {
                d = q[m];               /* the answer repeats the question */
            } else {
                d += MOVE[urand(8)];
                if ((s & 3u) == 0u)     /* a strong beat: a tone of the chord there */
                    d = nearest_deg(d, h, 0x15u);
            }
            if (d < -2)
                d += 2;
            if (d > 9)
                d -= 2;
            if (half == 0)
                q[m] = d;
            if (STYLE && !last && m && (acid->step[s % alen].flags & ROMI_ST_ON) && urand(2)) {
                tr->step[s].flags = 0;  /* call and response with the acid */
                continue;
            }
            set_step(tr, s, m == 0, m == 0 || last ? 0 : (urand(6) == 0 ? 2 : 0), scale_note(d + oct));
            if ((half || m) && (d - prev == 1 || prev - d == 1) && urand(5) == 0)
                tr->slide |= (uint16_t)(1u << s);   /* a step slides now and then */
            prev = d;
        }
}
