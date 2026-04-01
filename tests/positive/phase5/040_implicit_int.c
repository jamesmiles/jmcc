// TEST: implicit_int
// DESCRIPTION: Implicit int with all storage classes (C89 K&R style, no type specifier)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: x=5
// STDOUT: x=10
// STDOUT: a=1
// STDOUT: b=2
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

void update(void) {
    /* Doom's am_map.c: 'static nexttic = 0;' with no type specifier. */
    static nexttic = 0;
    nexttic += 5;
    printf("x=%d\n", nexttic);
}

int main(void) {
    update();
    update();

    /* Doom's am_map.c: 'register outcode1 = 0;' with no type specifier. */
    register a = 1;
    register b = 0;
    b = 2;
    printf("a=%d\n", a);
    printf("b=%d\n", b);
    return 0;
}
