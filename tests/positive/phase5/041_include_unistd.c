// TEST: include_unistd
// DESCRIPTION: #include <unistd.h> for R_OK/access() (Doom's d_main.c pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: R_OK=4
// STDOUT: X_OK=1
// ENVIRONMENT: hosted
// PHASE: 5

#include <unistd.h>

int printf(const char *fmt, ...);

int main(void) {
    printf("R_OK=%d\n", R_OK);
    printf("X_OK=%d\n", X_OK);
    return 0;
}
