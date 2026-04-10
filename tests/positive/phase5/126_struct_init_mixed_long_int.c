// TEST: struct_init_mixed_long_int
// DESCRIPTION: Struct initializer with mixed long and int fields must emit correct sizes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's state_t has:
     { spritenum_t(int), long, long, actionf_t(ptr), statenum_t(int), long, long }
   Initialized with: {SPR_TROO, 0, -1, {NULL}, S_NULL, 0, 0}
   Each long field must emit 8 bytes, not 4. If longs are emitted as
   4-byte .long instead of 8-byte .quad, the struct layout is wrong
   and subsequent fields shift, corrupting the entire states[] array. */

int printf(const char *fmt, ...);

typedef void (*funcptr_t)(void);

struct state {
    int sprite;
    long frame;
    long tics;
    funcptr_t action;
    int nextstate;
    long misc1;
    long misc2;
};

void dummy_action(void) {}

struct state states[3] = {
    {0, 0, -1, 0, 0, 0, 0},         /* NULL state */
    {1, 4, 0, dummy_action, 0, 0, 0}, /* with function pointer */
    {2, 1, 10, 0, 3, 100, 200},       /* with misc values */
};

int main(void) {
    /* Check sizeof */
    if (sizeof(struct state) != 56) return 1;

    /* Check first state */
    if (states[0].sprite != 0) return 2;
    if (states[0].tics != -1) return 3;
    if (states[0].action != 0) return 4;

    /* Check second state */
    if (states[1].sprite != 1) return 5;
    if (states[1].frame != 4) return 6;
    if (states[1].action != dummy_action) return 7;

    /* Check third state */
    if (states[2].sprite != 2) return 8;
    if (states[2].tics != 10) return 9;
    if (states[2].nextstate != 3) return 10;
    if (states[2].misc1 != 100) return 11;
    if (states[2].misc2 != 200) return 12;

    /* Array stride */
    long stride = (char *)&states[1] - (char *)&states[0];
    if (stride != 56) return 13;

    printf("ok\n");
    return 0;
}
