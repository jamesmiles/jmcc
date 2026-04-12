// TEST: static_assert
// DESCRIPTION: _Static_assert declarations must be parsed and accepted
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C11 _Static_assert appears in glibc and SDL headers for
   compile-time size/alignment checks. jmcc needs to parse
   and skip these. Appears 10 times in SDL preprocessed output. */

int printf(const char *fmt, ...);

_Static_assert(sizeof(int) == 4, "int must be 4 bytes");
_Static_assert(sizeof(void *) == 8, "pointers must be 8 bytes");

typedef struct {
    int x;
    int y;
} point_t;

_Static_assert(sizeof(point_t) == 8, "point_t must be 8 bytes");

int main(void) {
    printf("ok\n");
    return 0;
}
