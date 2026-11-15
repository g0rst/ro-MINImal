/* SPDX-License-Identifier: MIT
 * ro:MINImal -- a rominimal / microhouse groove engine for the M-VAVE FM-1.
 *
 * The core is portable C99 with no libc and no platform calls: the same file runs on the FM-1 (app/app.c, on
 * fm1-base), in the browser test page (sim/, WebAssembly) and in the host tests (tests/).
 *
 * Threads: romi_render and romi_midi_note run in the audio context; everything else in the main loop.
 */
#ifndef ROMI_CORE_H
#define ROMI_CORE_H
#include <stdint.h>

#define ROMI_SR 44100
#define ROMI_TRACKS 6
#define ROMI_STEPS 16
#define ROMI_PATTERNS 4
#define ROMI_W 240
#define ROMI_H 240
#define ROMI_STRIP_H 48                 /* the screen is redrawn in 5 strips of 48 rows */
#define ROMI_STRIPS (ROMI_H / ROMI_STRIP_H)
#define ROMI_NKEYS 27                   /* F3 .. G5 */

enum { ROMI_KICK, ROMI_SUB, ROMI_HAT, ROMI_PERC, ROMI_STAB, ROMI_CLICK };

/* panel controls, in fm1-base's order (plat.h); app.c asserts they match */
enum { ROMI_B_FX, ROMI_B_SEL, ROMI_B_ENV, ROMI_B_LFO, ROMI_B_EDIT, ROMI_B_GLO, ROMI_B_HOME, ROMI_B_SAVE,
       ROMI_B_ARP, ROMI_B_SEQ, ROMI_B_PLAY, ROMI_B_REC, ROMI_B_OCTDN, ROMI_B_OCTUP, ROMI_NB };
enum { ROMI_E_SELECT, ROMI_E_ALGO, ROMI_E_PRESET, ROMI_E_K1, ROMI_E_K2, ROMI_E_K3, ROMI_E_K4, ROMI_NE };

enum { ROMI_PG_HOME, ROMI_PG_SOUND, ROMI_PG_MIX, ROMI_PG_FX, ROMI_PG_GLOBAL, ROMI_NPAGES };

/* step flags */
#define ROMI_ST_ON 0x80u
#define ROMI_ST_ACC 0x40u
#define ROMI_ST_PROB(f) (((f) >> 4) & 3u)   /* 0: 100 %, 1: 75 %, 2: 50 %, 3: 25 % */

typedef struct {
    uint8_t flags;
    int8_t note;                        /* semitones from the track's base note */
} romi_step_t;

typedef struct {
    romi_step_t step[ROMI_STEPS];
    uint8_t len;                        /* 1..16: each track loops on its own length (polymetre) */
    uint8_t mute;
    uint8_t p[4];                       /* the sound's four parameters, 0..127 */
    uint8_t level, pan, dly, rev;       /* 0..127 */
} romi_track_t;

typedef struct {
    romi_track_t tr[ROMI_TRACKS];
} romi_pattern_t;

typedef struct {
    uint32_t magic;                     /* ROMI_MAGIC */
    uint16_t version, size;
    uint8_t bpm;                        /* 90..150 */
    uint8_t swing;                      /* 50..75 % */
    uint8_t drift;                      /* 0..127: slow random movement of timbre, level and timing */
    uint8_t duck;                       /* 0..127: the kick ducks everything else */
    uint8_t root;                       /* MIDI note of the sub's root, 24..47 */
    uint8_t scale;                      /* 0..3 */
    uint8_t dly_time;                   /* 0: 1/16, 1: 1/8, 2: 3/16 */
    uint8_t dly_fb, rev_size, rev_damp; /* 0..127 */
    uint8_t clock_out;                  /* MIDI clock and start / stop out */
    uint8_t cur_pat;
    romi_pattern_t pat[ROMI_PATTERNS];
    uint32_t sum;                       /* over everything before it */
} romi_project_t;

#define ROMI_MAGIC 0x314D4F52u          /* "ROM1" */
#define ROMI_VERSION 1u

/* ---- life cycle ---- */
void romi_init(uint32_t seed);          /* tables, defaults and a first groove generated from seed */
void romi_panic(void);                  /* silence now */

/* ---- audio context ---- */
/* n stereo frames of signed 24-bit samples (Q23 in int32), at gain_q12 (0..4096) */
void romi_render(int32_t *lr, uint32_t n, uint32_t gain_q12);
/* a MIDI note: channels 1..6 play the tracks (note 60 = the step's base note), channel 10 a drum map */
void romi_midi_note(uint32_t channel, uint32_t note, uint32_t velocity);
void romi_midi_transport(int start);    /* MIDI start / stop in */
int romi_midi_rt_pop(void);             /* a real-time byte to send (0xF8, 0xFA, 0xFC), or -1 */

/* ---- main loop ---- */
/* the panel as it is now: held buttons (bit ROMI_B_*), held keys (bit k), detents since the last call */
void romi_input(uint32_t buttons, uint32_t keys, const int32_t enc[ROMI_NE], uint32_t now_ms);
uint32_t romi_dirty(void);              /* bit s: strip s must be drawn again (cleared by the call) */
void romi_draw(uint16_t *px, int strip);   /* strip's 240 x 48 pixels, RGB565 */
void romi_lights(uint32_t *buttons, uint32_t *keys, uint32_t *dim_buttons, uint32_t *dim_keys);
void romi_message(const char *a, const char *b);

/* ---- the project, for the platform's storage ---- */
uint32_t romi_project_get(void *dst, uint32_t max);       /* bytes written (0: too small) */
int romi_project_set(const void *src, uint32_t len);      /* 0 = loaded; else nothing changed */
int romi_save_wanted(void);             /* 1 once after SAVE: the platform writes the project */

/* ---- for tests and the simulator ---- */
int romi_state(int what);
enum { ROMI_Q_PLAYING, ROMI_Q_TRACK, ROMI_Q_PAGE, ROMI_Q_BPM, ROMI_Q_GSTEP, ROMI_Q_PATTERN, ROMI_Q_KEYS_MODE,
       ROMI_Q_LEN, ROMI_Q_STEPS_ON, ROMI_Q_MUTE, ROMI_Q_UNSAVED, ROMI_Q_POS };
romi_project_t *romi_project(void);

#endif
