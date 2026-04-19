// TEST: const_func_ptr_member
// DESCRIPTION: struct member with const function pointer type: type (*const name)(args) must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef long ssize_t;

typedef struct {
    long (*const hash)(const void *data, ssize_t len);
    const char *name;
    const int bits;
} HashDef;

static long my_hash(const void *data, ssize_t len) {
    (void)data; return len * 31;
}

static const HashDef def = { my_hash, "fnv", 64 };

int main(void) {
    long h = def.hash("hello", 5);
    if (h != 155) return 1;
    if (def.bits != 64) return 2;
    printf("OK\n");
    return 0;
}
