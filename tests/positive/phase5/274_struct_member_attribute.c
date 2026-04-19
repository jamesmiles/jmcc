/* __attribute__ on struct members must be accepted (and ignored).
   GCC's stddef.h defines max_align_t using this pattern — blocking
   any file that includes <stddef.h> or <stdlib.h> when jmcc is used. */
#include <stdio.h>

typedef struct {
    long long   x __attribute__((__aligned__(__alignof__(long long))));
    long double y __attribute__((__aligned__(__alignof__(long double))));
} my_max_align_t;

struct S {
    int a __attribute__((unused));
    char b __attribute__((aligned(4)));
};

int main(void) {
    my_max_align_t m;
    m.x = 42;
    m.y = 3.14;
    struct S s;
    s.a = 1;
    s.b = 2;
    if (m.x != 42 || s.a != 1 || s.b != 2) return 1;
    printf("OK\n");
    return 0;
}
