// TEST: bitfield_compound_arm64
// DESCRIPTION: Compound assignments and comparisons on signed bitfields
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -1 8
// -5 6
// 5
// neg
// gt
// ENVIRONMENT: hosted
// PHASE: 5

#include <stdio.h>

struct S { signed int sx : 4; unsigned int ux : 4; };

int main(void) {
    struct S f;
    f.sx = -3; f.ux = 5;
    f.sx += 2; f.ux += 3;
    printf("%d %u\n", f.sx, f.ux);
    f.sx -= 4; f.ux -= 2;
    printf("%d %u\n", f.sx, f.ux);
    f.sx *= -1;
    printf("%d\n", f.sx);
    f.sx = -3;
    if (f.sx < 0) printf("neg\n");
    if (f.sx > -10) printf("gt\n");
    return 0;
}
