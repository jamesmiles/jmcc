// TEST: atomic_builtins
// DESCRIPTION: __ATOMIC_* constants, _Atomic qualifier, and __atomic_store/load_n builtins must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
/* GCC predefined atomic constants (__ATOMIC_RELAXED etc.) must be defined,
   and _Atomic type qualifier must work in typedefs. Without these, stdatomic.h
   fails to compile, blocking Redis and other projects that use C11 atomics. */
#include <stdio.h>

/* Simulate what stdatomic.h does */
typedef enum {
    my_order_relaxed = __ATOMIC_RELAXED,
    my_order_consume = __ATOMIC_CONSUME,
    my_order_acquire = __ATOMIC_ACQUIRE,
    my_order_release = __ATOMIC_RELEASE,
    my_order_acq_rel = __ATOMIC_ACQ_REL,
    my_order_seq_cst = __ATOMIC_SEQ_CST
} my_memory_order;

typedef _Atomic int atomic_int;
typedef _Atomic unsigned int atomic_uint;
typedef _Atomic long atomic_long;

static atomic_int counter;

int main(void) {
    /* __ATOMIC_RELAXED must be 0 per GCC spec */
    if (my_order_relaxed != 0) return 1;
    /* __ATOMIC_SEQ_CST must be 5 per GCC spec */
    if (my_order_seq_cst != 5) return 2;

    __atomic_store_n(&counter, 42, __ATOMIC_RELAXED);
    int v = __atomic_load_n(&counter, __ATOMIC_RELAXED);
    if (v != 42) return 3;

    printf("OK\n");
    return 0;
}
