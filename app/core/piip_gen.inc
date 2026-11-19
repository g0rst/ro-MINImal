/* SPDX-License-Identifier: MIT
 * PIIP's generator (suom1saundi's rules), for track 5 or 6 when it plays the engine PIIP, in either style: question
 * and answer, eight notes over the chord; it leaves room where the track before (acid or percussion) plays.
 * Included by romi.c ahead of gen_track(). */
static void piip_gen(romi_track_t *tr, int t)
{
    uint32_t i;
    (void)t;
        /* PIIP, the melody: question and answer, eight notes over the chord; it leaves room where the acid plays */
        static const uint8_t LEN[5] = {16, 16, 12, 10, 6};
        static const int8_t MOT[8][8] = {
            {0, 2, 4, 2, 0, 2, 4, 7}, {7, 6, 4, 2, 4, 2, 1, 0}, {4, 4, 2, 4, 7, 6, 4, 4}, {0, 4, 7, 9, 7, 4, 2, 0},
            {2, 0, -1, 0, 2, 4, 2, 0}, {0, 7, 0, 6, 0, 4, 0, 2}, {4, 3, 2, 0, 2, 3, 4, 7}, {0, 2, 0, 4, 0, 5, 4, 2},
        };
        const int8_t *mo = MOT[urand(8)];
        const romi_track_t *acid = &EDT->tr[ROMI_PERC];
        uint32_t n = 0, up = urand(3) == 0 ? 2u : 0u, alen = acid->len ? acid->len : 1u;
        tr->len = LEN[urand(5)];
        euclid(tr, tr->len / 2u + urand(tr->len / 4u + 1u), urand(tr->len));
        for (i = 0; i < tr->len; i++)
            if (tr->step[i].flags & ROMI_ST_ON) {
                if ((acid->step[i % alen].flags & ROMI_ST_ON) && urand(2)) {
                    tr->step[i].flags = 0;      /* call and response */
                    continue;
                }
                set_step(tr, i, (n & 3u) == 0u, urand(5) == 0 ? 2 : 0, scale_note(mo[n & 7u] + (int)(n / 8u % 2u ? up : 0u)));
                if (n && urand(6) == 0)
                    tr->slide |= (uint16_t)(1u << i);
                n++;
            }
        if (!n) {
            set_step(tr, 0, 1, 0, scale_note(0));
            set_step(tr, tr->len / 2u, 0, 0, scale_note(4));
        }
}
