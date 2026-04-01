// TEST: multifile_struct
// DESCRIPTION: Shared struct definition across translation units via header
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: x=10 y=20
// ENVIRONMENT: hosted
// PHASE: 5
// MULTI_FILE: helpers/010_helper.c
// NOTE: Requires multi-file compilation support. Will not pass until harness is updated.

#include "helpers/010_shared.h"

int printf(const char *fmt, ...);

void fill_point(point_t *p, int x, int y);

int main(void) {
    point_t p;
    fill_point(&p, 10, 20);
    printf("x=%d y=%d\n", p.x, p.y);
    return 0;
}
