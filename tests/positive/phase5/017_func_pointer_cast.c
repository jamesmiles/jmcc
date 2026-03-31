// TEST: func_pointer_cast
// DESCRIPTION: Cast between function pointer types (Doom action function pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: action called with mobj
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef struct {
    int x;
    int y;
    int type;
} mobj_t;

void action(void *mobj) {
    mobj_t *mo = (mobj_t *)mobj;
    if (mo->type == 42) {
        printf("action called with mobj\n");
    }
}

int main(void) {
    mobj_t mo;
    mo.x = 10;
    mo.y = 20;
    mo.type = 42;

    /* Doom casts action functions between types */
    void (*generic)(void) = (void (*)(void))action;
    void (*typed)(void *) = (void (*)(void *))generic;
    typed(&mo);
    return 0;
}
