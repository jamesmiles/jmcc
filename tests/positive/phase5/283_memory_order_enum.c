// TEST: memory_order_enum
// DESCRIPTION: memory_order enum values from stdatomic.h must be defined (memory_order_relaxed etc.)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdatomic.h>

int main(void) {
    _Atomic int x = 0;
    atomic_store_explicit(&x, 42, memory_order_relaxed);
    int v = atomic_load_explicit(&x, memory_order_acquire);
    if (v != 42) return 1;
    printf("OK\n");
    return 0;
}
