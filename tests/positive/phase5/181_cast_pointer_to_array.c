// TEST: cast_pointer_to_array
// DESCRIPTION: Cast expression with pointer-to-array type must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's i_oplmusic.c casts a pointer to pointer-to-array:
     main_instr_names = (char (*)[32]) (percussion_instrs + 47);
   Test 178 fixed the declaration syntax char (*name)[32], but the
   same type used in a CAST expression still fails to parse. */

int printf(const char *fmt, ...);
int strcmp(const char *a, const char *b);

int main(void) {
    /* Array of fixed-size strings laid out contiguously */
    char data[3][8] = {"hello", "world", "test"};

    /* Cast raw pointer to pointer-to-array-of-8-chars */
    char (*p)[8] = (char (*)[8]) data;
    if (strcmp(p[0], "hello") != 0) return 1;
    if (strcmp(p[1], "world") != 0) return 2;
    if (strcmp(p[2], "test") != 0) return 3;

    /* Cast from void pointer */
    void *raw = data;
    char (*q)[8] = (char (*)[8]) raw;
    if (strcmp(q[1], "world") != 0) return 4;

    /* Cast with offset arithmetic (Doom's exact pattern) */
    char (*r)[8] = (char (*)[8]) ((char *)data + 8);
    if (strcmp(r[0], "world") != 0) return 5;

    printf("ok\n");
    return 0;
}
