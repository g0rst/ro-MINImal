/* SPDX-License-Identifier: MIT
 * Host tests for the ro:MINImal core: tests/run_tests.sh builds and runs this. It also writes a WAV of the factory
 * groove and the screen as PPM images into the directory given as argv[1]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "romi.h"

static int fails;
#define CHECK(c, ...) do { if (!(c)) { fails++; printf("FAIL %s:%d: ", __FILE__, __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)

static int32_t blk[2 * 128];
static uint32_t now_ms;
static uint32_t held_b, held_k;

static void frame(const int32_t *enc)       /* one UI frame, 16 ms of audio */
{
    static const int32_t none[ROMI_NE];
    int i;
    romi_input(held_b, held_k, enc ? enc : none, now_ms);
    for (i = 0; i < 6; i++)
        romi_render(blk, 128, 4096);
    now_ms += 17;
}
static void tap_button(int b) { held_b |= 1u << b; frame(0); held_b &= ~(1u << b); frame(0); }
static void tap_key(int k) { held_k |= 1u << k; frame(0); held_k &= ~(1u << k); frame(0); }
static void turn(int e, int d) { int32_t enc[ROMI_NE] = {0}; enc[e] = d; frame(enc); }

static void write_wav(const char *path, const int16_t *pcm, uint32_t frames)
{
    FILE *f = fopen(path, "wb");
    uint32_t n = frames * 4, v;
    uint16_t w;
    if (!f) return;
    fwrite("RIFF", 1, 4, f); v = 36 + n; fwrite(&v, 4, 1, f); fwrite("WAVEfmt ", 1, 8, f);
    v = 16; fwrite(&v, 4, 1, f); w = 1; fwrite(&w, 2, 1, f); w = 2; fwrite(&w, 2, 1, f);
    v = ROMI_SR; fwrite(&v, 4, 1, f); v = ROMI_SR * 4; fwrite(&v, 4, 1, f); w = 4; fwrite(&w, 2, 1, f);
    w = 16; fwrite(&w, 2, 1, f); fwrite("data", 1, 4, f); fwrite(&n, 4, 1, f); fwrite(pcm, 4, frames, f);
    fclose(f);
}

