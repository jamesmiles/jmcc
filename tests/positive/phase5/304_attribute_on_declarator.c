// TEST: attribute_on_declarator
// DESCRIPTION: __attribute__ applied to individual declarators in a multi-variable declaration list must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

typedef struct { int type; int version; } Event;

static const Event
    Event_First = {0, 1},
    __attribute__((deprecated))
    Event_Legacy = {12, 1},
    Event_Last = {14, 1};

int main(void) {
    if (Event_First.type != 0) return 1;
    if (Event_Legacy.type != 12) return 2;
    if (Event_Last.type != 14) return 3;
    printf("OK\n");
    return 0;
}
