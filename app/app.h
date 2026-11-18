/* SPDX-License-Identifier: MIT
 * ro:MINImal on the M-VAVE FM-1: the app's half of the contract with fm1-base (base/device/unity.c on the FM-1,
 * base/host/plat_host.c in the host simulator). The instrument itself is core/romi.c. */
#pragma once
#include <stdint.h>
#include "plat.h"

#define APP_NAME "ro:MINImal"
#define APP_TAGLINE "rominimal + microhouse"
#define APP_SPLASH_RGB RGB(255, 98, 44)
#define APP_BLOCK 256u                   /* frames per audio block: 5.8 ms */

/* the store: the settings, each pattern on its own (about 400 bytes packed: core/romi.c "store"), and the
 * platform's panel calibration */
enum { OBJ_SETTINGS, OBJ_PANEL, OBJ_PAT_A, OBJ_PAT_B, OBJ_PAT_C, OBJ_PAT_D, OBJ_NOBJ };
/* Where they live: two 4 KiB sectors (A/B) each. ro:MINImal's own five objects sit in 0xB1000..0xBAFFF, a range
 * that is safe on both boards: on the FM-1 inside fm1-base's data area (0x97000..0xDFFFF, clear of the update's
 * staging at 0xE0000 and of Felucca's settings at 0xFC000), and on the SMK-37 inside the store window the porting
 * playbook gives a firmware's extra objects (genkigenki/fm1-to-smk37 AGENTS.md, step 3), clear of every range it
 * protects. app.c checks all of it at compile time (the flash map asserts); never move an object without them. */
#define ROMI_ADDR_SETTINGS 0xB1000u
#define ROMI_ADDR_PAT_A 0xB3000u
#define ROMI_ADDR_PAT_B 0xB5000u
#define ROMI_ADDR_PAT_C 0xB7000u
#define ROMI_ADDR_PAT_D 0xB9000u
#if defined BOARD_SMK37 && BOARD_SMK37
/* The panel calibration is the platform's object; on the SMK-37 the board layer decides its place (and reads the
 * factory calibration at 0xC1000 without ever writing it). Until that layer exists, no SMK-37 build. */
#error "ro:MINImal: no SMK-37 board layer yet: OBJ_PANEL's place on the SMK-37 is not decided (smk37-port.yaml)"
#endif
#define ROMI_ADDR_PANEL 0xDC000u        /* FM-1: the platform's panel calibration, where fm1-base's template has it */
#define APP_STORE_MAP {ROMI_ADDR_SETTINGS, ROMI_ADDR_PANEL, ROMI_ADDR_PAT_A, ROMI_ADDR_PAT_B, ROMI_ADDR_PAT_C, \
                       ROMI_ADDR_PAT_D}

/* the contract: the platform calls these */
void app_init(void);
void app_render(int32_t *lr, uint32_t n, uint32_t master_q12);
void app_panic(void);
void app_ui_init(void);
void app_frame(void);
void app_input_only(void);
void app_say(const char *a, const char *b);

/* the host simulator's checks (app/tests/basic.txt) */
#define APP_HOST_EXPECT
int app_expect(const char *what, int *got);
