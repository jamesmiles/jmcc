// TEST: nullable_in_struct_fields
// DESCRIPTION: Darwin stdio.h uses _Nullable on function pointer fields inside
//              struct __sFILE (the FILE internals), e.g.:
//                int (* _Nullable _close)(void *);
//              jmcc must accept _Nullable/_Nonnull qualifiers inside struct
//              field declarations, not just in standalone typedefs.
//              Regression test for Chocolate Doom / stdio.h struct FILE on arm64.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef long long fpos_t_sim;

struct file_ops {
    void *_cookie;
    int (* _Nullable _close)(void *);
    int (* _Nullable _read)(void *, char *, int n);
    fpos_t_sim (* _Nullable _seek)(void *, fpos_t_sim, int);
    int (* _Nullable _write)(void *, const char *, int n);
};

int main(void) {
    printf("OK\n");
    return 0;
}
