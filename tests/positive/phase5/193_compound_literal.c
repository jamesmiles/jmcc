// TEST: compound_literal
// DESCRIPTION: C99 compound literals (type){...} must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C99 compound literals create unnamed objects:
     point_t p = (point_t){.x = 1, .y = 2};
     func((point_t){10, 20});
   Used in modern C code and Linux kernel headers. */

int printf(const char *fmt, ...);

typedef struct {
    int x;
    int y;
} point_t;

int sum_point(point_t p) {
    return p.x + p.y;
}

void set_point(point_t *p, point_t value) {
    *p = value;
}

int main(void) {
    /* Test 1: compound literal as initializer */
    point_t p1 = (point_t){10, 20};
    if (p1.x != 10) return 1;
    if (p1.y != 20) return 2;

    /* Test 2: compound literal as function arg */
    if (sum_point((point_t){3, 4}) != 7) return 3;

    /* Test 3: compound literal in assignment */
    point_t p2;
    p2 = (point_t){100, 200};
    if (p2.x != 100) return 4;
    if (p2.y != 200) return 5;

    /* Test 4: compound literal passed by reference */
    point_t p3;
    set_point(&p3, (point_t){5, 6});
    if (p3.x != 5) return 6;

    /* Test 5: array compound literal */
    int *arr = (int[]){10, 20, 30};
    if (arr[0] != 10) return 7;
    if (arr[2] != 30) return 8;

    /* Test 6: compound literal in expression */
    int total = sum_point((point_t){1, 2}) + sum_point((point_t){3, 4});
    if (total != 10) return 9;

    printf("ok\n");
    return 0;
}
