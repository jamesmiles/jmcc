// TEST: struct_array_union_init
// DESCRIPTION: Array of structs containing union with function pointer must initialize correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's states[] array contains state_t structs with an actionf_t
   union member (a union of function pointers). The initializer uses
   nested braces: {SPR_TROO, 0, -1, {NULL}, S_NULL, 0, 0}
   where {NULL} initializes the union. */

int printf(const char *fmt, ...);

typedef void (*actionf_v)(void);
typedef void (*actionf_p1)(void *);

typedef union {
    actionf_p1 acp1;
    actionf_v acv;
} actionf_t;

typedef struct {
    int sprite;
    long frame;
    long tics;
    actionf_t action;
    int nextstate;
    long misc1;
    long misc2;
} state_t;

void A_Look(void *actor) {}
void A_Chase(void *actor) {}

state_t states[] = {
    {0, 0, -1, {(actionf_p1)0}, 0, 0, 0},
    {1, 4,  0, {(actionf_p1)A_Look}, 2, 0, 0},
    {2, 0,  8, {(actionf_p1)A_Chase}, 0, 5, 10},
};

int main(void) {
    /* Check sizeof */
    if (sizeof(state_t) != 56) return 1;

    /* State 0: NULL action */
    if (states[0].sprite != 0) return 2;
    if (states[0].tics != -1) return 3;
    if (states[0].action.acp1 != 0) return 4;
    if (states[0].nextstate != 0) return 5;

    /* State 1: A_Look action */
    if (states[1].sprite != 1) return 6;
    if (states[1].frame != 4) return 7;
    if (states[1].action.acp1 != (actionf_p1)A_Look) return 8;
    if (states[1].nextstate != 2) return 9;

    /* State 2: misc values */
    if (states[2].tics != 8) return 10;
    if (states[2].action.acp1 != (actionf_p1)A_Chase) return 11;
    if (states[2].misc1 != 5) return 12;
    if (states[2].misc2 != 10) return 13;

    /* Array stride */
    long stride = (char *)&states[1] - (char *)&states[0];
    if (stride != 56) return 14;

    printf("ok\n");
    return 0;
}
