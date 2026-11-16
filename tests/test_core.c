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
    static uint8_t saved[4096], saved2[4096];
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
    tap_button(ROMI_B_LFO);
    CHECK(romi_state(ROMI_Q_MUTE) == 1, "mute");
    tap_button(ROMI_B_LFO);
    tap_button(ROMI_B_SEL);
    CHECK(romi_state(ROMI_Q_STEPS_ON) > 0, "generate made nothing");
    snprintf(path, sizeof path, "%s/screen-fx.ppm", out);
    write_screen(path);
    held_k = 1u << 0; frame(0);
    snprintf(path, sizeof path, "%s/screen-step.ppm", out);
    write_screen(path);
    held_k = 0; frame(0);
    tap_key(0);                                     /* (put step 1 back as it was) */

    /* the project: saved, damaged copies refused, loaded back the same */
    CHECK(romi_state(ROMI_Q_UNSAVED) == 1, "not marked unsaved");
    tap_button(ROMI_B_SAVE);
    CHECK(romi_save_wanted() == 1 && romi_save_wanted() == 0, "save request");
    n = romi_project_get(saved, sizeof saved);
    CHECK(n == sizeof(romi_project_t) && n <= 3840, "project size %u", n);
    printf("project: %u bytes\n", n);
    romi_init(31337);
    saved[40] ^= 1;
    CHECK(romi_project_set(saved, n) != 0, "a damaged project loaded");
    saved[40] ^= 1;
    CHECK(romi_project_set(saved, n - 1) != 0, "a short project loaded");
    CHECK(romi_project_set(saved, n) == 0, "the project did not load");
    CHECK(romi_state(ROMI_Q_BPM) == 120, "bpm after load %d", romi_state(ROMI_Q_BPM));
    CHECK(romi_project_get(saved2, sizeof saved2) == n && !memcmp(saved, saved2, n), "load and save differ");

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
    held_b = 1u << ROMI_B_LFO;
    for (i = 0; i < 40; i++) frame(0);
    held_b = 0; frame(0);
    CHECK(romi_state(ROMI_Q_SOLO) == 0 && romi_state(ROMI_Q_MUTE) == 0, "solo %d mute %d", romi_state(ROMI_Q_SOLO), romi_state(ROMI_Q_MUTE));
    tap_button(ROMI_B_PLAY);
    run(4.0, 0, &peak, &rms);
    CHECK(peak > 0.2, "the solo kick is silent: %f", peak);
    held_b = 1u << ROMI_B_LFO;
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

    /* SAVE held: PRESETS copies the pattern, SELECT the track; a tap still saves */
    romi_init(22);
    romi_save_wanted();
    held_b = 1u << ROMI_B_SAVE; frame(0);
    turn(ROMI_E_PRESET, 2);
    held_b = 0; frame(0);
    CHECK(!memcmp(&romi_project()->pat[0], &romi_project()->pat[2], sizeof(romi_pattern_t)), "pattern A not copied to C");
    CHECK(romi_state(ROMI_Q_PATTERN) == 0 && romi_save_wanted() == 0, "a copy changed the pattern or saved");
    CHECK(memcmp(&romi_project()->pat[0].tr[1], &romi_project()->pat[3].tr[1], sizeof(romi_track_t)), "D is A already");
    tap_key(3);                                     /* SUB */
    held_b = 1u << ROMI_B_SAVE; frame(0);
    turn(ROMI_E_SELECT, 3);
    held_b = 0; frame(0);
    CHECK(romi_state(ROMI_Q_TRACK) == ROMI_SUB, "SELECT under SAVE moved the track");
    CHECK(!memcmp(&romi_project()->pat[0].tr[1], &romi_project()->pat[3].tr[1], sizeof(romi_track_t)), "track not copied to D");
    CHECK(memcmp(&romi_project()->pat[0].tr[2], &romi_project()->pat[3].tr[2], sizeof(romi_track_t)), "more than the track was copied");
    tap_button(ROMI_B_SAVE);
    CHECK(romi_save_wanted() == 1, "a tap on SAVE did not save");

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
    for (v = -8; v <= 8; v += 8) {
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
        CHECK(tr->step[2].shift == -3 && tr->step[11].shift == 5 && tr->step[5].shift == 8 && tr->tshift == -2,
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

    /* MIDI: channel 1 plays the kick */
    romi_init(3);
    romi_midi_note(0, 60, 127);
    run(0.2, 0, &peak, 0);
    CHECK(peak > 0.2, "MIDI note: peak %f", peak);

    printf(fails ? "%d FAILED\n" : "all tests passed\n", fails);
    return fails != 0;
}
