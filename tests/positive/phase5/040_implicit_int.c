// TEST: implicit_int
// DESCRIPTION: Implicit int declaration (C89 K&R style, no type specifier)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: x=5
// STDOUT: x=10
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

void update(void) {
    /* Doom's am_map.c: 'static nexttic = 0;' with no type specifier.
       In C89, the type defaults to int when omitted. */
    static nexttic = 0;
    nexttic += 5;
    printf("x=%d\n", nexttic);
}

int main(void) {
    update();
    update();
    return 0;
}
