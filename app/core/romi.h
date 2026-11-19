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

enum { ROMI_PG_HOME, ROMI_PG_SOUND, ROMI_PG_MIX, ROMI_PG_FX, ROMI_PG_GLOBAL, ROMI_PG_EUCLID, ROMI_PG_SC, ROMI_PG_LINK,
       ROMI_PG_TIMING, ROMI_PG_LFO1, ROMI_PG_LFO2, ROMI_PG_SOUND2, ROMI_PG_GLOBAL2, ROMI_NPAGES };

/* step flags */
#define ROMI_ST_ON 0x80u
#define ROMI_ST_ACC 0x40u
#define ROMI_CHANCE(st) ((st)->chance ? (st)->chance : 100u)   /* a step's chance in %, 1..100 (0 stored: sure) */
#define ROMI_ST_RATCH(f) (((f) & 3u) + 1u)  /* 1..4 hits within the step */

typedef struct {
    uint8_t flags;
    int8_t note;                        /* semitones from the track's base note, -32..31 */
    int8_t shift;                       /* microtiming, -7..7: sixteenths of a step early or late */
    uint8_t lock[8];                    /* a sound parameter for this step alone: 0 none, else value + 1
                                         * (0..3 the SOUND page's, 4..7 the SOUND 2 page's) */
    uint8_t chance;                     /* 1..100 %: how likely it plays, stepless; 0 = 100 % (a plain step) */
} romi_step_t;

/* an LFO: a slow wave in time with the groove, added to one of the track's values */
typedef struct {
    uint8_t rate;                       /* 0..8: 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 8, 16 bars a cycle */
    int8_t depth;                       /* -64..63: how far it moves the value (0..127), either way */
    uint8_t target;                     /* 0..3 the sound's parameters, 4 level, 5 pan, 6 delay send, 7 reverb send,
                                         * 8..11 the SOUND 2 parameters */
    uint8_t shape;                      /* 0 sine, 1 triangle, 2 saw down, 3 square, 4 random (a new value a cycle) */
} romi_lfo_t;
#define ROMI_LFOS 2

typedef struct {
    romi_step_t step[ROMI_STEPS];
    uint8_t len;                        /* 1..16: each track loops on its own length (polymetre) */
    uint8_t mute;
    uint8_t p[4];                       /* the sound's four parameters, 0..127 */
    uint8_t q[4];                       /* SOUND 2: pitch (0..48, 24 = none), then per track: kick click, sub FM
                                         * time, perc bend time, else attack; drive (kick: pitch time); crush */
    uint8_t level, pan, dly, rev;       /* 0..127 */
    uint8_t eu_hits, eu_rot;            /* the EUCLID page: hits spread over the loop, rotated */
    uint8_t eu_prob;                    /* 0..3: 25, 50, 75, 100 % for all of them */
    uint8_t eu_acc;                     /* 0: none; n: every n-th hit accented */
    uint8_t sc;                         /* 0..127: how much the sidechain ducks this track */
    uint8_t dep_src;                    /* the LINK page: 0 none, else track + 1 whose hits gate this track's steps */
    int8_t tshift;                      /* microtiming of the whole track, -8..8, added to each step's shift */
    uint8_t dep_mode;                   /* 0 WITH: only on its hits; 1 GAPS: only where it is silent; 2 AFTER: a step later */
    uint8_t follow;                     /* 0 none, else track + 1 whose notes transpose this track's (its harmony) */
    uint16_t slide;                     /* sub and stab: bit i, step i slides from the note before (no new attack) */
    uint8_t glide;                      /* stab: 0..127, how long its chords glide when they overlap (the sub's is p3) */
    romi_lfo_t lfo[ROMI_LFOS];
} romi_track_t;

typedef struct {
    romi_track_t tr[ROMI_TRACKS];
} romi_pattern_t;

typedef struct {
    uint8_t bpm;                        /* 90..150 */
    uint8_t swing;                      /* 50..75 % */
    uint8_t drift;                      /* 0..127: slow random movement of timbre, level and timing */
    uint8_t duck;                       /* 0..127: the sidechain's depth */
    uint8_t root;                       /* MIDI note of the sub's root, 24..47 */
    uint8_t scale;                      /* 0..3 */
    uint8_t dly_time;                   /* 0: 1/16, 1: 1/8, 2: 3/16 */
    uint8_t dly_fb, rev_size, rev_damp; /* 0..127 */
    uint8_t clock_out;                  /* MIDI clock and start / stop out */
    uint8_t cur_pat;
    uint8_t chain;                      /* 0: off; 1..3: patterns A-B, A-C, A-D in turn, four bars each;
                                         * 4: EVOLVE, A-D and new variations of B-D after each round */
    uint16_t var_seed[3];               /* the variations B, C, D of A: each one's dice */
    uint8_t order;                      /* 0 LOOP (CHAIN decides), 1 A-D and round again, 2 RANDOM; four bars each */
    uint8_t mode;                       /* 0 LAZY: B..D are made from A; 1 HARD: four patterns of their own */
    uint8_t sc_src;                     /* the track whose hits duck the others (muted, it still does) */
    uint8_t sc_rel;                     /* 0..127: how fast the ducking lets go */
    romi_pattern_t pat[ROMI_PATTERNS];
} romi_project_t;

/* What is kept is not this struct but packed objects (romi.c, "store"): the settings, and each pattern on its own,
 * steps in two bytes and the locks as a list. Hence these limits, which every edit keeps to: */
#define ROMI_MAX_LOCKS 32               /* per pattern */
#define ROMI_SHIFT_MAX 7                /* a step's own shift (the track's: 8) */
#define ROMI_NOTE_MIN (-32)
#define ROMI_NOTE_MAX 31
#define ROMI_VERSION 14u
#define ROMI_NOBJ (1 + ROMI_PATTERNS)   /* object 0: the settings; 1..4: patterns A..D. In LAZY mode only 0 and
                                         * 1 are saved (B..D are made from A); in HARD all five. In LAZY, objects
                                         * 2..4 load aside: the HARD patterns, back when HARD is chosen again */
#define ROMI_OBJ_MAX 600u               /* the largest packed object, in bytes */

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

/* ---- the project, for the platform's storage: ROMI_NOBJ objects, each saved and loaded on its own ---- */
uint32_t romi_store_get(int obj, void *dst, uint32_t max);   /* the object packed: its bytes (0: too small) */
int romi_store_set(int obj, const void *src, uint32_t len);  /* 0 = loaded; else this object is left as it was */
/* once after SAVE: bit k, object k changed since it was last loaded or saved (0: nothing to write). The platform
 * writes those, calling romi_store_saved(k) for each one written */
uint32_t romi_save_wanted(void);
void romi_store_saved(int obj);

/* ---- for tests and the simulator ---- */
int romi_state(int what);
enum { ROMI_Q_PLAYING, ROMI_Q_TRACK, ROMI_Q_PAGE, ROMI_Q_BPM, ROMI_Q_GSTEP, ROMI_Q_PATTERN, ROMI_Q_KEYS_MODE,
       ROMI_Q_LEN, ROMI_Q_STEPS_ON, ROMI_Q_MUTE, ROMI_Q_UNSAVED, ROMI_Q_POS, ROMI_Q_SOLO, ROMI_Q_CURSOR, ROMI_Q_DENSITY, ROMI_Q_LFO_PAGE, ROMI_Q_KEY_STEP,
       ROMI_Q_HITS = 100,              /* + track: hits sounded since PLAY */
       ROMI_Q_NOTE = 110 };            /* + track: the note of its last hit, as played (semitones from its base) */
romi_project_t *romi_project(void);

#endif
