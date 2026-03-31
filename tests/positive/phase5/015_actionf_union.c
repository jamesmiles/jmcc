// TEST: actionf_union
// DESCRIPTION: Doom's actionf_t union - store function via one member, call via another
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: action called
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef union {
    void (*acv)(void);
    void (*acp1)(void *);
} actionf_t;

void my_action(void) {
    printf("action called\n");
}

int main(void) {
    actionf_t action;
    action.acv = my_action;
    action.acv();
    return 0;
}
