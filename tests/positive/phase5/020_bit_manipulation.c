// TEST: bit_manipulation
// DESCRIPTION: Doom flag patterns: |=, &= ~, & test
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: flags=3
// STDOUT: has_solid=1
// STDOUT: after_clear=1
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

#define MF_SOLID     0x01
#define MF_SHOOTABLE 0x02
#define MF_SPECIAL   0x04
#define MF_NOSECTOR  0x08

int main(void) {
    int flags = 0;

    /* Set flags */
    flags |= MF_SOLID | MF_SHOOTABLE;
    printf("flags=%d\n", flags);  /* 3 */

    /* Test flag */
    printf("has_solid=%d\n", (flags & MF_SOLID) != 0);  /* 1 */

    /* Clear flag */
    flags &= ~MF_SHOOTABLE;
    printf("after_clear=%d\n", flags);  /* 1 (only SOLID remains) */

    return 0;
}
