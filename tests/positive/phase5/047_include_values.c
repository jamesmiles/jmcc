// TEST: include_values
// DESCRIPTION: #include <values.h> for MININT/MAXINT (Doom's m_bbox.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include <values.h>

int printf(const char *fmt, ...);

int main(void) {
    int x = MININT;
    int y = MAXINT;
    printf("ok\n");
    return 0;
}
