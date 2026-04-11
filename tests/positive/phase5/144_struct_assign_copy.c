// TEST: struct_assign_copy
// DESCRIPTION: Struct assignment must copy ALL fields, not just the first
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's event queue does: events[eventhead] = *ev;
   where event_t has 4 int fields. Only the first field (type) gets
   copied; data1, data2, data3 remain zero. This means all keyboard
   events lose their key data, making input non-functional. */

int printf(const char *fmt, ...);

typedef struct {
    int type;
    int data1;
    int data2;
    int data3;
} event_t;

event_t events[8];

int main(void) {
    event_t e;
    e.type = 1;
    e.data1 = 42;
    e.data2 = 100;
    e.data3 = 200;

    /* Struct assignment through array index */
    events[0] = e;

    if (events[0].type != 1) return 1;
    if (events[0].data1 != 42) return 2;
    if (events[0].data2 != 100) return 3;
    if (events[0].data3 != 200) return 4;

    /* Through pointer dereference */
    event_t *p = &e;
    events[1] = *p;

    if (events[1].type != 1) return 5;
    if (events[1].data1 != 42) return 6;
    if (events[1].data2 != 100) return 7;
    if (events[1].data3 != 200) return 8;

    /* Struct-to-struct copy */
    event_t copy;
    copy = e;
    if (copy.data1 != 42) return 9;
    if (copy.data3 != 200) return 10;

    printf("ok\n");
    return 0;
}
