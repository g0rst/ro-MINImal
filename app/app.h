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
#define APP_STORE_MAP {0xFC000u, 0xDC000u, 0xD4000u, 0xD6000u, 0xD8000u, 0xDA000u}   /* two 4 KiB sectors each */

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
