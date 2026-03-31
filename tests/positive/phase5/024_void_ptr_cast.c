// TEST: void_ptr_cast
// DESCRIPTION: Pass struct as void*, cast back and access members (Doom universal pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: x=10 y=20
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef struct {
    int x;
    int y;
    int type;
} mobj_t;

void process(void *ptr) {
    mobj_t *mo = (mobj_t *)ptr;
    printf("x=%d y=%d\n", mo->x, mo->y);
}

int main(void) {
    mobj_t mo;
    mo.x = 10;
    mo.y = 20;
    mo.type = 1;
    process(&mo);
    return 0;
}
