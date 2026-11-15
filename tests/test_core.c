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

    /* MIDI: channel 1 plays the kick */
    romi_init(3);
    romi_midi_note(0, 60, 127);
    run(0.2, 0, &peak, 0);
    CHECK(peak > 0.2, "MIDI note: peak %f", peak);

    printf(fails ? "%d FAILED\n" : "all tests passed\n", fails);
    return fails != 0;
}
