// TEST: enum_const_expr
// DESCRIPTION: Enum values using constant expressions (Doom's powerduration_t pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1050
// STDOUT: 2100
// STDOUT: 4200
// STDOUT: 17
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef enum {
    INVULNTICS = (30 * 35),
    INVISTICS  = (60 * 35),
    INFRATICS  = (120 * 35)
} powerduration_t;

typedef enum {
    A = 1 + 2,
    B = A + 4,
    C = 3 << 2,
    D = (1 | 16)
} expr_enum_t;

int main(void) {
    printf("%d\n", INVULNTICS);
    printf("%d\n", INVISTICS);
    printf("%d\n", INFRATICS);
    printf("%d\n", D);
    return 0;
}
