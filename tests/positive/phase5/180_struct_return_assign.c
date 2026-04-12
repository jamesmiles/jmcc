// TEST: struct_return_assign
// DESCRIPTION: Assigning struct returned by function must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's i_joystick.c does:
     SDL_JoystickGUID dev_guid;
     dev_guid = SDL_JoystickGetDeviceGUID(i);
   This assigns a struct returned by value from a function call.
   jmcc reports "expression is not an lvalue" for the struct variable. */

int printf(const char *fmt, ...);
int memcmp(const void *a, const void *b, long n);

typedef struct {
    unsigned char data[16];
} guid_t;

guid_t make_guid(int seed) {
    guid_t g;
    int i;
    for (i = 0; i < 16; i++)
        g.data[i] = seed + i;
    return g;
}

typedef struct {
    int x;
    int y;
} point_t;

point_t make_point(int x, int y) {
    point_t p;
    p.x = x;
    p.y = y;
    return p;
}

int main(void) {
    /* Test 1: assign struct from function return */
    guid_t g;
    g = make_guid(10);
    if (g.data[0] != 10) return 1;
    if (g.data[15] != 25) return 2;

    /* Test 2: smaller struct */
    point_t p;
    p = make_point(42, 99);
    if (p.x != 42) return 3;
    if (p.y != 99) return 4;

    /* Test 3: compare two struct returns */
    guid_t g2;
    g2 = make_guid(10);
    if (memcmp(&g, &g2, sizeof(guid_t)) != 0) return 5;

    /* Test 4: assign in a loop */
    int i;
    for (i = 0; i < 3; i++) {
        point_t tmp;
        tmp = make_point(i, i * 10);
        if (tmp.x != i) return 6;
        if (tmp.y != i * 10) return 7;
    }

    /* Test 5: pass returned struct to memcmp */
    guid_t g3 = make_guid(20);
    g = make_guid(20);
    if (memcmp(&g, &g3, sizeof(guid_t)) != 0) return 8;

    printf("ok\n");
    return 0;
}
