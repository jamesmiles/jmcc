// TEST: values_h_minint
// DESCRIPTION: Doom's m_bbox.h uses MININT from <values.h>; JMCC needs system header support
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: min=-2147483648
// STDOUT: max=2147483647
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom includes <values.h> for these. Test that the pattern works
   whether via system header or local define. */
#ifndef MININT
#define MININT ((int)0x80000000)
#endif
#ifndef MAXINT
#define MAXINT ((int)0x7FFFFFFF)
#endif

int main(void) {
    int a = MININT;
    int b = MAXINT;
    printf("min=%d\n", a);
    printf("max=%d\n", b);
    return 0;
}
