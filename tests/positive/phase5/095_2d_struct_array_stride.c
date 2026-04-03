// TEST: 2d_struct_array_stride
// DESCRIPTION: 2D array of structs must use correct stride for first dimension (inner_dim * sizeof(struct))
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom declares: ticcmd_t netcmds[MAXPLAYERS][BACKUPTICS]  (4 x 12, 8 bytes each)
   When indexing netcmds[i][j], the first dimension stride should be
   BACKUPTICS * sizeof(ticcmd_t) = 12 * 8 = 96 bytes.

   Bug: the codegen uses sizeof(ticcmd_t) = 8 as the stride for BOTH
   dimensions, so netcmds[1][0] accesses offset 8 instead of offset 96.
   This causes G_BuildTiccmd to read/write the wrong ticcmd slot,
   corrupting adjacent data and causing the game loop crash. */

int printf(const char *fmt, ...);

struct cmd {
    char a;
    char b;
    short c;
    short d;
    char e;
    char f;
};  /* 8 bytes */

struct cmd cmds[4][12];

int main(void) {
    /* Initialize all to zero */
    int i, j;
    for (i = 0; i < 4; i++)
        for (j = 0; j < 12; j++) {
            cmds[i][j].a = 0;
            cmds[i][j].b = 0;
            cmds[i][j].c = 0;
        }

    /* Write to cmds[0][0] */
    cmds[0][0].a = 1;
    cmds[0][0].c = 100;

    /* Write to cmds[1][0] — should be at byte offset 96, not 8 */
    cmds[1][0].a = 2;
    cmds[1][0].c = 200;

    /* Write to cmds[0][1] — should be at byte offset 8 */
    cmds[0][1].a = 3;
    cmds[0][1].c = 300;

    /* Verify cmds[0][0] is not corrupted by cmds[1][0] write */
    if (cmds[0][0].a != 1) return 1;
    if (cmds[0][0].c != 100) return 2;

    /* Verify cmds[1][0] has correct values */
    if (cmds[1][0].a != 2) return 3;
    if (cmds[1][0].c != 200) return 4;

    /* Verify cmds[0][1] has correct values and didn't overwrite cmds[1][0] */
    if (cmds[0][1].a != 3) return 5;
    if (cmds[0][1].c != 300) return 6;

    /* Cross-check: cmds[1][0] should still be intact after cmds[0][1] write */
    if (cmds[1][0].a != 2) return 7;

    /* Test higher indices */
    cmds[3][11].a = 99;
    cmds[3][11].c = 999;
    if (cmds[3][11].a != 99) return 8;
    if (cmds[3][11].c != 999) return 9;

    /* Verify cmds[3][10] was not corrupted */
    if (cmds[3][10].a != 0) return 10;

    printf("ok\n");
    return 0;
}
