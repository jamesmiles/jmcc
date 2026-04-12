// TEST: atomic_qualifier
// DESCRIPTION: _Atomic type qualifier must be accepted
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C11 _Atomic qualifier appears in glibc headers (stdatomic.h,
   included transitively by SDL). jmcc doesn't need to implement
   atomic semantics, just accept the qualifier without choking.
   Appears 10 times in SDL preprocessed output. */

int printf(const char *fmt, ...);

_Atomic int counter = 0;

int main(void) {
    counter = 42;
    if (counter != 42) return 1;

    _Atomic int local = 10;
    local = local + 5;
    if (local != 15) return 2;

    printf("ok\n");
    return 0;
}
