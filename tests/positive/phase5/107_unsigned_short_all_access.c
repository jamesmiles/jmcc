// TEST: unsigned_short_all_access
// DESCRIPTION: All access patterns for unsigned short must zero-extend (not sign-extend)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Same as test 106 but for unsigned short. Values >= 32768 must
   remain positive (0-65535). */

int printf(const char *fmt, ...);

/* Globals */
unsigned short g_val = 40000;
unsigned short g_arr[4] = {32768, 40000, 60000, 65535};
unsigned short g_2d[2][3] = {{32768, 40000, 65535}, {33000, 50000, 60000}};

struct s_short {
    unsigned short a;
    unsigned short b;
};
struct s_short g_struct = {40000, 65535};

int main(void) {
    int val;

    /* 1. Global scalar */
    val = g_val;
    if (val != 40000) return 1;

    /* 2. Global 1D array */
    val = g_arr[0];
    if (val != 32768) return 2;
    val = g_arr[3];
    if (val != 65535) return 3;

    /* 3. Global 2D array */
    val = g_2d[0][0];
    if (val != 32768) return 4;
    val = g_2d[1][2];
    if (val != 60000) return 5;

    /* 4. Global struct member */
    val = g_struct.a;
    if (val != 40000) return 6;
    val = g_struct.b;
    if (val != 65535) return 7;

    /* 5. Local scalar */
    unsigned short l_val = 50000;
    val = l_val;
    if (val != 50000) return 8;

    /* 6. Pointer dereference */
    unsigned short *ptr = &g_arr[2];
    val = *ptr;
    if (val != 60000) return 9;

    /* 7. Pointer indexing */
    val = ptr[-1];
    if (val != 40000) return 10;

    /* 8. Struct pointer member */
    struct s_short *sp = &g_struct;
    val = sp->b;
    if (val != 65535) return 11;

    /* 9. Arithmetic */
    val = g_arr[3] + 1;
    if (val != 65536) return 12;

    /* 10. Comparison */
    if (g_arr[3] != 65535) return 13;
    if (g_arr[0] < 32768) return 14;

    printf("ok\n");
    return 0;
}
