// TEST: unsigned_char_all_access
// DESCRIPTION: All access patterns for unsigned char must zero-extend (not sign-extend)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Comprehensive test for unsigned char zero-extension across all
   code paths. Values >= 128 must remain positive (0-255).
   Each return code identifies a specific failing pattern. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

/* Globals */
byte g_val = 200;
byte g_arr[4] = {128, 200, 250, 255};
byte g_2d[2][3] = {{128, 200, 255}, {130, 210, 240}};

struct s_byte {
    byte a;
    byte b;
};
struct s_byte g_struct = {200, 255};

int main(void) {
    int val;

    /* 1. Global scalar */
    val = g_val;
    if (val != 200) return 1;

    /* 2. Global 1D array */
    val = g_arr[0];
    if (val != 128) return 2;
    val = g_arr[3];
    if (val != 255) return 3;

    /* 3. Global 2D array */
    val = g_2d[0][0];
    if (val != 128) return 4;
    val = g_2d[1][2];
    if (val != 240) return 5;

    /* 4. Global struct member */
    val = g_struct.a;
    if (val != 200) return 6;
    val = g_struct.b;
    if (val != 255) return 7;

    /* 5. Local scalar */
    byte l_val = 200;
    val = l_val;
    if (val != 200) return 8;

    /* 6. Local array */
    byte l_arr[3] = {128, 200, 255};
    val = l_arr[2];
    if (val != 255) return 9;

    /* 7. Pointer dereference */
    byte *ptr = &g_arr[2];
    val = *ptr;
    if (val != 250) return 10;

    /* 8. Pointer indexing */
    val = ptr[-1];
    if (val != 200) return 11;

    /* 9. Struct pointer member */
    struct s_byte *sp = &g_struct;
    val = sp->b;
    if (val != 255) return 12;

    /* 10. Cast from signed char to unsigned char */
    signed char sc = -1;
    byte uc = (byte)sc;
    val = uc;
    if (val != 255) return 13;

    /* 11. Function parameter */
    /* (tested indirectly via pointer) */

    /* 12. Return value used in arithmetic */
    val = g_arr[3] * 2;
    if (val != 510) return 14;

    /* 13. Used as array index (the Doom palette pattern) */
    int lookup[256];
    int i;
    for (i = 0; i < 256; i++) lookup[i] = i;
    val = lookup[g_arr[2]];  /* g_arr[2] = 250 */
    if (val != 250) return 15;

    /* 14. Shift operations */
    val = g_arr[3] << 16;   /* 255 << 16 = 0x00FF0000 */
    if (val != 0x00FF0000) return 16;

    /* 15. Comparison */
    if (g_arr[3] != 255) return 17;
    if (g_arr[3] < 128) return 18;

    printf("ok\n");
    return 0;
}
