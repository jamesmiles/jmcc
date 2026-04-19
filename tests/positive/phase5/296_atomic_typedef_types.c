// TEST: atomic_typedef_types
// DESCRIPTION: atomic_int, atomic_uint, atomic_uintptr_t etc. typedefs must be defined in stdatomic.h
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdatomic.h>
#include <stdint.h>

typedef struct { atomic_uintptr_t ptr; } AtomicPtr;
typedef struct { atomic_int count; } AtomicCounter;
typedef struct { atomic_uint flags; } AtomicFlags;

int main(void) {
    AtomicCounter c;
    atomic_store(&c.count, 42);
    if (atomic_load(&c.count) != 42) return 1;
    AtomicFlags f;
    atomic_store(&f.flags, 7u);
    if (atomic_load(&f.flags) != 7u) return 2;
    printf("OK\n");
    return 0;
}
