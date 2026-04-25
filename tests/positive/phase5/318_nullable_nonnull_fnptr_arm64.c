// TEST: nullable_nonnull_fnptr
// DESCRIPTION: Darwin system headers (stdlib.h, stdio.h) use _Nullable and _Nonnull
//              qualifiers inside function pointer parameters, e.g.
//              int atexit(void (* _Nonnull)(void));
//              jmcc must accept these qualifiers as no-op type annotations.
//              Regression test for Chocolate Doom / stdlib.h include chain on arm64.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef int (* _Nullable nullable_cmp)(const void *, const void *);
typedef int (* _Nonnull  nonnull_cmp)(const void *, const void *);

int call_nullable(nullable_cmp fn, const void *a, const void *b) {
    if (fn) return fn(a, b);
    return 0;
}

int main(void) {
    printf("OK\n");
    return 0;
}