static void write_screen(const char *path)
{
    static uint16_t px[ROMI_W * ROMI_STRIP_H];
    FILE *f = fopen(path, "wb");
    int s, i;
    if (!f) return;
    fprintf(f, "P6\n%d %d\n255\n", ROMI_W, ROMI_H);
    for (s = 0; s < ROMI_STRIPS; s++) {
        romi_draw(px, s);
        for (i = 0; i < ROMI_W * ROMI_STRIP_H; i++) {
            uint8_t rgb[3] = {(uint8_t)((px[i] >> 11) << 3), (uint8_t)((px[i] >> 5 & 63) << 2), (uint8_t)((px[i] & 31) << 3)};
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
}

/* render seconds of the playing groove: peak, RMS, a hash, NaN-free */
static uint32_t run(double seconds, int16_t *pcm, double *peak, double *rms)
{
    uint32_t frames = (uint32_t)(seconds * ROMI_SR) / 128 * 128, i, k, h = 2166136261u;
    double sum = 0, pk = 0;
    for (i = 0; i < frames; i += 128) {
        romi_render(blk, 128, 4096);
        for (k = 0; k < 256; k++) {
            double v = blk[k] / 8388608.0;
            if (fabs(v) > pk) pk = fabs(v);
            sum += v * v;
            h = (h ^ (uint32_t)blk[k]) * 16777619u;
            if (pcm) pcm[2 * i + k] = (int16_t)(blk[k] >> 8);
        }
    }
    if (peak) *peak = pk;
    if (rms) *rms = sqrt(sum / (frames * 2.0));
    return h;
}

int main(int argc, char **argv)
{
    const char *out = argc > 1 ? argv[1] : ".";
    char path[512];
    double peak, rms;
    uint32_t h1, h2, n;
    static int16_t pcm[2 * ROMI_SR * 20];
    int i, v;

    /* silence until PLAY; then sound, bounded, deterministic for a seed */
    romi_init(1234);
    run(0.5, 0, &peak, &rms);
    CHECK(peak == 0.0, "sound before PLAY: peak %f", peak);
    tap_button(ROMI_B_PLAY);
    CHECK(romi_state(ROMI_Q_PLAYING) == 1, "PLAY did not start");
    h1 = run(15.2, pcm, &peak, &rms);
    printf("groove: peak %.3f rms %.3f hash %08x\n", peak, rms, h1);
    CHECK(peak > 0.3 && peak <= 1.0, "peak %f", peak);
    CHECK(rms > 0.03 && rms < 0.5, "rms %f", rms);
    snprintf(path, sizeof path, "%s/groove.wav", out);
    write_wav(path, pcm, (uint32_t)(15.2 * ROMI_SR) / 128 * 128);
    snprintf(path, sizeof path, "%s/screen-groove.ppm", out);
    write_screen(path);

    romi_init(1234);
    now_ms = 0;
    tap_button(ROMI_B_PLAY);
    h2 = run(15.2, 0, 0, 0);
    CHECK(h1 == h2, "same seed, different audio: %08x %08x", h1, h2);
    romi_init(99);
    tap_button(ROMI_B_PLAY);
    CHECK(run(15.2, 0, 0, 0) != h1, "another seed, the same audio");

    /* the clock: 126 BPM is 8.4 sixteenths a second; MIDI clock 6 a sixteenth */
    romi_init(5);
    tap_button(ROMI_B_PLAY);
    while (romi_midi_rt_pop() >= 0) {}
    v = romi_state(ROMI_Q_GSTEP);
    run(10.0, 0, 0, 0);
    v = romi_state(ROMI_Q_GSTEP) - v;
    CHECK(v >= 83 && v <= 85, "steps in 10 s at 126 BPM: %d", v);
    for (n = 0; romi_midi_rt_pop() >= 0;) n++;
    CHECK(n > 0, "no MIDI clock");
    tap_button(ROMI_B_PLAY);
    CHECK(romi_state(ROMI_Q_PLAYING) == 0, "PLAY did not stop");
    run(6.0, 0, 0, 0);
    run(0.5, 0, &peak, 0);
    CHECK(peak < 0.01, "tails after stop: %f", peak);

    /* steps: a white key toggles; hold and turn edits without toggling; ALGO sets the length (polymetre) */
    romi_init(7);
    tap_key(1 + 2 * 3 > 0 ? 8 : 8);                 /* black key 3 (key 8): the PERC track */
    CHECK(romi_state(ROMI_Q_TRACK) == ROMI_PERC, "track %d", romi_state(ROMI_Q_TRACK));
    tap_key(15);                                    /* black key 6: clear */
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 0, "clear left %d steps", romi_state(ROMI_Q_STEPS_ON));
    turn(ROMI_E_ALGO, 16);
    turn(ROMI_E_ALGO, -9);
    CHECK(romi_state(ROMI_Q_LEN) == 7, "len %d", romi_state(ROMI_Q_LEN));
    tap_key(0);
    tap_key(4);
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 2, "steps on %d", romi_state(ROMI_Q_STEPS_ON));
    held_k = 1u << 4; frame(0);                     /* hold step 3, turn K1: the note; no toggle on release */
    turn(ROMI_E_K1, 5);
    held_k = 0; frame(0); frame(0);
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 2, "an edited step toggled: %d", romi_state(ROMI_Q_STEPS_ON));
    CHECK(romi_project()->pat[0].tr[ROMI_PERC].step[2].note == 5, "note %d", romi_project()->pat[0].tr[ROMI_PERC].step[2].note);
    tap_key(26);                                    /* step 16 is beyond the loop: nothing */
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 2, "a step beyond the length was set");
    tap_button(ROMI_B_PLAY);
    for (i = 0; i < 400; i++) {                     /* the playhead never leaves the loop */
        run(0.01, 0, 0, 0);
        CHECK(romi_state(ROMI_Q_POS) < 7, "pos %d in a loop of 7", romi_state(ROMI_Q_POS));
    }
    tap_button(ROMI_B_PLAY);
    tap_key(25);                                    /* black key 10: undo (the last kept: before the clear) */

    /* pages, tempo, mute, generate */
    tap_button(ROMI_B_HOME);
    turn(ROMI_E_K1, -6);
    CHECK(romi_state(ROMI_Q_BPM) == 120, "bpm %d", romi_state(ROMI_Q_BPM));
    tap_button(ROMI_B_FX);
    CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_FX, "page %d", romi_state(ROMI_Q_PAGE));
    tap_button(ROMI_B_SEL);
    CHECK(romi_state(ROMI_Q_MUTE) == 1, "mute");
    tap_button(ROMI_B_SEL);
    CHECK(romi_state(ROMI_Q_MUTE) == 0, "unmute");
    tap_key(22);                                    /* NEW: the track */
    CHECK(romi_state(ROMI_Q_STEPS_ON) > 0, "generate made nothing");
    snprintf(path, sizeof path, "%s/screen-fx.ppm", out);
    write_screen(path);
    held_k = 1u << 0; frame(0);
    snprintf(path, sizeof path, "%s/screen-step.ppm", out);
    write_screen(path);
    held_k = 0; frame(0);
    tap_key(0);                                     /* (put step 1 back as it was) */

    /* the store: settings and each pattern packed on their own; a damaged or short object refused, the others
     * load; all of it loads back the same; SAVE asks only for what changed */
    CHECK(romi_state(ROMI_Q_UNSAVED) == 1, "not marked unsaved");
    tap_button(ROMI_B_SAVE);
    {
        static uint8_t obj[ROMI_NOBJ][ROMI_OBJ_MAX], again[ROMI_OBJ_MAX];
        uint32_t len[ROMI_NOBJ], m;
        int k;
        m = romi_save_wanted();
        CHECK(m == 3u && romi_save_wanted() == 0, "first save: mask %x (the settings and A only)", m);
        for (k = 0; k < ROMI_NOBJ; k++) {
            len[k] = romi_store_get(k, obj[k], sizeof obj[k]);
            CHECK(len[k] > 0 && len[k] <= ROMI_OBJ_MAX && len[k] <= 3840, "object %d: %u bytes", k, len[k]);
            romi_store_saved(k);
        }
        printf("store: settings %u bytes, patterns %u %u %u %u bytes\n", len[0], len[1], len[2], len[3], len[4]);
        tap_button(ROMI_B_SAVE);
        CHECK(romi_save_wanted() == 0, "nothing changed, yet something to save");
        turn(ROMI_E_ALGO, -1);                      /* a change in pattern A only */
        tap_button(ROMI_B_SAVE);
        m = romi_save_wanted();
        CHECK(m == 1u << 1, "one change in A: mask %x", m);
        turn(ROMI_E_ALGO, 1);                       /* back as saved */
        romi_init(31337);
        obj[2][20] ^= 1;                            /* pattern B damaged */
        CHECK(romi_store_set(2, obj[2], len[2]) != 0, "a damaged pattern loaded");
        obj[2][20] ^= 1;
        CHECK(romi_store_set(1, obj[1], len[1] - 1) != 0, "a short pattern loaded");
        CHECK(romi_store_set(2, obj[1], len[1]) != 0, "pattern A loaded as B");
        for (k = 0; k < ROMI_NOBJ; k++)
            CHECK(romi_store_set(k, obj[k], len[k]) == 0, "object %d did not load", k);
        CHECK(romi_state(ROMI_Q_BPM) == 120, "bpm after load %d", romi_state(ROMI_Q_BPM));
        for (k = 0; k < ROMI_NOBJ; k++)
            CHECK(romi_store_get(k, again, sizeof again) == len[k] && !memcmp(obj[k], again, len[k]),
                  "object %d: load and save differ", k);
        tap_button(ROMI_B_SAVE);
        CHECK(romi_save_wanted() == 0, "just loaded, yet something to save");
    }

    /* the packed limits: shift and note at their ends, locks up to 32 a pattern and no more */
    romi_init(41);
    {
        static uint8_t obj[ROMI_OBJ_MAX];
        romi_track_t *tr = &romi_project()->pat[0].tr[ROMI_PERC];
        uint32_t n;
        int k, t2, got = 0;
        tr->step[3].flags = 0x80 | 0x40 | 0x20 | 0x02; tr->step[3].shift = -7; tr->step[3].note = -32;
        tr->step[4].flags = 0x80; tr->step[4].shift = 7; tr->step[4].note = 31;
        n = romi_store_get(1, obj, sizeof obj);
        romi_init(42);
        CHECK(romi_store_set(1, obj, n) == 0, "limits: did not load");
        tr = &romi_project()->pat[0].tr[ROMI_PERC];
        CHECK(tr->step[3].flags == 0xE2 && tr->step[3].shift == -7 && tr->step[3].note == -32 &&
              tr->step[4].shift == 7 && tr->step[4].note == 31, "limits: %02x %d %d / %d %d", tr->step[3].flags,
              tr->step[3].shift, tr->step[3].note, tr->step[4].shift, tr->step[4].note);
        tap_button(ROMI_B_EDIT);                    /* 32 locks by hand: the kick's 16 steps, two knobs each */
        for (k = 0; k < 16; k++) {
            int wk[16] = {0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26};
            held_k = 1u << wk[k]; frame(0);
            turn(ROMI_E_K1, 1);
            turn(ROMI_E_K2, 1);
            held_k = 0; frame(0); frame(0);
        }
        for (t2 = 0; t2 < ROMI_TRACKS; t2++)
            for (k = 0; k < ROMI_STEPS; k++)
                for (i = 0; i < 4; i++)
                    got += romi_project()->pat[0].tr[t2].step[k].lock[i] != 0;
        CHECK(got == 32, "locks set: %d", got);
        held_k = 1u << 0; frame(0);
        turn(ROMI_E_K3, 1);                         /* the 33rd: refused */
        held_k = 0; frame(0); frame(0);
        CHECK(romi_project()->pat[0].tr[0].step[0].lock[2] == 0, "a 33rd lock was set");
        held_k = 1u << 0; frame(0);
        turn(ROMI_E_K1, 2);                         /* an existing lock still turns */
        held_k = 0; frame(0); frame(0);
        n = romi_store_get(1, obj, sizeof obj);
        romi_init(43);
        CHECK(romi_store_set(1, obj, n) == 0 && n <= ROMI_OBJ_MAX, "32 locks: did not load (%u bytes)", n);
        for (got = 0, k = 0; k < ROMI_STEPS; k++)
            for (i = 0; i < 4; i++)
                got += romi_project()->pat[0].tr[0].step[k].lock[i] != 0;
        CHECK(got == 32, "locks after load: %d", got);
        printf("store: a pattern with 32 locks, %u bytes\n", n);
    }

    /* every generated groove of many seeds plays without clipping hard or going silent */
    for (i = 0; i < 40; i++) {
        romi_init(1000u + (uint32_t)i * 7919u);
        tap_button(ROMI_B_PLAY);
        run(4.0, 0, &peak, &rms);
        CHECK(peak > 0.2 && peak <= 1.0 && rms > 0.02, "seed %d: peak %f rms %f", i, peak, rms);
    }

    /* K4 on a held step: the ratchet; LFO held: solo; CHAIN walks the patterns every four bars */
    romi_init(11);
    held_k = 1u << 0; frame(0);
    turn(ROMI_E_K4, 2);
    held_k = 0; frame(0); frame(0);
    CHECK(ROMI_ST_RATCH(romi_project()->pat[0].tr[0].step[0].flags) == 3, "ratchet %u",
          ROMI_ST_RATCH(romi_project()->pat[0].tr[0].step[0].flags));
    held_b = 1u << ROMI_B_SEL;
    for (i = 0; i < 40; i++) frame(0);
    held_b = 0; frame(0);
    CHECK(romi_state(ROMI_Q_SOLO) == 0 && romi_state(ROMI_Q_MUTE) == 0, "solo %d mute %d", romi_state(ROMI_Q_SOLO), romi_state(ROMI_Q_MUTE));
    tap_button(ROMI_B_PLAY);
    run(4.0, 0, &peak, &rms);
    CHECK(peak > 0.2, "the solo kick is silent: %f", peak);
    held_b = 1u << ROMI_B_SEL;
    for (i = 0; i < 40; i++) frame(0);
    held_b = 0; frame(0);
    CHECK(romi_state(ROMI_Q_SOLO) == -1, "solo off: %d", romi_state(ROMI_Q_SOLO));
    tap_button(ROMI_B_PLAY);
    romi_project()->chain = 2;
    tap_button(ROMI_B_PLAY);
    run(64 * 15.0 / 126 + 0.3, 0, 0, 0);
    CHECK(romi_state(ROMI_Q_PATTERN) == 1, "chain after 4 bars: pattern %d", romi_state(ROMI_Q_PATTERN));
    run(2 * 64 * 15.0 / 126, 0, 0, 0);
    CHECK(romi_state(ROMI_Q_PATTERN) == 0, "chain after 12 bars: pattern %d", romi_state(ROMI_Q_PATTERN));

    /* SEQ: the EUCLID page spreads hits over the loop; UNDO brings the steps back */
    romi_init(21);
    tap_key(8);                                     /* PERC */
    v = romi_state(ROMI_Q_STEPS_ON);
    tap_button(ROMI_B_SEQ);
    CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_EUCLID, "SEQ: page %d", romi_state(ROMI_Q_PAGE));
    turn(ROMI_E_ALGO, 16);
    turn(ROMI_E_K1, -16);
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 0, "0 hits: %d steps", romi_state(ROMI_Q_STEPS_ON));
    turn(ROMI_E_K1, 5);
    CHECK(romi_state(ROMI_Q_STEPS_ON) == 5, "5 hits: %d steps", romi_state(ROMI_Q_STEPS_ON));
    {
        const romi_track_t *tr = &romi_project()->pat[0].tr[ROMI_PERC];
        int gaps = 0, last = -1, lo = 99, hi = 0;
        for (i = 0; i < 32; i++)
            if (tr->step[i % 16].flags & ROMI_ST_ON) {
                if (last >= 0) { int g = i - last; if (g < lo) lo = g; if (g > hi) hi = g; gaps++; }
                last = i;
            }
        CHECK(gaps && hi - lo <= 1 && (tr->step[0].flags & ROMI_ST_ON), "5 in 16 uneven: gaps %d..%d", lo, hi);
        turn(ROMI_E_K2, 2);
        CHECK(!(tr->step[0].flags & ROMI_ST_ON) && (tr->step[2].flags & ROMI_ST_ON), "rotate by 2");
        turn(ROMI_E_K3, -2);
        turn(ROMI_E_K4, 2);
        CHECK(ROMI_ST_PROB(tr->step[2].flags) == 2 && (tr->step[2].flags & ROMI_ST_ACC), "chance and accent: %02x", tr->step[2].flags);
    }
    tap_key(25);                                    /* UNDO */
    CHECK(romi_state(ROMI_Q_STEPS_ON) == v, "undo after euclid: %d, was %d", romi_state(ROMI_Q_STEPS_ON), v);

    /* SAVE tapped: a save */
    romi_init(22);
    romi_save_wanted();
    tap_button(ROMI_B_SAVE);
    CHECK(romi_save_wanted() != 0, "a tap on SAVE did not save");

    /* the sidechain: the muted kick still ducks the rest; a track with AMOUNT 0 is left alone */
    {
        double loud, ducked;
        for (v = 0; v < 2; v++) {
            romi_init(23);
            romi_project()->pat[0].tr[ROMI_KICK].mute = 1;
            romi_project()->drift = 0;
            romi_project()->duck = v ? 127 : 0;
            tap_button(ROMI_B_PLAY);
            run(8.0, 0, 0, v ? &ducked : &loud);
        }
        CHECK(ducked < loud * 0.96, "ghost sidechain: rms %f against %f", ducked, loud);
        tap_button(ROMI_B_FX);
        tap_button(ROMI_B_FX);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_SC, "FX twice: page %d", romi_state(ROMI_Q_PAGE));
    }

    /* microtiming: a step held, SELECT nudges it; it sounds that much early or late */
    for (v = -7; v <= 7; v += 7) {
        static const int32_t none[ROMI_NE];
        int t, first = -1;
        romi_init(24);
        for (t = 0; t < ROMI_TRACKS; t++)
            for (i = 0; i < ROMI_STEPS; i++)
                romi_project()->pat[0].tr[t].step[i].flags = 0;
        tap_key(7);                                 /* step 5 of the kick, set */
        if (v) {                                    /* (held without a turn, the release would toggle it) */
            held_k = 1u << 7; frame(0);
            turn(ROMI_E_SELECT, v);
            held_k = 0; frame(0); frame(0);
        }
        CHECK(romi_project()->pat[0].tr[0].step[4].shift == v && romi_state(ROMI_Q_STEPS_ON) == 1 &&
              romi_state(ROMI_Q_TRACK) == 0, "shift %d: %d", v, romi_project()->pat[0].tr[0].step[4].shift);
        run(1.0, 0, 0, 0);
        romi_input(1u << ROMI_B_PLAY, 0, none, now_ms);
        run(1.0, pcm, 0, 0);
        romi_input(0, 0, none, now_ms);
        for (i = 0; i < ROMI_SR - 128 && first < 0; i++)
            if (abs(pcm[2 * i]) > 300) first = i;
        /* step 5 starts 4 sixteenths in: 21000 samples at 126 BPM; a full shift is half a sixteenth, 2625 */
        CHECK(abs(first - (21000 + v * 2625 / 8)) < 200, "shift %d: the kick at sample %d", v, first);
    }

    /* locks: a step held on the sound page gets its own value; the track's stays; SEL makes the step plain */
    romi_init(25);
    tap_button(ROMI_B_EDIT);
    v = romi_project()->pat[0].tr[0].p[0];
    held_k = 1u << 0; frame(0);
    turn(ROMI_E_K1, 3);
    CHECK(romi_project()->pat[0].tr[0].step[0].lock[0] == v + 12 + 1 && romi_project()->pat[0].tr[0].p[0] == v,
          "lock %d, track %d (was %d)", romi_project()->pat[0].tr[0].step[0].lock[0], romi_project()->pat[0].tr[0].p[0], v);
    snprintf(path, sizeof path, "%s/screen-lock.ppm", out);
    write_screen(path);
    tap_button(ROMI_B_SEL);
    CHECK(romi_project()->pat[0].tr[0].step[0].lock[0] == 0, "SEL on a held step left its lock");
    held_k = 0; frame(0); frame(0);
    CHECK(romi_project()->pat[0].tr[0].step[0].flags & ROMI_ST_ON, "the step went off");
    {   /* a locked step sounds different from the same step without */
        uint32_t a, b;
        romi_init(26); romi_project()->drift = 0; tap_button(ROMI_B_PLAY); a = run(2.0, 0, 0, 0);
        romi_init(26); romi_project()->drift = 0; romi_project()->pat[0].tr[0].step[0].lock[1] = 128;
        tap_button(ROMI_B_PLAY); b = run(2.0, 0, 0, 0);
        CHECK(a != b, "a lock changed nothing");
    }

    /* LINK: a track's steps gated by another track's hits: with them, in their gaps, a step after them */
    for (v = 0; v < 3; v++) {
        int kick, hat, steps;
        romi_init(27);
        romi_project()->drift = 0;
        for (i = 0; i < ROMI_STEPS; i++) {
            romi_project()->pat[0].tr[ROMI_KICK].step[i].flags = (uint8_t)(i % 4 == 0 ? 0x80 : 0);
            romi_project()->pat[0].tr[ROMI_HAT].step[i].flags = 0x80;
        }
        romi_project()->pat[0].tr[ROMI_KICK].len = romi_project()->pat[0].tr[ROMI_HAT].len = 16;
        romi_project()->pat[0].tr[ROMI_KICK].mute = (uint8_t)(v == 1);   /* a muted source gates all the same */
        tap_key(5);                                 /* HAT */
        tap_button(ROMI_B_SEQ);
        tap_button(ROMI_B_SEQ);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_LINK, "SEQ twice: page %d", romi_state(ROMI_Q_PAGE));
        turn(ROMI_E_K1, 1);
        if (v) turn(ROMI_E_K2, v);
        CHECK(romi_project()->pat[0].tr[ROMI_HAT].dep_src == 1 && romi_project()->pat[0].tr[ROMI_HAT].dep_mode == v,
              "link %d mode %d", romi_project()->pat[0].tr[ROMI_HAT].dep_src, romi_project()->pat[0].tr[ROMI_HAT].dep_mode);
        tap_button(ROMI_B_PLAY);
        run(64 * 15.0 / 126 + 0.05, 0, 0, 0);       /* four bars and a little: step 65 has begun */
        steps = romi_state(ROMI_Q_GSTEP);
        kick = romi_state(ROMI_Q_HITS + ROMI_KICK);
        hat = romi_state(ROMI_Q_HITS + ROMI_HAT);
        if (v == 0) CHECK(kick == 17 && hat == kick, "WITH: kick %d hat %d of %d steps", kick, hat, steps);
        if (v == 1) CHECK(kick == 0 && hat == steps - 17, "GAPS: kick %d hat %d of %d steps", kick, hat, steps);
        if (v == 2) CHECK(kick == 17 && hat == 16, "AFTER: kick %d hat %d of %d steps", kick, hat, steps);
    }

    /* the TIMING page: SELECT walks the hits, a key picks a step without toggling it; the first knob shifts that
     * step, the second the whole track; the track's choice and its steps stay */
    romi_init(28);
    {
        romi_track_t *tr = &romi_project()->pat[0].tr[ROMI_PERC];
        int on;
        for (i = 0; i < ROMI_STEPS; i++)
            tr->step[i].flags = (uint8_t)(i == 2 || i == 5 || i == 11 ? 0x80 : 0);
        tr->len = 16;
        tap_key(8);                                 /* PERC */
        tap_button(ROMI_B_SEQ); tap_button(ROMI_B_SEQ); tap_button(ROMI_B_SEQ);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_TIMING, "SEQ three times: page %d", romi_state(ROMI_Q_PAGE));
        turn(ROMI_E_SELECT, 1);
        CHECK(romi_state(ROMI_Q_CURSOR) == 2 && romi_state(ROMI_Q_TRACK) == ROMI_PERC, "cursor %d track %d",
              romi_state(ROMI_Q_CURSOR), romi_state(ROMI_Q_TRACK));
        turn(ROMI_E_K1, -3);
        turn(ROMI_E_SELECT, 2);
        CHECK(romi_state(ROMI_Q_CURSOR) == 11, "cursor %d", romi_state(ROMI_Q_CURSOR));
        turn(ROMI_E_K1, 5);
        turn(ROMI_E_SELECT, 1);                     /* round the end, to the first hit */
        CHECK(romi_state(ROMI_Q_CURSOR) == 2, "cursor wrapped to %d", romi_state(ROMI_Q_CURSOR));
        turn(ROMI_E_SELECT, -1);
        CHECK(romi_state(ROMI_Q_CURSOR) == 11, "cursor back to %d", romi_state(ROMI_Q_CURSOR));
        on = romi_state(ROMI_Q_STEPS_ON);
        tap_key(9);                                 /* the white key of step 6 */
        CHECK(romi_state(ROMI_Q_CURSOR) == 5 && romi_state(ROMI_Q_STEPS_ON) == on, "a key on the timing page: cursor %d, %d steps",
              romi_state(ROMI_Q_CURSOR), romi_state(ROMI_Q_STEPS_ON));
        turn(ROMI_E_K1, 20);
        turn(ROMI_E_K2, -2);
        CHECK(tr->step[2].shift == -3 && tr->step[11].shift == 5 && tr->step[5].shift == 7 && tr->tshift == -2,
              "shifts %d %d %d track %d", tr->step[2].shift, tr->step[11].shift, tr->step[5].shift, tr->tshift);
        snprintf(path, sizeof path, "%s/screen-timing.ppm", out);
        write_screen(path);
    }
    for (v = -8; v <= 8; v += 16) {                 /* the whole track early or late: heard */
        static const int32_t none[ROMI_NE];
        int t, first = -1;
        romi_init(29);
        for (t = 0; t < ROMI_TRACKS; t++)
            for (i = 0; i < ROMI_STEPS; i++)
                romi_project()->pat[0].tr[t].step[i].flags = (uint8_t)(t == 0 && i == 4 ? 0x80 : 0);
        romi_project()->pat[0].tr[0].tshift = (int8_t)v;
        romi_input(1u << ROMI_B_PLAY, 0, none, now_ms);
        run(1.0, pcm, 0, 0);
        romi_input(0, 0, none, now_ms);
        for (i = 0; i < ROMI_SR - 128 && first < 0; i++)
            if (abs(pcm[2 * i]) > 300) first = i;
        CHECK(abs(first - (21000 + v * 2625 / 8)) < 200, "track shift %d: the kick at sample %d", v, first);
    }

    /* the STAB generator: a phrase, not one tone. Over many seeds and all four scales: at least two hits, more than
     * one pitch, every note in the scale, in a playable register, and the phrases differ from seed to
     * seed */
    {
        static const uint8_t SC[4][7] = {{0, 2, 3, 5, 7, 8, 10}, {0, 2, 3, 5, 7, 9, 10}, {0, 1, 3, 5, 7, 8, 10},
                                         {0, 3, 5, 7, 10, 12, 15}};
        int seed, sc, one_tone = 0, total = 0, distinct_phrases = 0;
        uint32_t seen[64];
        int nseen = 0;
        for (sc = 0; sc < 4; sc++)
            for (seed = 0; seed < 60; seed++) {
                const romi_track_t *tr;
                int k, hits = 0, first = 99, lastn = 99, multi = 0, lastpos = -1;
                uint32_t h = 2166136261u;
                romi_init(5000u + (uint32_t)seed * 31u);
                romi_project()->scale = (uint8_t)sc;
                tap_key(10);                        /* STAB (black key 5) */
                tap_key(22);                        /* NEW: the track */
                tr = &romi_project()->pat[0].tr[ROMI_STAB];
                for (k = 0; k < tr->len; k++) {
                    int nt = tr->step[k].note, m = ((nt % 12) + 12) % 12, j, ok = 0;
                    if (!(tr->step[k].flags & ROMI_ST_ON))
                        continue;
                    hits++;
                    if (first == 99) first = nt;
                    if (nt != first) multi = 1;
                    lastn = nt;
                    lastpos = k;
                    h = (h ^ (uint32_t)(k * 64 + nt + 32)) * 16777619u;
                    for (j = 0; j < 7; j++)
                        ok |= SC[sc][j] % 12 == m;
                    CHECK(ok, "scale %d seed %d: note %d not in the scale", sc, seed, nt);
                    CHECK(nt >= -7 && nt <= 12, "scale %d seed %d: note %d out of the register", sc, seed, nt);
                }
                (void)lastpos;
                total++;
                CHECK(hits >= 2, "scale %d seed %d: %d hits", sc, seed, hits);
                if (!multi) one_tone++;
                (void)lastn;
                if (sc == 0) {
                    int j, dup = 0;
                    for (j = 0; j < nseen; j++) dup |= seen[j] == h;
                    if (!dup && nseen < 64) { seen[nseen++] = h; distinct_phrases++; }
                }
            }
        printf("stab: %d of %d phrases on one tone; %d different phrases in 60 seeds\n", one_tone, total, distinct_phrases);
        CHECK(one_tone * 50 <= total, "too many one-tone phrases: %d of %d", one_tone, total);
        CHECK(distinct_phrases >= 30, "only %d different phrases in 60 seeds", distinct_phrases);
    }

    /* FOLLOW: the sub transposed by the stab's written chord, from the stab's step on, through a mute; off: not */
    for (v = 0; v < 2; v++) {
        romi_track_t *sub, *stab;
        int got[16], k;
        romi_init(31);
        romi_project()->drift = 0;
        sub = &romi_project()->pat[0].tr[ROMI_SUB];
        stab = &romi_project()->pat[0].tr[ROMI_STAB];
        CHECK(sub->follow == ROMI_STAB + 1, "the sub does not follow the stab by default: %d", sub->follow);
        for (i = 0; i < ROMI_STEPS; i++) {
            sub->step[i].flags = 0x80; sub->step[i].note = 0;
            stab->step[i].flags = 0; stab->step[i].note = 0;
        }
        sub->len = stab->len = 16;
        stab->step[2].flags = 0xB0; stab->step[2].note = 0;    /* chance 25 %: the harmony is the written one */
        stab->step[6].flags = 0x80; stab->step[6].note = -4;   /* VI below */
        stab->step[11].flags = 0x80; stab->step[11].note = 7;  /* v: folded to a fourth below */
        stab->mute = 1;
        if (v) {                                               /* LINK page of the sub: FOLLOW off */
            tap_key(3);
            tap_button(ROMI_B_SEQ); tap_button(ROMI_B_SEQ);
            turn(ROMI_E_K3, -6);
            CHECK(sub->follow == 0, "FOLLOW not off: %d", sub->follow);
        }
        tap_button(ROMI_B_PLAY);
        for (k = 0; k < 16; k++) {                             /* the note of each sub hit, step by step */
            int g0 = romi_state(ROMI_Q_GSTEP);
            while (romi_state(ROMI_Q_GSTEP) == g0) run(0.003, 0, 0, 0);
            run(0.02, 0, 0, 0);
            got[k] = romi_state(ROMI_Q_NOTE + ROMI_SUB);
        }
        tap_button(ROMI_B_PLAY);
        if (!v) {
            /* (got[k] is step k + 1: read once the step after it has begun) the stab's chords on steps 3, 7, 12 */
            static const int8_t WANT[16] = {-5, 0, 0, 0, 0, -4, -4, -4, -4, -4, -5, -5, -5, -5, -5, -5};
            for (k = 0; k < 16; k++)
                CHECK(got[k] == WANT[k], "follow: step %d note %d, want %d", k + 1, got[k], WANT[k]);
        } else {
            for (k = 0; k < 16; k++) CHECK(got[k] == 0, "FOLLOW off: step %d note %d", k, got[k]);
        }
    }

    /* NEW (the whole groove): one groove, not six dice. Over many throws, roots and scales: the kick four on the
     * floor and tuned to the key; the sub never on a quarter (so never on the kick, in a 12- or 16-step loop) and
     * starting on the root; hats on every off-beat; the percussion's notes in the scale and its hits mostly off the
     * kick; every note of every melodic track in the scale; each throw different; and the groove plays clean */
    {
        static const uint8_t SC[4][7] = {{0, 2, 3, 5, 7, 8, 10}, {0, 2, 3, 5, 7, 9, 10}, {0, 1, 3, 5, 7, 8, 10},
                                         {0, 3, 5, 7, 10, 12, 15}};
        uint32_t seen[200];
        int nseen = 0, throw_, perc_on_kick = 0, perc_hits = 0, dens[3] = {0, 0, 0};
        for (throw_ = 0; throw_ < 200; throw_++) {
            const romi_pattern_t *pt;
            int t2, k, sc = throw_ % 4, root = 24 + (throw_ * 7) % 24, ok;
            uint32_t h = 2166136261u;
            romi_init(9000u + (uint32_t)throw_ * 101u);
            romi_project()->scale = (uint8_t)sc;
            romi_project()->root = (uint8_t)root;
            held_k = 1u << 22;                      /* NEW held: the whole groove */
            for (k = 0; k < 32; k++) frame(0);
            held_k = 0; frame(0);
            pt = &romi_project()->pat[0];
            /* the kick: four on the floor, all on one note, which puts its pitch on the root */
            for (k = 0; k < 16; k += 4)
                CHECK(pt->tr[ROMI_KICK].step[k].flags & ROMI_ST_ON, "throw %d: kick missing on %d", throw_, k);
            {
                double f0 = 36.0 * pow(2.0, pt->tr[ROMI_KICK].p[0] / 127.0) *
                            pow(2.0, pt->tr[ROMI_KICK].step[0].note / 12.0);
                double cents = fmod(1200.0 * log2(f0 / (440.0 * pow(2.0, (root - 69) / 12.0))) + 12000.0, 1200.0);
                if (cents > 600.0) cents = 1200.0 - cents;
                CHECK(cents < 60.0, "throw %d: the kick is %0.f cents off the key", throw_, cents);
            }
            /* the sub */
            {
                const romi_track_t *sub = &pt->tr[ROMI_SUB];
                int first = 1;
                for (k = 0; k < sub->len; k++) {
                    if (!(sub->step[k].flags & ROMI_ST_ON)) continue;
                    CHECK((k & 3) != 0, "throw %d: the sub on a quarter (%d)", throw_, k);
                    if (first) CHECK(sub->step[k].note == 0, "throw %d: the sub starts on %d", throw_, sub->step[k].note);
                    first = 0;
                }
                CHECK(!first, "throw %d: no sub", throw_);
            }
            /* the hats on the off-beat */
            for (k = 2; k < 16; k += 4)
                CHECK(pt->tr[ROMI_HAT].step[k].flags & ROMI_ST_ON, "throw %d: no hat on %d", throw_, k);
            /* notes in the scale: stab and percussion (the sub follows the stab: chord tones) */
            for (t2 = ROMI_PERC; t2 <= ROMI_STAB; t2++)
                for (k = 0; k < pt->tr[t2].len; k++) {
                    int m, j;
                    if (!(pt->tr[t2].step[k].flags & ROMI_ST_ON)) continue;
                    m = ((pt->tr[t2].step[k].note % 12) + 12) % 12;
                    for (ok = 0, j = 0; j < 7; j++) ok |= SC[sc][j] % 12 == m;
                    CHECK(ok, "throw %d: track %d note %d not in scale %d", throw_, t2, pt->tr[t2].step[k].note, sc);
                }
            /* the percussion against the kick, over four bars */
            {
                const romi_track_t *pc = &pt->tr[ROMI_PERC];
                int g;
                for (g = 0; g < 64; g++)
                    if (pc->step[g % pc->len].flags & ROMI_ST_ON) {
                        perc_hits++;
                        perc_on_kick += (g & 3) == 0;
                    }
            }
            /* every throw its own */
            for (t2 = 0; t2 < ROMI_TRACKS; t2++)
                for (k = 0; k < ROMI_STEPS; k++)
                    h = (h ^ (uint32_t)(pt->tr[t2].step[k].flags * 131 + pt->tr[t2].step[k].note + 64 + t2 * 977 + k)) *
                        16777619u;
            for (ok = 1, k = 0; k < nseen; k++) ok &= seen[k] != h;
            if (ok) seen[nseen++] = h;
            dens[romi_state(ROMI_Q_DENSITY)]++;
            /* and it plays clean */
            if (throw_ % 10 == 0) {
                tap_button(ROMI_B_PLAY);
                run(3.0, 0, &peak, &rms);
                CHECK(peak > 0.2 && peak <= 1.0 && rms > 0.02, "throw %d: peak %f rms %f", throw_, peak, rms);
            }
        }
        printf("new: %d different grooves in 200; percussion on the kick %d of %d hits; density %d %d %d\n", nseen,
               perc_on_kick, perc_hits, dens[0], dens[1], dens[2]);
        CHECK(nseen >= 195, "only %d different grooves in 200", nseen);
        CHECK(perc_on_kick * 6 <= perc_hits, "the percussion on the kick: %d of %d", perc_on_kick, perc_hits);
        CHECK(dens[0] && dens[1] && dens[2], "a density never chosen");
    }

    /* NEW tapped: the selected track alone, the other five as they were; UNDO brings the track back */
    {
        static romi_pattern_t before;
        int t2, k, changed_tr = 0;
        romi_init(77);
        tap_key(8);                                 /* PERC */
        before = romi_project()->pat[0];
        tap_key(22);                                /* NEW, tapped */
        for (t2 = 0; t2 < ROMI_TRACKS; t2++) {
            int same = !memcmp(&before.tr[t2], &romi_project()->pat[0].tr[t2], sizeof(romi_track_t));
            if (t2 != ROMI_PERC) CHECK(same, "NEW tapped changed track %d too", t2);
            else changed_tr = !same;
        }
        CHECK(changed_tr, "NEW tapped left the selected track as it was");
        tap_key(25);                                /* UNDO */
        CHECK(!memcmp(&before, &romi_project()->pat[0], sizeof before), "UNDO after NEW: not as before");
        held_k = 1u << 22;                          /* NEW held: every track */
        for (k = 0; k < 32; k++) frame(0);
        held_k = 0; frame(0);
        for (k = 0, t2 = 0; t2 < ROMI_TRACKS; t2++)
            k += !!memcmp(&before.tr[t2], &romi_project()->pat[0].tr[t2], sizeof(romi_track_t));
        CHECK(k >= 5, "NEW held changed only %d tracks", k);
        tap_key(25);
        CHECK(!memcmp(&before, &romi_project()->pat[0], sizeof before), "UNDO after NEW held: not as before");
    }

    /* LFOs: LFO opens LFO 1, again LFO 2, again LFO 1; the knobs set rate, depth, target, shape; a level LFO
     * (square, a bar) makes one half of the bar loud and the other quiet; a decay LFO changes the sound; both kept
     * by the store; off (depth 0) changes nothing */
    {
        static uint8_t obj[ROMI_OBJ_MAX];
        romi_track_t *hat;
        uint32_t n, h0, h1;
        double a, b2;
        int k;
        romi_init(55);
        romi_project()->drift = 0;
        for (k = 0; k < ROMI_TRACKS; k++)
            if (k != ROMI_HAT) romi_project()->pat[0].tr[k].mute = 1;
        hat = &romi_project()->pat[0].tr[ROMI_HAT];
        for (k = 0; k < 16; k++) { hat->step[k].flags = 0xC0; hat->step[k].note = 0; }   /* every step, accented */
        hat->len = 16; hat->dly = hat->rev = 0;
        tap_button(ROMI_B_PLAY);
        h0 = run(4 * 60.0 / 126 * 2, 0, 0, 0);       /* two bars, no LFO */
        tap_button(ROMI_B_PLAY);
        tap_key(5);                                 /* HAT */
        tap_button(ROMI_B_LFO);
        CHECK(romi_state(ROMI_Q_LFO_PAGE) == 1, "LFO: page %d", romi_state(ROMI_Q_LFO_PAGE));
        tap_button(ROMI_B_LFO);
        CHECK(romi_state(ROMI_Q_LFO_PAGE) == 2, "LFO twice: page %d", romi_state(ROMI_Q_LFO_PAGE));
        tap_button(ROMI_B_LFO);
        CHECK(romi_state(ROMI_Q_LFO_PAGE) == 1, "LFO three times: page %d", romi_state(ROMI_Q_LFO_PAGE));
        turn(ROMI_E_K1, 20); turn(ROMI_E_K1, -4);   /* rate: 1 bar */
        turn(ROMI_E_K2, -40);                       /* depth: -64 */
        turn(ROMI_E_K3, -10); turn(ROMI_E_K3, 4);   /* target: level */
        turn(ROMI_E_K4, 3);                         /* shape: square */
        CHECK(hat->lfo[0].rate == 4 && hat->lfo[0].depth == -64 && hat->lfo[0].target == 4 && hat->lfo[0].shape == 3,
              "LFO 1: rate %d depth %d target %d shape %d", hat->lfo[0].rate, hat->lfo[0].depth, hat->lfo[0].target,
              hat->lfo[0].shape);
        snprintf(path, sizeof path, "%s/screen-lfo.ppm", out);
        write_screen(path);
        tap_button(ROMI_B_PLAY);
        run(4 * 60.0 / 126 / 2, 0, 0, &a);          /* the first half bar: square at +1, depth -64: quiet */
        run(4 * 60.0 / 126 / 2, 0, 0, &b2);         /* the second: loud */
        tap_button(ROMI_B_PLAY);
        printf("lfo: level square, half bars rms %.4f and %.4f\n", a, b2);
        CHECK(a < b2 * 0.7, "a level LFO did nothing: %.4f %.4f", a, b2);
        n = romi_store_get(1, obj, sizeof obj);
        CHECK(n <= ROMI_OBJ_MAX, "pattern object %u bytes", n);
        romi_init(56);
        CHECK(romi_store_set(1, obj, n) == 0, "LFOs: did not load");
        hat = &romi_project()->pat[0].tr[ROMI_HAT];
        CHECK(hat->lfo[0].rate == 4 && hat->lfo[0].depth == -64 && hat->lfo[0].target == 4 && hat->lfo[0].shape == 3,
              "LFO after load: %d %d %d %d", hat->lfo[0].rate, hat->lfo[0].depth, hat->lfo[0].target, hat->lfo[0].shape);
        /* a decay LFO, heard */
        hat->lfo[0].target = 0; hat->lfo[0].depth = 50; hat->lfo[0].shape = 1;
        romi_project()->drift = 0;
        for (k = 0; k < ROMI_TRACKS; k++)
            romi_project()->pat[0].tr[k].mute = (uint8_t)(k != ROMI_HAT);
        tap_button(ROMI_B_PLAY);
        h1 = run(4 * 60.0 / 126 * 2, 0, 0, 0);
        tap_button(ROMI_B_PLAY);
        CHECK(h0 != h1, "a decay LFO changed nothing");
    }

    /* SEL held + track keys: each mutes its own track, the selection stays; letting go adds no mute or solo;
     * pressed again under SEL, a track plays again; a long hold alone is still solo */
    {
        int k;
        romi_init(88);
        tap_key(8);                                 /* PERC selected */
        held_b = 1u << ROMI_B_SEL;
        for (k = 0; k < 40; k++) frame(0);         /* longer than a solo's hold */
        tap_key(1);                                 /* KICK */
        tap_key(5);                                 /* HAT */
        held_k = (1u << 3) | (1u << 10); frame(0); held_k = 0; frame(0);   /* SUB and STAB at once */
        held_b = 0; frame(0);
        CHECK(romi_project()->pat[0].tr[ROMI_KICK].mute && romi_project()->pat[0].tr[ROMI_HAT].mute &&
              romi_project()->pat[0].tr[ROMI_SUB].mute && romi_project()->pat[0].tr[ROMI_STAB].mute,
              "SEL + track keys: mutes %d %d %d %d", romi_project()->pat[0].tr[ROMI_KICK].mute,
              romi_project()->pat[0].tr[ROMI_HAT].mute, romi_project()->pat[0].tr[ROMI_SUB].mute,
              romi_project()->pat[0].tr[ROMI_STAB].mute);
        CHECK(romi_state(ROMI_Q_TRACK) == ROMI_PERC && !romi_project()->pat[0].tr[ROMI_PERC].mute &&
              !romi_project()->pat[0].tr[ROMI_CLICK].mute && romi_state(ROMI_Q_SOLO) == -1,
              "SEL + track keys: track %d perc mute %d solo %d", romi_state(ROMI_Q_TRACK),
              romi_project()->pat[0].tr[ROMI_PERC].mute, romi_state(ROMI_Q_SOLO));
        held_b = 1u << ROMI_B_SEL; frame(0);
        tap_key(1);                                 /* KICK plays again */
        held_b = 0; frame(0);
        CHECK(!romi_project()->pat[0].tr[ROMI_KICK].mute && romi_project()->pat[0].tr[ROMI_HAT].mute,
              "SEL + KICK again: kick %d hat %d", romi_project()->pat[0].tr[ROMI_KICK].mute,
              romi_project()->pat[0].tr[ROMI_HAT].mute);
        held_b = 1u << ROMI_B_SEL;
        for (k = 0; k < 40; k++) frame(0);
        held_b = 0; frame(0);
        CHECK(romi_state(ROMI_Q_SOLO) == ROMI_PERC, "SEL held alone: solo %d", romi_state(ROMI_Q_SOLO));
        tap_button(ROMI_B_SEL);
        CHECK(romi_project()->pat[0].tr[ROMI_PERC].mute, "SEL tapped: not muted");
    }

    /* SOUND 2: EDIT twice; PITCH moves the track's notes; DRIVE, CRUSH and ATTACK change the sound and stay
     * bounded; a step held on SOUND 2 takes locks there (kept by the store); an LFO can aim at them */
    {
        static uint8_t obj[ROMI_OBJ_MAX];
        romi_track_t *sub, *hat;
        uint32_t h_plain, h, n;
        int k, which;
        tap_button(ROMI_B_PLAY);                    /* (stopped) */
        romi_init(66);
        tap_button(ROMI_B_EDIT);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_SOUND, "EDIT: page %d", romi_state(ROMI_Q_PAGE));
        tap_button(ROMI_B_EDIT);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_SOUND2, "EDIT twice: page %d", romi_state(ROMI_Q_PAGE));
        snprintf(path, sizeof path, "%s/screen-sound2.ppm", out);
        write_screen(path);
        tap_button(ROMI_B_EDIT);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_SOUND, "EDIT three times: page %d", romi_state(ROMI_Q_PAGE));
        /* PITCH: the sub's notes, five up */
        sub = &romi_project()->pat[0].tr[ROMI_SUB];
        sub->follow = 0;
        for (k = 0; k < 16; k++) { sub->step[k].flags = (uint8_t)(k == 2 ? 0x80 : 0); sub->step[k].note = 3; }
        tap_key(3);                                 /* SUB */
        tap_button(ROMI_B_EDIT);                    /* (SOUND 2) */
        turn(ROMI_E_K1, 5);
        CHECK(sub->q[0] == 29, "PITCH +5: %d", sub->q[0]);
        tap_button(ROMI_B_PLAY);
        run(0.4, 0, 0, 0);
        tap_button(ROMI_B_PLAY);
        CHECK(romi_state(ROMI_Q_NOTE + ROMI_SUB) == 8, "PITCH +5 on a note 3: played %d",
              romi_state(ROMI_Q_NOTE + ROMI_SUB));
        /* DRIVE, CRUSH, ATTACK: each changes the hats, and the sound stays bounded */
        for (which = 0; which < 4; which++) {
            romi_init(67);
            romi_project()->drift = 0;
            for (k = 0; k < ROMI_TRACKS; k++) romi_project()->pat[0].tr[k].mute = (uint8_t)(k != ROMI_HAT);
            hat = &romi_project()->pat[0].tr[ROMI_HAT];
            if (which == 1) hat->q[2] = 110;        /* drive */
            if (which == 2) hat->q[3] = 100;        /* crush */
            if (which == 3) hat->q[1] = 90;         /* attack */
            tap_button(ROMI_B_PLAY);
            h = run(2.0, 0, &peak, &rms);
            tap_button(ROMI_B_PLAY);
            if (!which) h_plain = h;
            else CHECK(h != h_plain, "SOUND 2 %d changed nothing", which);
            CHECK(peak <= 1.0 && rms > 0.001, "SOUND 2 %d: peak %f rms %f", which, peak, rms);
        }
        /* a lock on SOUND 2 (the stab's DRIVE), kept by the store */
        romi_init(68);
        tap_key(10);                                /* STAB */
        tap_button(ROMI_B_EDIT); tap_button(ROMI_B_EDIT);
        held_k = 1u << 9; frame(0);                 /* step 6 */
        turn(ROMI_E_K3, 10);
        held_k = 0; frame(0); frame(0);
        CHECK(romi_project()->pat[0].tr[ROMI_STAB].step[5].lock[6] == 41 &&
              romi_project()->pat[0].tr[ROMI_STAB].q[2] == 0, "SOUND 2 lock: %d (track %d)",
              romi_project()->pat[0].tr[ROMI_STAB].step[5].lock[6], romi_project()->pat[0].tr[ROMI_STAB].q[2]);
        n = romi_store_get(1, obj, sizeof obj);
        romi_init(69);
        CHECK(romi_store_set(1, obj, n) == 0 && romi_project()->pat[0].tr[ROMI_STAB].step[5].lock[6] == 41,
              "SOUND 2 lock after load: %d", romi_project()->pat[0].tr[ROMI_STAB].step[5].lock[6]);
        /* an LFO aimed at SOUND 2 */
        tap_key(10);
        tap_button(ROMI_B_LFO);
        turn(ROMI_E_K3, 20);
        CHECK(romi_project()->pat[0].tr[ROMI_STAB].lfo[0].target == 11, "LFO target: %d",
              romi_project()->pat[0].tr[ROMI_STAB].lfo[0].target);
    }

    /* the variations: B, C, D made from A. Over many grooves and every scale: each differs from A; all keep the
     * kick on 0 and 4 (B may leave out 8 or 12, C may pause for the last four steps); B keeps A's harmony (its stab notes are A's, in another order), C rolls in its last
     * four hat steps, D is A's stab moved by its key step; an edit made while B plays goes to A and B follows;
     * NEW on B throws only B again; EVOLVE gives new B..D after a round; the store keeps only the settings and
     * A and makes B..D again from them */
    {
        static const uint8_t SC[4][7] = {{0, 2, 3, 5, 7, 8, 10}, {0, 2, 3, 5, 7, 9, 10}, {0, 1, 3, 5, 7, 8, 10},
                                         {0, 3, 5, 7, 10, 12, 15}};
        static romi_pattern_t keep_b, keep_c, keep_d;
        static uint8_t obj[ROMI_NOBJ][ROMI_OBJ_MAX];
        uint32_t len[ROMI_NOBJ];
        int g, k, t2, drops[3] = {0, 0, 0};
        for (g = 0; g < 80; g++) {
            const romi_pattern_t *pa, *pb, *pc2, *pd;
            int sa[16], sb2[16], na = 0, nb = 0, iv, sc = g % 4, m, j, ok;
            romi_init(12000u + (uint32_t)g * 37u);
            romi_project()->scale = (uint8_t)sc;
            held_k = 1u << 22; for (k = 0; k < 32; k++) frame(0); held_k = 0; frame(0);   /* a whole groove */
            pa = &romi_project()->pat[0]; pb = &romi_project()->pat[1];
            pc2 = &romi_project()->pat[2]; pd = &romi_project()->pat[3];
            CHECK(memcmp(pa, pb, sizeof *pa) && memcmp(pa, pc2, sizeof *pa) && memcmp(pa, pd, sizeof *pa),
                  "groove %d: a variation the same as A", g);
            for (t2 = 1; t2 < 4; t2++)              /* the kick: D four on the floor; B and C may sit out 8 or 12 */
                for (k = 0; k < 16; k += 4) {
                    int on = romi_project()->pat[t2].tr[ROMI_KICK].step[k].flags & ROMI_ST_ON;
                    if (!on && t2 < 3 && k >= 8) { drops[t2]++; continue; }
                    CHECK(on, "groove %d: pattern %c without the kick on %d", g, 'A' + t2, k);
                }
            if (!(pc2->tr[ROMI_KICK].step[12].flags & ROMI_ST_ON))   /* C's pause: the whole last four steps */
                for (k = 13; k < 16; k++)
                    CHECK(!(pc2->tr[ROMI_KICK].step[k].flags & ROMI_ST_ON), "groove %d: C's kick pause on %d", g, k);
            for (k = 0; k < 16; k++) {              /* B: the same chords, maybe in another order */
                if (pa->tr[ROMI_STAB].step[k].flags & ROMI_ST_ON) sa[na++] = pa->tr[ROMI_STAB].step[k].note;
                if (pb->tr[ROMI_STAB].step[k].flags & ROMI_ST_ON) sb2[nb++] = pb->tr[ROMI_STAB].step[k].note;
            }
            CHECK(na == nb, "groove %d: B has %d stab hits, A %d", g, nb, na);
            for (k = 0; k < na && na == nb; k++) {
                for (ok = 0, j = 0; j < nb; j++) ok |= sa[k] == sb2[j];
                CHECK(ok, "groove %d: B's stab has a chord A has not", g);
            }
            for (k = 12; k < 16; k++)               /* C: rolling hats */
                CHECK((pc2->tr[ROMI_HAT].step[k].flags & ROMI_ST_ON) && ROMI_ST_RATCH(pc2->tr[ROMI_HAT].step[k].flags) >= 2,
                      "groove %d: C without a roll on %d", g, k);
            iv = romi_state(ROMI_Q_KEY_STEP);       /* D: A's stab, moved by the key step */
            for (k = 0; k < 16; k++)
                if (pa->tr[ROMI_STAB].step[k].flags & ROMI_ST_ON) {
                    m = ((pd->tr[ROMI_STAB].step[k].note - pa->tr[ROMI_STAB].step[k].note - iv) % 12 + 12) % 12;
                    CHECK(m == 0, "groove %d: D's stab not moved by %d", g, iv);
                    m = ((pd->tr[ROMI_STAB].step[k].note - iv) % 12 + 12) % 12;
                    for (ok = 0, j = 0; j < 7; j++) ok |= SC[sc][j] % 12 == m;
                    CHECK(ok, "groove %d: D's note %d not in the scale moved by %d", g, pd->tr[ROMI_STAB].step[k].note, iv);
                }
            for (k = 0; k < 16; k++)                /* B and C: every melodic note in the scale */
                for (t2 = ROMI_PERC; t2 <= ROMI_STAB; t2++)
                    for (j = 1; j <= 2; j++) {
                        const romi_step_t *st = &romi_project()->pat[j].tr[t2].step[k];
                        int q, hit = 0;
                        if (!(st->flags & ROMI_ST_ON) || k >= romi_project()->pat[j].tr[t2].len) continue;
                        m = ((st->note % 12) + 12) % 12;
                        for (q = 0; q < 7; q++) hit |= SC[sc][q] % 12 == m;
                        CHECK(hit, "groove %d: pattern %c track %d note %d not in the scale", g, 'A' + j, t2, st->note);
                    }
        }
        CHECK(drops[1] > 5 && drops[1] < 60, "B left out a kick beat %d times in 80 grooves", drops[1]);
        CHECK(drops[2] > 20 && drops[2] < 70, "C paused the kick %d times in 80 grooves", drops[2]);
        /* an edit while B plays goes to A, and B follows */
        romi_init(13);
        turn(ROMI_E_PRESET, 1);
        CHECK(romi_state(ROMI_Q_PATTERN) == 1, "PRESETS: pattern %d", romi_state(ROMI_Q_PATTERN));
        tap_button(ROMI_B_ENV);
        turn(ROMI_E_K1, -5);                        /* the kick's level, on B: 120 - 5 x 4 (a fast turn) */
        CHECK(romi_project()->pat[0].tr[ROMI_KICK].level == 100 && romi_project()->pat[1].tr[ROMI_KICK].level == 100 &&
              romi_project()->pat[3].tr[ROMI_KICK].level == 100, "an edit on B: A %d B %d D %d",
              romi_project()->pat[0].tr[ROMI_KICK].level, romi_project()->pat[1].tr[ROMI_KICK].level,
              romi_project()->pat[3].tr[ROMI_KICK].level);
        /* NEW on B: B again, A, C and D as they were */
        keep_c = romi_project()->pat[2]; keep_d = romi_project()->pat[3]; keep_b = romi_project()->pat[1];
        {
            static romi_pattern_t keep_a;
            keep_a = romi_project()->pat[0];
            tap_key(22);
            CHECK(!memcmp(&keep_a, &romi_project()->pat[0], sizeof keep_a), "NEW on B changed A");
        }
        CHECK(memcmp(&keep_b, &romi_project()->pat[1], sizeof keep_b), "NEW on B: B the same");
        CHECK(!memcmp(&keep_c, &romi_project()->pat[2], sizeof keep_c) &&
              !memcmp(&keep_d, &romi_project()->pat[3], sizeof keep_d), "NEW on B changed C or D");
        /* the store: the settings and A make B..D again, the same */
        turn(ROMI_E_PRESET, -1);
        tap_button(ROMI_B_SAVE);
        CHECK(romi_save_wanted() == 3u, "save: not the settings and A");
        for (k = 0; k < ROMI_NOBJ; k++) len[k] = romi_store_get(k, obj[k], sizeof obj[k]);
        keep_b = romi_project()->pat[1]; keep_c = romi_project()->pat[2]; keep_d = romi_project()->pat[3];
        romi_init(14);
        CHECK(romi_store_set(0, obj[0], len[0]) == 0 && romi_store_set(1, obj[1], len[1]) == 0, "load");
        CHECK(!memcmp(&keep_b, &romi_project()->pat[1], sizeof keep_b) && !memcmp(&keep_c, &romi_project()->pat[2],
              sizeof keep_c) && !memcmp(&keep_d, &romi_project()->pat[3], sizeof keep_d), "B..D not made again the same");
        /* EVOLVE: after a round A-D, new B..D */
        romi_init(15);
        romi_project()->chain = 4;
        keep_b = romi_project()->pat[1];
        tap_button(ROMI_B_PLAY);
        for (k = 0; k < 16 * 16 + 8; k++) {         /* a little over four times four bars, a frame a step */
            int g0 = romi_state(ROMI_Q_GSTEP);
            while (romi_state(ROMI_Q_GSTEP) == g0) run(0.01, 0, 0, 0);
            frame(0);
        }
        tap_button(ROMI_B_PLAY);
        CHECK(memcmp(&keep_b, &romi_project()->pat[1], sizeof keep_b), "EVOLVE: B the same after a round");
    }

    /* LAZY and HARD (GLOBAL 2): HARD makes B..D copies of A, edits and NEW go to the pattern playing, all five
     * objects are saved; back in LAZY B..D are made from A again and the HARD ones wait aside */
    {
        static romi_pattern_t keep_a, keep_b, hard_b;
        static uint8_t obj[ROMI_NOBJ][ROMI_OBJ_MAX];
        uint32_t len[ROMI_NOBJ];
        int k;
        romi_init(21);
        tap_button(ROMI_B_GLO); tap_button(ROMI_B_GLO);
        CHECK(romi_state(ROMI_Q_PAGE) == ROMI_PG_GLOBAL2, "GLO twice: page %d", romi_state(ROMI_Q_PAGE));
        turn(ROMI_E_K1, 1);
        CHECK(romi_project()->mode == 1, "MODE: %d", romi_project()->mode);
        for (k = 1; k < 4; k++)
            CHECK(!memcmp(&romi_project()->pat[0], &romi_project()->pat[k], sizeof keep_a), "HARD: %c not A", 'A' + k);
        keep_a = romi_project()->pat[0];
        turn(ROMI_E_PRESET, 1);                     /* on B */
        tap_button(ROMI_B_ENV);
        turn(ROMI_E_K1, -5);
        CHECK(romi_project()->pat[1].tr[ROMI_KICK].level == 100 && romi_project()->pat[0].tr[ROMI_KICK].level == 120,
              "HARD edit on B: A %d B %d", romi_project()->pat[0].tr[ROMI_KICK].level, romi_project()->pat[1].tr[ROMI_KICK].level);
        keep_b = romi_project()->pat[1];
        tap_key(22);                                /* NEW: B's current track, only B */
        CHECK(!memcmp(&keep_a, &romi_project()->pat[0], sizeof keep_a), "HARD NEW on B changed A");
        CHECK(memcmp(&keep_b, &romi_project()->pat[1], sizeof keep_b), "HARD NEW on B: B the same");
        hard_b = romi_project()->pat[1];
        tap_button(ROMI_B_SAVE);
        CHECK(romi_save_wanted() == 0x1fu, "HARD save: %x", romi_save_wanted());
        for (k = 0; k < ROMI_NOBJ; k++) len[k] = romi_store_get(k, obj[k], sizeof obj[k]);
        romi_init(22);
        for (k = 0; k < ROMI_NOBJ; k++) CHECK(romi_store_set(k, obj[k], len[k]) == 0, "HARD load %d", k);
        CHECK(romi_project()->mode == 1 && !memcmp(&hard_b, &romi_project()->pat[1], sizeof hard_b), "HARD: B not loaded");
        /* back to LAZY: B made from A; then HARD again: the HARD B is back */
        tap_button(ROMI_B_GLO); tap_button(ROMI_B_GLO);
        turn(ROMI_E_K1, -1);
        CHECK(romi_project()->mode == 0 && memcmp(&hard_b, &romi_project()->pat[1], sizeof hard_b), "LAZY: B not made from A");
        tap_button(ROMI_B_SAVE);
        { uint32_t w = romi_save_wanted(); CHECK(w == 1u, "LAZY save: %x (the settings only: A as loaded, B..D not kept)", w); }
        turn(ROMI_E_K1, 1);
        CHECK(!memcmp(&hard_b, &romi_project()->pat[1], sizeof hard_b), "HARD again: B lost");
        /* loaded in LAZY, the HARD patterns wait aside */
        romi_init(23);
        romi_project()->mode = 0;
        CHECK(romi_store_set(2, obj[2], len[2]) == 0, "LAZY load of B");
        CHECK(memcmp(&hard_b, &romi_project()->pat[1], sizeof hard_b), "LAZY: the loaded B plays");
        tap_button(ROMI_B_GLO); tap_button(ROMI_B_GLO);
        turn(ROMI_E_K1, 1);
        CHECK(!memcmp(&hard_b, &romi_project()->pat[1], sizeof hard_b), "HARD: the B kept aside not back");
    }

    /* PLAY on GLOBAL 2: LOOP stays on its pattern, A-D goes round, RANDOM picks another every four bars */
    {
        int o, k, seen[3][4] = {{0}}, order[8], no, same = 0;
        for (o = 0; o < 3; o++) {
            romi_init(31u + (uint32_t)o);
            tap_button(ROMI_B_GLO); tap_button(ROMI_B_GLO);
            turn(ROMI_E_K2, o);
            CHECK(romi_project()->order == o, "PLAY %d: %d", o, romi_project()->order);
            tap_button(ROMI_B_PLAY);
            for (no = 0, k = 0; k < 64 * 24 + 8; k++) {
                int g0 = romi_state(ROMI_Q_GSTEP), pnow;
                while (romi_state(ROMI_Q_GSTEP) == g0) run(0.01, 0, 0, 0);
                frame(0);
                pnow = romi_state(ROMI_Q_PATTERN);
                seen[o][pnow]++;
                if ((k & 63) == 32) {           /* the middle of each four bars */
                    if (no && order[(no - 1) & 7] == pnow && o == 2) same++;
                    order[no++ & 7] = pnow;
                    if (o == 1) CHECK(pnow == (no - 1) % 4, "PLAY A-D: %d after %d rounds", pnow, no - 1);
                }
            }
            tap_button(ROMI_B_PLAY);
        }
        CHECK(seen[0][0] && !seen[0][1] && !seen[0][2] && !seen[0][3], "PLAY LOOP left A");
        CHECK(seen[2][0] && seen[2][1] && seen[2][2] && seen[2][3] && !same, "PLAY RANDOM: %d %d %d %d, %d repeats",
              seen[2][0], seen[2][1], seen[2][2], seen[2][3], same);
    }

    /* MIDI: channel 1 plays the kick */
    romi_init(3);
    romi_midi_note(0, 60, 127);
    run(0.2, 0, &peak, 0);
    CHECK(peak > 0.2, "MIDI note: peak %f", peak);

    printf(fails ? "%d FAILED\n" : "all tests passed\n", fails);
    return fails != 0;
}
