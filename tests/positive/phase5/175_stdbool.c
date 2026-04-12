// TEST: stdbool
// DESCRIPTION: stdbool.h with bool/true/false must work correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom includes <stdbool.h> in doomtype.h but defines
   its own boolean type. The header must be includable and the
   bool/true/false identifiers must work. C99 stdbool.h defines:
     #define bool _Bool
     #define true 1
     #define false 0 */

#include <stdbool.h>
#include <stdio.h>

/* Function returning bool */
bool is_positive(int x) {
    return x > 0;
}

/* Function taking bool parameter */
int select_val(bool cond, int a, int b) {
    if (cond)
        return a;
    return b;
}

/* Bool in struct */
typedef struct {
    int value;
    bool active;
    bool visible;
} item_t;

int printf(const char *fmt, ...);

int main(void) {
    /* Test 1: basic true/false */
    bool a = true;
    bool b = false;
    if (a != 1) return 1;
    if (b != 0) return 2;

    /* Test 2: bool from comparison */
    bool c = (5 > 3);
    bool d = (2 > 7);
    if (c != true) return 3;
    if (d != false) return 4;

    /* Test 3: bool in conditions */
    if (!a) return 5;
    if (b) return 6;

    /* Test 4: function returning bool */
    if (!is_positive(42)) return 7;
    if (is_positive(-1)) return 8;
    if (is_positive(0)) return 9;

    /* Test 5: bool as function parameter */
    if (select_val(true, 10, 20) != 10) return 10;
    if (select_val(false, 10, 20) != 20) return 11;

    /* Test 6: bool assignment from expression */
    bool e = is_positive(100) && !is_positive(-5);
    if (!e) return 12;

    /* Test 7: sizeof(bool) — must be 1 on most platforms */
    if (sizeof(bool) != 1) return 13;

    /* Test 8: bool in struct */
    item_t item;
    item.value = 42;
    item.active = true;
    item.visible = false;
    if (!item.active) return 14;
    if (item.visible) return 15;
    if (item.value != 42) return 16;

    /* Test 9: bool array */
    bool flags[4] = {true, false, true, false};
    int count = 0;
    int i;
    for (i = 0; i < 4; i++)
        if (flags[i]) count++;
    if (count != 2) return 17;

    /* Test 10: bool arithmetic (bool promotes to int) */
    bool x = true;
    bool y = true;
    int sum = x + y;
    if (sum != 2) return 18;

    /* Test 11: assigning non-zero int to bool truncates to 1 */
    bool z = 42;
    if (z != 1) return 19;

    printf("ok\n");
    return 0;
}
